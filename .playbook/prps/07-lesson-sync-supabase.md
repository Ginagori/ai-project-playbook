# PRP: Sync Auto-Captured Lessons to Supabase

## Goal
Ensure every auto-captured lesson is saved to both local JSON and Supabase, so the entire team benefits from accumulated knowledge — not just the developer whose session captured it.

## Why
Today `auto_capture_phase_lesson()` saves to `data/lessons.json` (local only). The result: local DB has 54 lessons, but Supabase only has 10 (manually shared via `playbook_share_lesson`). When MemoryBridge queries Supabase for team lessons, it only sees 10. The other 44 lessons are invisible to the retrieval pipeline when queried from Supabase, and invisible to other team members entirely. This is the single biggest gap in Archie's memory — the auto-capture system works, but its output doesn't reach the shared knowledge base.

## What
1. Modify `auto_capture_phase_lesson()` to also save each captured lesson to Supabase via the existing `SupabaseClient.share_lesson()` method
2. Create a one-time migration script that pushes all 54 existing local lessons to Supabase (deduplicating by title)
3. Configure MemoryBridge to be initialized with the Supabase client at startup (it already is via EngineCoordinator, but verify the fallback path)

## Success Criteria
- [ ] Every call to `auto_capture_phase_lesson()` saves to both local JSON AND Supabase
- [ ] Running the migration script pushes existing local lessons to Supabase without duplicates
- [ ] `playbook_team_lessons` returns 50+ lessons (up from 10)
- [ ] MemoryBridge retrieves lessons from both sources and deduplicates by title
- [ ] No regression — existing local save path continues to work when Supabase is unavailable

## Context

### Must-Read Files
- `agent/meta_learning/capture.py` — auto-capture logic, lines 335-474 (the `auto_capture_phase_lesson` function)
- `agent/meta_learning/models.py` — `LessonsDatabase.add_lesson()` local save method
- `agent/supabase_client.py` — `share_lesson()` method for Supabase persistence
- `agent/memory_bridge.py` — retrieval pipeline that merges local + Supabase
- `mcp_server/playbook_mcp.py` — `playbook_share_lesson` tool shows the Supabase save pattern (line ~1500+)
- `data/lessons.json` — current 54 local lessons

### Codebase Context
- The MemoryBridge singleton is initialized with the Supabase client via `EngineCoordinator.initialize()` → `MemoryEngine.__init__(supabase_client)` → `MemoryBridge.configure(supabase_client)`
- `auto_capture_phase_lesson()` is called at every phase transition in orchestrator.py (discovery→line 384, planning→line 462, roadmap→line 1199)
- The `SupabaseClient` is available as `db` in `playbook_mcp.py` and passed to EngineCoordinator
- Local lessons use `LessonsDatabase` (file-based), team lessons use `SupabaseClient.share_lesson()`

### Known Gotchas
- `auto_capture_phase_lesson()` is called synchronously from orchestrator nodes — Supabase save must not block or crash the pipeline if Supabase is down
- Deduplication on sync: local DB may have lessons with slightly different titles than Supabase. Use title.lower().strip() for matching
- The Supabase `share_lesson()` expects `team_id` — must pass it from environment. Already available in `SupabaseClient.team_id`
- Rate consideration: auto-capture creates 1-3 lessons per phase transition. With 5 phases, max ~15 lessons per project run. Not a volume concern

### Relevant Patterns
- Look at how `playbook_share_lesson` in `playbook_mcp.py` calls `db.share_lesson()` — follow the same pattern
- The MemoryBridge already handles Supabase failures gracefully (try/except, returns empty list)
- Follow the pattern: save locally first (fast, reliable), then save to Supabase (async best-effort)

## Implementation Blueprint

### Data Models
No new models needed. Existing `LessonLearned` Pydantic model is used by both local and Supabase paths.

### Tasks

#### Task 1: Pass Supabase client to auto_capture_phase_lesson
**Files:** `agent/meta_learning/capture.py`
**Pseudocode:**
```python
# Modify auto_capture_phase_lesson signature to accept optional supabase_client
def auto_capture_phase_lesson(phase: str, project: ProjectState, supabase_client=None) -> list[LessonLearned]:
    # ... existing lesson generation logic stays the same ...

    # Store lessons in local database (existing)
    if lessons:
        db = get_lessons_db()
        for lesson in lessons:
            db.add_lesson(lesson)

    # NEW: Also sync to Supabase if available
    if lessons and supabase_client and getattr(supabase_client, 'is_configured', False):
        for lesson in lessons:
            try:
                supabase_client.share_lesson(
                    title=lesson.title,
                    description=lesson.description,
                    recommendation=lesson.recommendation,
                    category=lesson.category.value,
                    project_type=lesson.project_types[0] if lesson.project_types else "unknown",
                    tech_stack=",".join(lesson.tech_stacks),
                    tags=lesson.tags,
                    confidence=lesson.confidence,
                    contributed_by="archie-auto-capture",
                )
            except Exception as e:
                print(f"[Archie] Supabase sync for lesson '{lesson.title}' failed: {e}")

    return lessons
```

#### Task 2: Pass Supabase client from orchestrator nodes
**Files:** `agent/orchestrator.py`
**Depends on:** Task 1
**Pseudocode:**
```python
# In discovery_node(), planning_node(), roadmap_node() — where auto_capture_phase_lesson is called:

# Get Supabase client from engine coordinator
def _get_supabase_client():
    """Get Supabase client from engine coordinator if available."""
    if _engine_coordinator and hasattr(_engine_coordinator, 'memory'):
        memory = _engine_coordinator.memory
        if hasattr(memory, '_supabase'):
            return memory._supabase
    return None

# Then in each phase node, change:
#   auto_capture_phase_lesson("discovery", project)
# to:
#   auto_capture_phase_lesson("discovery", project, supabase_client=_get_supabase_client())
```

#### Task 3: Verify share_lesson method compatibility
**Files:** `agent/supabase_client.py`
**Depends on:** Task 1
**Pseudocode:**
```python
# Verify that share_lesson() accepts the fields we need
# Check if it accepts 'confidence' and 'contributed_by' params
# If not, add optional params:
#   confidence: float = 0.5
#   contributed_by: str = ""
# This is a read-and-verify task — may need minor signature changes
```

#### Task 4: Create one-time migration script
**Files:** `scripts/sync_lessons_to_supabase.py` (new file)
**Depends on:** Task 3
**Pseudocode:**
```python
# scripts/sync_lessons_to_supabase.py
"""One-time migration: push all local lessons to Supabase."""

import json
from pathlib import Path
from agent.supabase_client import configure_supabase
from dotenv import load_dotenv
import os

def migrate():
    load_dotenv()
    db = configure_supabase(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_ANON_KEY"), os.getenv("PLAYBOOK_TEAM_ID"))

    # Load local lessons
    lessons_file = Path("data/lessons.json")
    data = json.loads(lessons_file.read_text())

    # Get existing Supabase lessons (for dedup)
    existing = db.get_team_lessons(limit=100)
    existing_titles = {l["title"].lower().strip() for l in existing}

    # Sync new lessons
    synced = 0
    skipped = 0
    for lesson in data["lessons"]:
        if lesson["title"].lower().strip() in existing_titles:
            skipped += 1
            continue
        db.share_lesson(
            title=lesson["title"],
            description=lesson["description"],
            recommendation=lesson["recommendation"],
            category=lesson["category"],
            project_type=lesson["project_types"][0] if lesson["project_types"] else "unknown",
            tech_stack=",".join(lesson.get("tech_stacks", [])),
            tags=lesson.get("tags", []),
        )
        synced += 1

    print(f"Synced {synced} lessons, skipped {skipped} duplicates")

if __name__ == "__main__":
    migrate()
```

### Integration Points
- **Connects to:** Supabase `lessons_learned` table, local `data/lessons.json`
- **Called by:** `auto_capture_phase_lesson()` → orchestrator nodes → MCP tools
- **Depends on:** Supabase client configured via env vars, existing `share_lesson()` method

## Validation Loop

### Level 1: Syntax & Style
```bash
ruff check agent/meta_learning/capture.py agent/orchestrator.py --fix
ruff format agent/meta_learning/capture.py agent/orchestrator.py
```

### Level 2: Type Safety
```bash
mypy agent/meta_learning/capture.py agent/orchestrator.py --ignore-missing-imports
```

### Level 3: Unit Tests
```bash
# Test auto_capture_phase_lesson with mock Supabase client
.venv/Scripts/python.exe -c "
from agent.meta_learning.capture import auto_capture_phase_lesson
from agent.models.project import ProjectState, ProjectType, Phase
p = ProjectState(id='test', objective='Test', project_type=ProjectType.SAAS, current_phase=Phase.PLANNING)
p.tech_stack.frontend = 'nextjs'
p.tech_stack.backend = 'fastapi'
p.tech_stack.database = 'postgresql-supabase'
lessons = auto_capture_phase_lesson('discovery', p)
print(f'Captured {len(lessons)} lessons (local only, no Supabase)')
for l in lessons:
    print(f'  - {l.title}')
"
```

### Level 4: Integration Tests
```bash
# Test with real Supabase (requires env vars)
.venv/Scripts/python.exe -c "
import asyncio
from mcp_server.playbook_mcp import start_project
result = asyncio.run(start_project('Test memory sync', 'supervised'))
print(result[:500])
"
```

### Level 5: Build Verification
```bash
.venv/Scripts/python.exe -c "from agent.meta_learning.capture import auto_capture_phase_lesson; print('OK')"
```

## Final Validation Checklist
- [ ] All tasks completed (no TODOs in code)
- [ ] `auto_capture_phase_lesson()` saves to local AND Supabase
- [ ] Graceful degradation when Supabase is unavailable
- [ ] Migration script runs without errors
- [ ] `playbook_team_lessons` shows 50+ lessons after migration
- [ ] No duplicate lessons in Supabase after running migration twice

## Anti-Patterns
- Do NOT make Supabase sync blocking — if Supabase is down, local save must still work
- Do NOT remove the local save path — it's the reliable fallback
- Do NOT create a new table or schema — use existing `lessons_learned` table
- Do NOT sync lessons with confidence < 0.4 to Supabase (noise filtering)
- Do NOT batch all lessons into a single Supabase call — individual inserts with error handling per lesson
