# PRP: Lesson Effectiveness Tracking

## Goal
Add a feedback loop that tracks whether surfaced lessons were actually useful, so lesson quality improves over time through real usage data.

## Why
Archie surfaces lessons in every CLAUDE.md, PRD, and PRP — but has no way to know if those lessons helped. A lesson about "RLS policies" might be surfaced 50 times but never actually relevant. Without effectiveness tracking, low-quality lessons pollute the knowledge base forever. This PRP adds a lightweight feedback mechanism: when Archie surfaces lessons, it records it; when the user rates them, confidence adjusts automatically. Over time, useful lessons rise and useless ones decay.

## What
1. Track which lessons get surfaced (increment a `times_surfaced` counter)
2. Add `playbook_rate_lesson` MCP tool — user rates a specific lesson as helpful/not-helpful
3. Auto-decay: lessons surfaced 10+ times with zero positive ratings lose confidence
4. Wire surfacing tracking into MemoryBridge retrieval

## Success Criteria
- [ ] Every lesson retrieval increments `times_surfaced` on returned lessons
- [ ] `playbook_rate_lesson` adjusts confidence based on helpful/not-helpful feedback
- [ ] Lessons surfaced 10+ times with 0 helpful ratings get confidence reduced
- [ ] `playbook_lesson_stats` shows effectiveness metrics (surfaced vs. rated)
- [ ] No performance regression from tracking (async, non-blocking)

## Context

### Must-Read Files
- `agent/meta_learning/models.py` — `LessonLearned` model, `LessonsDatabase` class
- `agent/memory_bridge.py` — `get_relevant_lessons()`, `semantic_search()` — retrieval entry points
- `mcp_server/playbook_mcp.py` — Existing `playbook_vote_lesson`, `playbook_lesson_stats` tools
- `agent/supabase_client.py` — `update_lesson()` method for Supabase sync

### Codebase Context
- `LessonLearned` model already has `upvotes`, `downvotes`, `frequency` fields
- `playbook_vote_lesson` already adjusts confidence by +/-0.05 — extend this for effectiveness
- `LessonsDatabase._save()` persists to JSON with UTF-8 encoding
- MemoryBridge retrieves from both local + Supabase — tracking should cover both

### Known Gotchas
- Don't make tracking synchronous in the retrieval path — it must not slow down lesson retrieval
- Local lessons and Supabase lessons need separate tracking (local = file, Supabase = DB column)
- `times_surfaced` should only increment once per retrieval call, not per-lesson (avoid double-counting)
- Don't auto-decay lessons that were never surfaced (they might just not match current projects)

### Relevant Patterns
- Current vote mechanism in `playbook_vote_lesson` (MCP tool)
- `LessonsDatabase.update_lesson_confidence()` method
- Non-blocking pattern: try/except with pass for tracking failures

## Implementation Blueprint

### Data Models
```python
# Add to LessonLearned model in agent/meta_learning/models.py
times_surfaced: int = 0    # How many times this lesson was returned in a query
times_helpful: int = 0     # How many times rated as helpful
times_not_helpful: int = 0 # How many times rated as not helpful
```

### Tasks

#### Task 1: Add effectiveness fields to LessonLearned
**Files:** `agent/meta_learning/models.py`
**Pseudocode:**
```python
class LessonLearned(BaseModel):
    # ... existing fields ...
    times_surfaced: int = 0
    times_helpful: int = 0
    times_not_helpful: int = 0

    @property
    def effectiveness_score(self) -> float | None:
        """Effectiveness ratio (None if not enough data)."""
        total_ratings = self.times_helpful + self.times_not_helpful
        if total_ratings < 2:
            return None
        return self.times_helpful / total_ratings
```

#### Task 2: Track surfacing in MemoryBridge
**Files:** `agent/memory_bridge.py`
**Depends on:** Task 1
**Pseudocode:**
```python
def get_relevant_lessons(self, ...):
    # ... existing retrieval logic ...
    # After ranking, before return:
    for lesson, _ in ranked[:limit]:
        lesson.times_surfaced += 1
    # Save updated local lessons (non-blocking)
    try:
        self._local_db._save()
    except Exception:
        pass
    return [lesson for lesson, _ in ranked[:limit]]
```

#### Task 3: Add playbook_rate_lesson MCP tool
**Files:** `mcp_server/playbook_mcp.py`
**Depends on:** Task 1
**Pseudocode:**
```python
@mcp.tool(name="playbook_rate_lesson")
async def rate_lesson(title: str, helpful: bool) -> str:
    """Rate a lesson as helpful or not helpful.

    Args:
        title: Lesson title (or partial match)
        helpful: True if the lesson was useful, False if not
    """
    # Update local DB
    db = get_lessons_db()
    for lesson in db.get_lessons():
        if title.lower() in lesson.title.lower():
            if helpful:
                lesson.times_helpful += 1
                lesson.confidence = min(1.0, lesson.confidence + 0.02)
            else:
                lesson.times_not_helpful += 1
                lesson.confidence = max(0.1, lesson.confidence - 0.03)
            lesson.updated_at = datetime.utcnow()
            db._save()
            break

    # Update Supabase too (if connected)
    # Return formatted result
```

#### Task 4: Auto-decay low-effectiveness lessons
**Files:** `agent/memory_bridge.py`
**Depends on:** Task 1, Task 2
**Pseudocode:**
```python
# In get_relevant_lessons(), after retrieval:
# Apply effectiveness penalty to ranking score
for key, (lesson, score) in all_lessons.items():
    eff = lesson.effectiveness_score
    if eff is not None and eff < 0.3:
        score *= 0.7  # Penalize low-effectiveness lessons
    if lesson.times_surfaced >= 10 and lesson.times_helpful == 0:
        score *= 0.5  # Heavy penalty for often-surfaced-never-helpful
    all_lessons[key] = (lesson, score)
```

#### Task 5: Enhance playbook_lesson_stats with effectiveness
**Files:** `mcp_server/playbook_mcp.py`
**Depends on:** Task 1
**Pseudocode:**
```python
# In playbook_lesson_stats, add effectiveness section:
# - Total lessons surfaced vs. rated
# - Top 5 most effective lessons
# - Bottom 5 (candidates for removal)
# - Lessons surfaced 10+ times with no ratings
```

### Integration Points
- **Connects to:** LessonsDatabase (local), Supabase lessons table (remote)
- **Called by:** MemoryBridge (surfacing tracking), MCP tools (rating), Heartbeat (decay)
- **Depends on:** Level 1-2 (existing lesson infrastructure)

## Validation Loop

### Level 1: Syntax & Style
```bash
.venv/Scripts/python.exe -c "
import py_compile
py_compile.compile('agent/meta_learning/models.py', doraise=True)
py_compile.compile('agent/memory_bridge.py', doraise=True)
py_compile.compile('mcp_server/playbook_mcp.py', doraise=True)
print('Syntax OK')
"
```

### Level 2: Type Safety
```bash
.venv/Scripts/python.exe -c "
from agent.meta_learning.models import LessonLearned
l = LessonLearned(title='Test', description='Test', recommendation='Test')
assert l.times_surfaced == 0
assert l.effectiveness_score is None
l.times_surfaced = 10
l.times_helpful = 3
l.times_not_helpful = 1
assert l.effectiveness_score == 0.75
print('Type checks OK')
"
```

### Level 3: Unit Tests
```bash
.venv/Scripts/python.exe -c "
from agent.meta_learning.models import LessonLearned, get_lessons_db
db = get_lessons_db()
lessons = db.get_lessons()
# Verify new fields don't break existing lessons
assert all(hasattr(l, 'times_surfaced') for l in lessons)
print(f'All {len(lessons)} lessons have effectiveness fields')
"
```

### Level 5: Build Verification
```bash
.venv/Scripts/python.exe -c "from mcp_server.playbook_mcp import mcp; print('MCP import OK')"
```

## Final Validation Checklist
- [ ] LessonLearned has `times_surfaced`, `times_helpful`, `times_not_helpful` fields
- [ ] `effectiveness_score` property works correctly
- [ ] MemoryBridge tracks surfacing on retrieval
- [ ] `playbook_rate_lesson` works for helpful and not-helpful
- [ ] `playbook_lesson_stats` shows effectiveness metrics
- [ ] Auto-decay penalizes low-effectiveness lessons in ranking
- [ ] Existing lessons load without errors (backward-compatible defaults)

## Anti-Patterns
- Do NOT make surfacing tracking synchronous/blocking — it must not slow retrieval
- Do NOT auto-delete lessons based on effectiveness — only reduce ranking score
- Do NOT track surfacing for direct `semantic_search()` calls (only `get_relevant_lessons`)
- Do NOT require rating — it's optional, lessons work fine without ratings
- Do NOT reset effectiveness counters on lesson update — they represent lifetime data
