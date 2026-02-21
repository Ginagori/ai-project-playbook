# PRP: Semantic Search in MemoryBridge

## Goal
Upgrade MemoryBridge from keyword-only matching to hybrid semantic search, so Archie finds relevant lessons by meaning — not just exact string overlap.

## Why
After PRP-10 adds embeddings to lessons, the retrieval layer (MemoryBridge) still uses `overlaps()` and `contains()` — exact array matching. A lesson about "multi-tenant data isolation with RLS" won't be found when the context is "security patterns for SaaS." Semantic search closes this gap: it converts the query context into a vector and finds geometrically close lessons. Combined with the existing keyword filters (tech_stack, project_type), this creates a hybrid retrieval system that's both precise (keywords) and intelligent (semantics). This is the single highest-impact change for Archie's memory — it makes all 150+ existing lessons dramatically more discoverable.

## What
1. Update `MemoryBridge._query_supabase_sync()` to use the `match_lessons` RPC for semantic retrieval
2. Implement hybrid scoring: semantic similarity (50%) + keyword/metadata match (30%) + confidence/frequency (20%)
3. Update `get_patterns_for_feature()` to use semantic search instead of naive word matching
4. Add a new method `semantic_search()` for direct semantic queries from MCP tools
5. Graceful fallback: if embeddings unavailable, use current keyword matching

## Success Criteria
- [ ] Query "database security" returns lessons about RLS, multi-tenant, Supabase auth (even if those exact words aren't in the query)
- [ ] Query "frontend state management" returns lessons about React tabs, form persistence, controlled components
- [ ] `get_patterns_for_feature("Authentication")` returns auth-related lessons even without "auth" keyword in lesson titles
- [ ] Hybrid scoring ranks lessons better than pure keyword matching (validated with 3+ example queries)
- [ ] System falls back gracefully to keyword matching when embeddings are unavailable
- [ ] No performance regression: <500ms for a full retrieval cycle

## Context

### Must-Read Files
- `agent/memory_bridge.py` — THE file to modify. Contains `_query_supabase_sync()`, `get_relevant_lessons()`, `get_patterns_for_feature()`
- `agent/embedding.py` — (from PRP-10) embedding generation functions
- `agent/orchestrator.py` — calls MemoryBridge in `_generate_claude_md()` (line ~675), `_generate_prd()` (line ~820), `discovery_node()` (line ~298)
- `mcp_server/playbook_mcp.py` — could add a `playbook_search_lessons` tool for direct semantic search

### Codebase Context
- MemoryBridge is a singleton (`get_instance()`) initialized at MCP startup
- `_query_supabase_sync()` currently builds a PostgREST query with `.overlaps()` and `.contains()`
- The `match_lessons` RPC (from PRP-10) returns `similarity` score along with lesson fields
- `get_relevant_lessons()` merges local + Supabase results and deduplicates by title
- The orchestrator passes `project_type` and `tech_stack` to MemoryBridge — these should still be used as filters
- `get_patterns_for_feature()` currently does naive word-by-word matching on title/description/tags

### Known Gotchas
- The `match_lessons` RPC is called via `client.rpc()`, not `client.table()` — different API
- Supabase RPC returns raw dicts, not PostgREST response objects — handle differently
- Semantic search may return lessons from ANY category — still need phase filtering after retrieval
- The embedding model may not be loaded (first call, or CI environment) — always check for None
- Don't replace keyword matching entirely — some queries are exact (e.g., "nextjs" should find all Next.js lessons regardless of semantic similarity)
- Local lessons (not in Supabase) don't have embeddings — local retrieval stays keyword-based

### Relevant Patterns
- Current `_query_supabase_sync()` pattern for PostgREST queries
- Current `get_relevant_lessons()` merge and dedup pattern
- Singleton pattern in MemoryBridge

## Implementation Blueprint

### Data Models
No new models. Modify existing MemoryBridge methods.

### Tasks

#### Task 1: Add semantic query method to MemoryBridge
**Files:** `agent/memory_bridge.py`
**Pseudocode:**
```python
def _query_supabase_semantic(
    self,
    query_text: str,
    tech_stack: list[str] | None = None,
    limit: int = 15,
) -> list[tuple[LessonLearned, float]]:
    """Query Supabase using semantic similarity. Returns (lesson, similarity) pairs."""
    from agent.embedding import generate_query_embedding

    query_embedding = generate_query_embedding(query_text)
    if query_embedding is None:
        return []  # Model unavailable, caller should fallback

    result = self._supabase.client.rpc("match_lessons", {
        "query_embedding": query_embedding,
        "match_team_id": self._supabase.team_id,
        "match_threshold": 0.3,
        "match_count": limit,
    }).execute()

    lessons_with_scores = []
    for row in result.data or []:
        try:
            lesson = LessonLearned(
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
            )
            similarity = row.get("similarity", 0.0)

            # Post-filter by tech_stack if provided (semantic search is broad)
            if tech_stack:
                overlap = len(set(lesson.tech_stacks) & set(tech_stack))
                if overlap == 0 and lesson.tech_stacks:
                    similarity *= 0.5  # Penalize tech mismatch, don't discard

            lessons_with_scores.append((lesson, similarity))
        except Exception:
            continue

    return lessons_with_scores
```

#### Task 2: Upgrade get_relevant_lessons() with hybrid retrieval
**Files:** `agent/memory_bridge.py`
**Depends on:** Task 1
**Pseudocode:**
```python
def get_relevant_lessons(self, project_type, tech_stack, phase=None, limit=15):
    all_lessons: dict[str, tuple[LessonLearned, float]] = {}  # title -> (lesson, score)

    # --- Local lessons (keyword-based, no embeddings) ---
    for lesson in local_lessons:
        keyword_score = lesson.matches_context(project_type, tech_stack)
        if keyword_score > 0.3:
            all_lessons[lesson.title.lower()] = (lesson, keyword_score)

    # --- Supabase lessons (try semantic first, fallback to keyword) ---
    if supabase_available:
        # Build semantic query from project context
        query_text = f"{project_type} project using {', '.join(tech_stack)}"
        semantic_results = self._query_supabase_semantic(query_text, tech_stack, limit=30)

        if semantic_results:
            # Hybrid scoring: semantic + metadata + confidence
            for lesson, similarity in semantic_results:
                key = lesson.title.lower()
                metadata_score = lesson.matches_context(project_type, tech_stack)
                hybrid_score = (
                    similarity * 0.50 +          # Semantic relevance
                    metadata_score * 0.30 +       # Tech/project type match
                    lesson.confidence * 0.20      # Quality signal
                )
                if key in all_lessons:
                    existing_lesson, existing_score = all_lessons[key]
                    existing_lesson.confidence = max(existing_lesson.confidence, lesson.confidence)
                    existing_lesson.frequency += lesson.frequency
                    all_lessons[key] = (existing_lesson, max(existing_score, hybrid_score))
                else:
                    all_lessons[key] = (lesson, hybrid_score)
        else:
            # Fallback: current keyword-based Supabase query
            # (unchanged from current implementation)
            supabase_lessons = self._query_supabase_sync(project_type, tech_stack)
            for lesson in supabase_lessons:
                key = lesson.title.lower()
                if key not in all_lessons:
                    score = lesson.matches_context(project_type, tech_stack)
                    all_lessons[key] = (lesson, score)

    # --- Phase filter + rank ---
    # Apply phase category filter (unchanged)
    # Sort by hybrid score descending
    # Return top N lessons
```

#### Task 3: Upgrade get_patterns_for_feature() with semantic search
**Files:** `agent/memory_bridge.py`
**Depends on:** Task 1
**Pseudocode:**
```python
def get_patterns_for_feature(self, feature_name, project_type, tech_stack, limit=3):
    # Try semantic search first
    semantic_results = self._query_supabase_semantic(
        f"implementation patterns for {feature_name}",
        tech_stack,
        limit=limit * 2,
    )

    if semantic_results:
        # Merge with local keyword results
        # Deduplicate, rank by hybrid score
        # Return top N
    else:
        # Fallback to current word-by-word keyword matching
        # (unchanged)
```

#### Task 4: Add playbook_search_lessons MCP tool
**Files:** `mcp_server/playbook_mcp.py`
**Depends on:** Task 1
**Pseudocode:**
```python
@mcp.tool(name="playbook_search_lessons")
async def search_lessons(query: str, limit: int = 10) -> str:
    """
    Search lessons using semantic similarity.

    Args:
        query: Natural language query (e.g., "database security patterns")
        limit: Maximum results (default 10)

    Returns:
        Matching lessons ranked by relevance
    """
    bridge = MemoryBridge.get_instance()
    results = bridge._query_supabase_semantic(query, limit=limit)

    if not results:
        # Fallback to keyword search
        results = [(l, 0.5) for l in bridge.get_relevant_lessons("", [], limit=limit)]

    # Format as markdown with similarity scores
```

### Integration Points
- **Connects to:** Supabase `match_lessons` RPC (from PRP-10), `agent/embedding.py` (from PRP-10)
- **Called by:** Orchestrator (`_generate_claude_md`, `_generate_prd`, `discovery_node`, `_get_learned_features`), new MCP tool
- **Depends on:** PRP-10 (pgvector + embeddings must be in place)

## Validation Loop

### Level 1: Syntax & Style
```bash
.venv/Scripts/python.exe -c "
import py_compile
py_compile.compile('agent/memory_bridge.py', doraise=True)
py_compile.compile('mcp_server/playbook_mcp.py', doraise=True)
print('Syntax OK')
"
```

### Level 2: Type Safety
```bash
.venv/Scripts/python.exe -c "
from agent.memory_bridge import MemoryBridge
print('MemoryBridge imports OK')
"
```

### Level 3: Unit Tests
```bash
.venv/Scripts/python.exe -c "
from agent.memory_bridge import MemoryBridge

bridge = MemoryBridge.get_instance()

# Test 1: get_relevant_lessons still works (backward compatible)
lessons = bridge.get_relevant_lessons('saas', ['nextjs', 'postgresql-supabase'])
print(f'Relevant lessons: {len(lessons)}')
assert len(lessons) > 0, 'Should find some lessons'

# Test 2: get_patterns_for_feature still works
patterns = bridge.get_patterns_for_feature('Authentication', 'saas', ['nextjs'])
print(f'Feature patterns: {len(patterns)}')

# Test 3: Graceful fallback (no Supabase in unit test)
lessons2 = bridge.get_relevant_lessons('api', ['fastapi'])
print(f'Fallback lessons: {len(lessons2)}')

print('All MemoryBridge tests passed!')
"
```

### Level 4: Integration Tests
```bash
# With Supabase configured (after PRP-10 backfill):
.venv/Scripts/python.exe -c "
import asyncio
from mcp_server.playbook_mcp import search_lessons

# Test semantic search
result = asyncio.run(search_lessons('database security and access control'))
print(result[:500])

# Test semantic search for feature
result2 = asyncio.run(search_lessons('frontend state management patterns'))
print(result2[:500])
"
```

### Level 5: Build Verification
```bash
.venv/Scripts/python.exe -c "from mcp_server.playbook_mcp import mcp; print('MCP import OK')"
```

## Final Validation Checklist
- [ ] Semantic search returns relevant lessons for 3+ test queries
- [ ] Hybrid scoring ranks better than pure keyword matching
- [ ] `get_relevant_lessons()` still works without Supabase (local fallback)
- [ ] `get_patterns_for_feature()` returns semantically relevant patterns
- [ ] `playbook_search_lessons` MCP tool works
- [ ] No performance regression (<500ms retrieval)
- [ ] Phase filtering still works correctly
- [ ] Deduplication still works (local + Supabase)
- [ ] Documentation updated (ONBOARDING.md tools count)

## Anti-Patterns
- Do NOT remove keyword matching — hybrid means BOTH semantic + keyword, not one replacing the other
- Do NOT call `generate_query_embedding()` inside loops — generate once, reuse
- Do NOT skip phase filtering after semantic search — semantic results are broad, phase narrows them
- Do NOT make embedding a hard dependency — always fallback gracefully to keyword matching
- Do NOT embed the entire lesson object — only title + description + recommendation
- Do NOT return raw similarity scores to users — convert to human-readable confidence
- Do NOT query semantic search for local lessons — local DB has no embeddings, keep keyword-based
