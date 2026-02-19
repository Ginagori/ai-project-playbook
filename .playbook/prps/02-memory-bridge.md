# PRP: Memory Bridge

## Goal
Create a unified lesson retrieval layer that queries both Supabase (team knowledge) and local JSON (session knowledge), providing a single API for proactive lesson injection into artifact generation.

## Why
Today the Playbook has two disconnected lesson stores:
- `LessonsDatabase` (local JSON at `data/lessons.json`) — used by `suggest.py`
- `SupabaseClient.get_lessons()` — used only by `playbook_team_lessons` MCP tool

When the orchestrator generates artifacts, it calls neither. Lessons are captured (write path works) but never consulted (read path broken). This means:
- KOMPLIA learned that Decreto 1072/2015 is critical → that lesson exists in Supabase → next SST project doesn't get it
- NOVA learned that Triple-Layer Soul works → stored as a lesson → KidSpark doesn't benefit
- Known gotchas from 3 real projects are ignored when generating PRPs

## What
A `MemoryBridge` class that:
1. Queries both Supabase and local DB for lessons matching a project context
2. Deduplicates and ranks results by relevance
3. Returns lessons in a format ready to inject into artifact templates
4. Provides specialized queries: `get_gotchas()`, `get_patterns()`, `get_architecture_lessons()`
5. Is callable from phase nodes without async complexity (handles sync/async bridge)

## Success Criteria
- [ ] `MemoryBridge.get_relevant_lessons(project_type="saas", tech_stack=["nextjs", "supabase"])` returns lessons from both local and Supabase
- [ ] Lessons are deduplicated (same title from both sources → single result)
- [ ] Results are ranked by `relevance_score * confidence`
- [ ] `get_gotchas(project_type, tech_stack)` returns pitfall-category lessons formatted as warnings
- [ ] `get_architecture_lessons(project_type)` returns architecture-category lessons
- [ ] Works when Supabase is disabled (falls back to local-only)
- [ ] Works when local DB is empty (falls back to Supabase-only)

## Context

### Must-Read Files
- `agent/meta_learning/models.py` — `LessonsDatabase`, `LessonLearned`, `PatternMatch`
- `agent/meta_learning/suggest.py` — existing `get_recommendations()`, `find_similar_projects()`
- `agent/supabase_client.py:349-373` — `get_lessons()` method
- `mcp_server/playbook_mcp.py:58-63` — how Supabase is configured at startup

### Codebase Context
- The Supabase client is configured as a module-level singleton (`db`) in `playbook_mcp.py`
- The local DB is a module-level singleton via `get_lessons_db()` in `models.py`
- Phase nodes in `orchestrator.py` are synchronous functions (LangGraph nodes)
- The Supabase client methods are `async` but use the synchronous `supabase-py` client internally

### Known Gotchas
- `SupabaseClient` methods are marked `async` but the underlying `supabase-py` is sync — `asyncio.run()` from a sync context will fail if an event loop is running. Use `await` from async context or call the sync client directly.
- `LessonsDatabase.find_matches()` returns `PatternMatch` objects, while `SupabaseClient.get_lessons()` returns raw dicts — need to normalize.
- Supabase lessons have `upvotes`/`downvotes`/`frequency` fields; local lessons have `frequency`/`confidence` — map appropriately.

### Relevant Patterns
- Follow the singleton pattern from `get_lessons_db()` in `models.py`
- Use the `LessonLearned` model to normalize both sources

## Implementation Blueprint

### Files to Create
- `agent/memory_bridge.py` — the unified retrieval layer

### Files to Modify
- (none — additive; consumers modified in later PRPs)

### Tasks

#### Task 1: Create MemoryBridge class
**Files:** `agent/memory_bridge.py`
**Pseudocode:**
```python
"""
Memory Bridge — Unified lesson retrieval across Supabase and local storage.

Provides proactive lesson injection for artifact generation.
The orchestrator calls this to enrich CLAUDE.md, PRD, PRPs with real experience.
"""

from agent.meta_learning.models import (
    LessonLearned,
    PatternCategory,
    get_lessons_db,
)


class MemoryBridge:
    """
    Unified lesson retrieval from Supabase + local storage.

    Usage:
        bridge = MemoryBridge.get_instance()
        lessons = bridge.get_relevant_lessons("saas", ["nextjs", "supabase"])
        gotchas = bridge.get_gotchas("saas", ["nextjs", "supabase"])
    """

    _instance = None

    def __init__(self, supabase_client=None):
        self._supabase = supabase_client
        self._local_db = get_lessons_db()

    @classmethod
    def get_instance(cls, supabase_client=None) -> "MemoryBridge":
        if cls._instance is None:
            cls._instance = cls(supabase_client)
        return cls._instance

    @classmethod
    def configure(cls, supabase_client) -> None:
        """Configure with Supabase client (called at startup)."""
        instance = cls.get_instance()
        instance._supabase = supabase_client

    def get_relevant_lessons(
        self,
        project_type: str,
        tech_stack: list[str],
        phase: str | None = None,
        limit: int = 15,
    ) -> list[LessonLearned]:
        """
        Get lessons relevant to this project context from ALL sources.

        1. Query local DB
        2. Query Supabase (if configured)
        3. Deduplicate by title
        4. Rank by relevance * confidence
        """
        all_lessons: dict[str, LessonLearned] = {}

        # --- Local lessons ---
        local_lessons = self._local_db.get_lessons(
            project_type=project_type,
            min_confidence=0.4,
        )
        for lesson in local_lessons:
            score = lesson.matches_context(project_type, tech_stack)
            if score > 0.3:
                all_lessons[lesson.title.lower()] = lesson

        # --- Supabase lessons ---
        if self._supabase and self._supabase.is_configured:
            supabase_lessons = self._query_supabase_sync(
                project_type=project_type,
                tech_stack=tech_stack,
            )
            for lesson in supabase_lessons:
                key = lesson.title.lower()
                if key not in all_lessons:
                    all_lessons[key] = lesson
                else:
                    # Merge: keep higher confidence, sum frequencies
                    existing = all_lessons[key]
                    existing.confidence = max(existing.confidence, lesson.confidence)
                    existing.frequency += lesson.frequency

        # --- Filter by phase if specified ---
        if phase:
            phase_categories = {
                "discovery": [PatternCategory.WORKFLOW, PatternCategory.TECH_STACK],
                "planning": [PatternCategory.WORKFLOW, PatternCategory.ARCHITECTURE],
                "roadmap": [PatternCategory.WORKFLOW],
                "implementation": [
                    PatternCategory.ARCHITECTURE, PatternCategory.TESTING,
                    PatternCategory.TOOLING, PatternCategory.PITFALL,
                ],
                "deployment": [PatternCategory.DEPLOYMENT],
            }
            relevant_cats = phase_categories.get(phase, [])
            if relevant_cats:
                all_lessons = {
                    k: v for k, v in all_lessons.items()
                    if v.category in relevant_cats
                }

        # --- Rank and return ---
        ranked = sorted(
            all_lessons.values(),
            key=lambda l: l.matches_context(project_type, tech_stack) * l.confidence,
            reverse=True,
        )
        return ranked[:limit]

    def get_gotchas(
        self,
        project_type: str,
        tech_stack: list[str],
        limit: int = 5,
    ) -> list[str]:
        """Get known gotchas formatted as warning strings."""
        lessons = self.get_relevant_lessons(project_type, tech_stack)
        pitfalls = [l for l in lessons if l.category == PatternCategory.PITFALL]

        gotchas = []
        for p in pitfalls[:limit]:
            gotchas.append(f"- **{p.title}**: {p.description} → {p.recommendation}")
        return gotchas

    def get_architecture_lessons(
        self,
        project_type: str,
        limit: int = 5,
    ) -> list[LessonLearned]:
        """Get architecture-specific lessons."""
        lessons = self.get_relevant_lessons(project_type, [])
        return [l for l in lessons if l.category == PatternCategory.ARCHITECTURE][:limit]

    def get_patterns_for_feature(
        self,
        feature_name: str,
        project_type: str,
        tech_stack: list[str],
        limit: int = 3,
    ) -> list[LessonLearned]:
        """Get lessons relevant to a specific feature."""
        all_lessons = self.get_relevant_lessons(project_type, tech_stack)
        feature_lower = feature_name.lower()

        # Score by feature keyword match
        scored = []
        for lesson in all_lessons:
            title_lower = lesson.title.lower()
            desc_lower = lesson.description.lower()
            tag_str = " ".join(lesson.tags).lower()

            feature_score = 0.0
            for word in feature_lower.split():
                if len(word) < 3:
                    continue
                if word in title_lower:
                    feature_score += 2.0
                if word in desc_lower:
                    feature_score += 1.0
                if word in tag_str:
                    feature_score += 0.5

            if feature_score > 0:
                scored.append((lesson, feature_score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [lesson for lesson, _ in scored[:limit]]

    def format_lessons_for_injection(
        self,
        lessons: list[LessonLearned],
        format_type: str = "markdown",
    ) -> str:
        """Format lessons as markdown for injection into artifacts."""
        if not lessons:
            return ""

        if format_type == "gotchas":
            lines = ["### Known Gotchas (from past projects)", ""]
            for l in lessons:
                lines.append(f"- **{l.title}**: {l.recommendation}")
            return "\n".join(lines)

        if format_type == "patterns":
            lines = ["### Learned Patterns", ""]
            for l in lessons:
                conf = f"{l.confidence:.0%}"
                freq = f"seen {l.frequency}x" if l.frequency > 1 else "new"
                lines.append(f"- **{l.title}** ({conf}, {freq}): {l.recommendation}")
            return "\n".join(lines)

        # Default: full markdown
        lines = ["### Lessons from Past Projects", ""]
        for l in lessons:
            lines.append(f"**{l.title}** [{l.category.value}]")
            lines.append(f"  {l.description}")
            lines.append(f"  → {l.recommendation}")
            lines.append("")
        return "\n".join(lines)

    def _query_supabase_sync(
        self,
        project_type: str,
        tech_stack: list[str],
    ) -> list[LessonLearned]:
        """Query Supabase lessons synchronously."""
        if not self._supabase or not self._supabase.client:
            return []

        try:
            # Direct sync call (supabase-py is sync under the hood)
            query = self._supabase.client.table("lessons_learned").select("*")

            if self._supabase.team_id:
                query = query.eq("team_id", self._supabase.team_id)

            if project_type:
                query = query.contains("project_types", [project_type])

            result = query.order("confidence", desc=True).limit(50).execute()

            lessons = []
            for row in (result.data or []):
                lessons.append(LessonLearned(
                    category=PatternCategory(row.get("category", "workflow")),
                    title=row.get("title", ""),
                    description=row.get("description", ""),
                    context=row.get("context", ""),
                    recommendation=row.get("recommendation", ""),
                    confidence=row.get("confidence", 0.5),
                    frequency=row.get("frequency", 1),
                    project_types=row.get("project_types", []),
                    tech_stacks=row.get("tech_stacks", []),
                    tags=row.get("tags", []),
                ))
            return lessons
        except Exception as e:
            print(f"MemoryBridge: Supabase query failed: {e}")
            return []
```

### Integration Points
- **Called by:** `orchestrator.py` phase nodes (Planning, Roadmap, Implementation)
- **Called by:** `prp_builder.py` for per-feature gotchas
- **Depends on:** `agent/meta_learning/models.py` (LessonLearned, LessonsDatabase)
- **Depends on:** `agent/supabase_client.py` (SupabaseClient, optional)
- **Configured by:** `mcp_server/playbook_mcp.py` at startup

## Validation Loop

### Level 1: Syntax & Style
```bash
ruff check agent/memory_bridge.py --fix
ruff format agent/memory_bridge.py
```

### Level 2: Type Safety
```bash
mypy agent/memory_bridge.py --ignore-missing-imports
```

### Level 3: Unit Tests
```python
# .venv/Scripts/python.exe -c "..."
from agent.memory_bridge import MemoryBridge

# Test without Supabase (local-only mode)
bridge = MemoryBridge(supabase_client=None)

# Should return empty or local lessons (not crash)
lessons = bridge.get_relevant_lessons("saas", ["nextjs", "supabase"])
print(f"Local lessons: {len(lessons)}")

# Test gotchas format
gotchas = bridge.get_gotchas("saas", ["nextjs"])
print(f"Gotchas: {len(gotchas)}")

# Test format injection
formatted = bridge.format_lessons_for_injection(lessons, "patterns")
assert isinstance(formatted, str)
print(f"Formatted length: {len(formatted)}")

# Test feature-specific
feature_lessons = bridge.get_patterns_for_feature("authentication", "saas", ["nextjs"])
print(f"Auth lessons: {len(feature_lessons)}")

print("All memory bridge tests passed!")
```

### Level 4: Integration Tests
```bash
.venv/Scripts/python.exe -c "
from agent.memory_bridge import MemoryBridge
from agent.supabase_client import get_supabase_client

# Test with Supabase if configured
db = get_supabase_client()
bridge = MemoryBridge(supabase_client=db if db.is_configured else None)
lessons = bridge.get_relevant_lessons('saas', ['nextjs', 'supabase'])
print(f'Total lessons (both sources): {len(lessons)}')
for l in lessons[:3]:
    print(f'  - [{l.category.value}] {l.title} (conf={l.confidence:.0%})')
"
```

### Level 5: Build Verification
```bash
.venv/Scripts/python.exe -c "from agent.memory_bridge import MemoryBridge; print('Import OK')"
```

## Final Validation Checklist
- [ ] Works without Supabase (graceful fallback)
- [ ] Works without local lessons (graceful fallback)
- [ ] Deduplication by title works
- [ ] Phase filtering works
- [ ] Feature-specific queries return relevant results
- [ ] Format injection produces valid markdown
- [ ] No changes to existing files

## Anti-Patterns
- Do NOT call `asyncio.run()` from sync context — use the sync Supabase client directly
- Do NOT cache Supabase results forever — lessons change between sessions
- Do NOT filter too aggressively — better to return extra lessons than miss relevant ones
- Do NOT modify existing `suggest.py` or `models.py` — this is additive
