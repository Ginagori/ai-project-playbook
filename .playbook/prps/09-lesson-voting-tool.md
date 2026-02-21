# PRP: Add Lesson Voting and Cleanup MCP Tools

## Goal
Give the team the ability to upvote, downvote, and remove lessons via MCP tools, so lesson quality improves over time instead of accumulating noise.

## Why
The `lessons_learned` table already has `upvotes` and `downvotes` fields (and MemoryBridge uses `confidence` for ranking), but there's no MCP tool to modify them. As auto-capture generates more lessons (especially after PRP-07), the team needs a way to signal which lessons are valuable and which are noise. Without voting, low-quality auto-captured lessons dilute the knowledge base. Without cleanup, duplicate or outdated lessons accumulate. The cost of adding 3 simple tools is low; the cost of a polluted knowledge base is high.

## What
1. `playbook_vote_lesson` — upvote or downvote a lesson by title (adjusts confidence)
2. `playbook_remove_lesson` — remove a lesson from both local and Supabase
3. `playbook_lesson_stats` — show lesson quality statistics (total, by category, low-confidence, duplicates)

## Success Criteria
- [ ] Team can upvote a lesson: `playbook_vote_lesson title="X" vote="up"`
- [ ] Team can downvote a lesson: `playbook_vote_lesson title="X" vote="down"`
- [ ] Upvoting increases confidence by 0.05, downvoting decreases by 0.05 (clamped 0.0-1.0)
- [ ] Team can remove a lesson: `playbook_remove_lesson title="X"`
- [ ] `playbook_lesson_stats` shows count by category, average confidence, flagged duplicates
- [ ] All operations work on both local JSON and Supabase

## Context

### Must-Read Files
- `mcp_server/playbook_mcp.py` — existing MCP tools pattern, `playbook_share_lesson` and `playbook_team_lessons` for reference
- `agent/meta_learning/models.py` — `LessonsDatabase` class with local JSON operations
- `agent/supabase_client.py` — Supabase operations pattern
- `data/lessons.json` — current lesson structure with confidence field

### Codebase Context
- MCP tools follow the `@mcp.tool(name="playbook_xxx")` decorator pattern
- All tools are async and call `await _ensure_engines_initialized()` first
- Supabase operations use `db.client.table("lessons_learned")` pattern
- Local operations use `get_lessons_db()` to get the `LessonsDatabase` singleton
- Current `LessonsDatabase` has `add_lesson()` but no `remove_lesson()` or `update_lesson()` methods

### Known Gotchas
- Lesson titles may not be unique — use case-insensitive matching with `.lower().strip()`
- When removing from Supabase, need to match by `title` + `team_id` (not by `id` since local lessons don't have Supabase IDs)
- Confidence should be clamped between 0.0 and 1.0 after vote adjustment
- The vote increment (0.05) is small by design — a lesson needs 6 upvotes to go from 0.5 to 0.8 (auto-injection threshold)

### Relevant Patterns
- Follow `playbook_share_lesson` pattern for the tool structure
- Follow `playbook_team_lessons` pattern for displaying results
- Local DB operations use `get_lessons_db()` singleton

## Implementation Blueprint

### Data Models
No new models. Uses existing `LessonLearned` with `confidence`, `upvotes`, `downvotes` fields.

### Tasks

#### Task 1: Add update/remove methods to LessonsDatabase
**Files:** `agent/meta_learning/models.py`
**Pseudocode:**
```python
class LessonsDatabase:
    # ... existing methods ...

    def update_lesson_confidence(self, title: str, delta: float, vote_type: str) -> bool:
        """Update a lesson's confidence and vote counts by title match."""
        title_lower = title.lower().strip()
        for lesson in self._lessons:
            if lesson.title.lower().strip() == title_lower:
                lesson.confidence = max(0.0, min(1.0, lesson.confidence + delta))
                if vote_type == "up":
                    lesson.upvotes = getattr(lesson, 'upvotes', 0) + 1
                else:
                    lesson.downvotes = getattr(lesson, 'downvotes', 0) + 1
                lesson.updated_at = datetime.now(timezone.utc).isoformat()
                self._save()
                return True
        return False

    def remove_lesson(self, title: str) -> bool:
        """Remove a lesson by title match."""
        title_lower = title.lower().strip()
        original_count = len(self._lessons)
        self._lessons = [l for l in self._lessons if l.title.lower().strip() != title_lower]
        if len(self._lessons) < original_count:
            self._save()
            return True
        return False

    def get_stats(self) -> dict:
        """Get lesson statistics."""
        categories = {}
        total_confidence = 0.0
        low_confidence = []

        for lesson in self._lessons:
            cat = lesson.category.value
            categories[cat] = categories.get(cat, 0) + 1
            total_confidence += lesson.confidence
            if lesson.confidence < 0.5:
                low_confidence.append(lesson.title)

        # Detect duplicates (similar titles)
        titles = [l.title.lower().strip() for l in self._lessons]
        duplicates = [t for t in set(titles) if titles.count(t) > 1]

        return {
            "total": len(self._lessons),
            "by_category": categories,
            "avg_confidence": total_confidence / max(len(self._lessons), 1),
            "low_confidence_count": len(low_confidence),
            "low_confidence_titles": low_confidence[:10],
            "duplicate_titles": duplicates,
        }
```

#### Task 2: Add vote_lesson MCP tool
**Files:** `mcp_server/playbook_mcp.py`
**Depends on:** Task 1
**Pseudocode:**
```python
@mcp.tool(name="playbook_vote_lesson")
async def vote_lesson(title: str, vote: str = "up") -> str:
    """
    Vote on a lesson to adjust its quality/confidence.

    Args:
        title: The lesson title (case-insensitive match)
        vote: "up" to increase confidence, "down" to decrease

    Returns:
        Confirmation with new confidence score
    """
    await _ensure_engines_initialized()

    if vote not in ("up", "down"):
        return "## Error\n\nVote must be 'up' or 'down'."

    delta = 0.05 if vote == "up" else -0.05

    # Update local
    local_db = get_lessons_db()
    local_updated = local_db.update_lesson_confidence(title, delta, vote)

    # Update Supabase
    supabase_updated = False
    if SUPABASE_ENABLED and db:
        try:
            result = db.client.table("lessons_learned") \
                .select("id, confidence, upvotes, downvotes") \
                .eq("team_id", db.team_id) \
                .ilike("title", title) \
                .execute()
            if result.data:
                row = result.data[0]
                new_conf = max(0.0, min(1.0, (row.get("confidence", 0.5) or 0.5) + delta))
                vote_field = "upvotes" if vote == "up" else "downvotes"
                current_votes = row.get(vote_field, 0) or 0
                db.client.table("lessons_learned") \
                    .update({
                        "confidence": new_conf,
                        vote_field: current_votes + 1,
                    }) \
                    .eq("id", row["id"]) \
                    .execute()
                supabase_updated = True
        except Exception as e:
            print(f"Supabase vote update failed: {e}")

    if not local_updated and not supabase_updated:
        return f"## Not Found\n\nNo lesson matching '{title}'."

    return f"## Vote Recorded\n\n**{title}** — {vote}voted.\nUpdated: {'local' if local_updated else ''} {'+ Supabase' if supabase_updated else ''}"
```

#### Task 3: Add remove_lesson MCP tool
**Files:** `mcp_server/playbook_mcp.py`
**Depends on:** Task 1
**Pseudocode:**
```python
@mcp.tool(name="playbook_remove_lesson")
async def remove_lesson(title: str) -> str:
    """
    Remove a lesson from the knowledge base.

    Args:
        title: The lesson title to remove (case-insensitive match)

    Returns:
        Confirmation of removal
    """
    await _ensure_engines_initialized()

    local_db = get_lessons_db()
    local_removed = local_db.remove_lesson(title)

    supabase_removed = False
    if SUPABASE_ENABLED and db:
        try:
            result = db.client.table("lessons_learned") \
                .delete() \
                .eq("team_id", db.team_id) \
                .ilike("title", title) \
                .execute()
            supabase_removed = bool(result.data)
        except Exception as e:
            print(f"Supabase remove failed: {e}")

    if not local_removed and not supabase_removed:
        return f"## Not Found\n\nNo lesson matching '{title}'."

    return f"## Lesson Removed\n\n**{title}** removed from {'local' if local_removed else ''} {'+ Supabase' if supabase_removed else ''}"
```

#### Task 4: Add lesson_stats MCP tool
**Files:** `mcp_server/playbook_mcp.py`
**Depends on:** Task 1
**Pseudocode:**
```python
@mcp.tool(name="playbook_lesson_stats")
async def lesson_stats() -> str:
    """
    Show lesson quality statistics and health metrics.

    Returns:
        Dashboard with counts, quality scores, and flagged issues
    """
    await _ensure_engines_initialized()

    local_db = get_lessons_db()
    stats = local_db.get_stats()

    output = f"""## Lesson Statistics

**Total lessons:** {stats['total']}
**Average confidence:** {stats['avg_confidence']:.0%}

### By Category
"""
    for cat, count in sorted(stats['by_category'].items()):
        output += f"- **{cat}**: {count}\n"

    if stats['low_confidence_titles']:
        output += f"\n### Low Confidence ({stats['low_confidence_count']} lessons < 50%)\n"
        for title in stats['low_confidence_titles']:
            output += f"- {title}\n"

    if stats['duplicate_titles']:
        output += f"\n### Duplicates Found ({len(stats['duplicate_titles'])})\n"
        for title in stats['duplicate_titles']:
            output += f"- {title}\n"

    return output
```

### Integration Points
- **Connects to:** `data/lessons.json`, Supabase `lessons_learned` table
- **Called by:** Team members via Claude Code MCP tools
- **Depends on:** Existing `get_lessons_db()` singleton, Supabase client

## Validation Loop

### Level 1: Syntax & Style
```bash
ruff check mcp_server/playbook_mcp.py agent/meta_learning/models.py --fix
ruff format mcp_server/playbook_mcp.py agent/meta_learning/models.py
```

### Level 2: Type Safety
```bash
mypy mcp_server/playbook_mcp.py agent/meta_learning/models.py --ignore-missing-imports
```

### Level 3: Unit Tests
```bash
.venv/Scripts/python.exe -c "
from agent.meta_learning.models import get_lessons_db
db = get_lessons_db()
stats = db.get_stats()
print(f'Total: {stats[\"total\"]}')
print(f'Categories: {stats[\"by_category\"]}')
print(f'Duplicates: {stats[\"duplicate_titles\"]}')
print('Stats test passed!')
"
```

### Level 4: Integration Tests
```bash
# Test vote tool
.venv/Scripts/python.exe -c "
import asyncio
from mcp_server.playbook_mcp import vote_lesson
result = asyncio.run(vote_lesson('Controlled Tabs for State Persistence', 'up'))
print(result)
"
```

### Level 5: Build Verification
```bash
.venv/Scripts/python.exe -c "from mcp_server.playbook_mcp import mcp; print('MCP import OK')"
```

## Final Validation Checklist
- [ ] `playbook_vote_lesson` works with "up" and "down" votes
- [ ] Vote adjusts confidence by +/-0.05 (clamped 0.0-1.0)
- [ ] `playbook_remove_lesson` removes from local and Supabase
- [ ] `playbook_lesson_stats` shows accurate statistics
- [ ] Case-insensitive title matching works
- [ ] Graceful handling when lesson not found
- [ ] Documentation updated (ONBOARDING.md tools count)

## Anti-Patterns
- Do NOT allow bulk deletion — only one lesson at a time (safety)
- Do NOT auto-remove low-confidence lessons — let the team decide
- Do NOT make vote delta configurable — fixed at 0.05 to prevent gaming
- Do NOT use lesson IDs for matching — use titles (consistent across local/Supabase)
- Do NOT skip the `_ensure_engines_initialized()` call in new tools
