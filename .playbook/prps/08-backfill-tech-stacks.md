# PRP: Backfill tech_stacks in Existing Lessons

## Goal
Populate the empty `tech_stacks[]` field in existing lessons so that technology-based filtering actually works when MemoryBridge queries lessons.

## Why
80% of the 54 local lessons (and likely 100% of Supabase lessons) have `tech_stacks: []`. When the orchestrator generates a CLAUDE.md for a Next.js + Supabase project and MemoryBridge runs `.overlaps("tech_stacks", ["nextjs", "supabase"])`, it returns zero results because there's nothing to overlap with. The lessons exist, the retrieval code works, but the data is missing the field that enables filtered search. This is a data quality issue with a simple fix.

## What
1. Create a script that analyzes each lesson's `title`, `description`, `recommendation`, and `tags` to infer tech_stacks
2. Apply the backfill to both `data/lessons.json` (local) and Supabase `lessons_learned` table
3. Normalize tech stack names to match the values used by the orchestrator's discovery questions

## Success Criteria
- [ ] 90%+ of lessons have at least one entry in `tech_stacks[]`
- [ ] Tech stack names are normalized (e.g., "react" not "React", "nextjs" not "Next.js")
- [ ] Running `playbook_team_lessons` with a tech filter returns relevant lessons
- [ ] MemoryBridge's `get_relevant_lessons("saas", ["nextjs", "supabase"])` returns 5+ matches
- [ ] Idempotent — running the script twice produces the same result

## Context

### Must-Read Files
- `data/lessons.json` — 54 lessons, inspect the `tags` and `title` fields for tech clues
- `agent/meta_learning/models.py` — `LessonLearned` model with `tech_stacks: list[str]`
- `agent/memory_bridge.py` — `_query_supabase_sync()` line 229 uses `.overlaps("tech_stacks", tech_stack)`
- `agent/orchestrator.py` — discovery questions use these tech values: `react-vite`, `nextjs`, `vue-nuxt`, `fastapi`, `express`, `django`, `serverless`, `postgresql-supabase`, `mongodb`, `sqlite`, `firebase`

### Codebase Context
- The orchestrator stores tech_stack values from DISCOVERY_QUESTIONS options: `react-vite`, `nextjs`, `vue-nuxt`, `none`, `fastapi`, `express`, `django`, `serverless`, `postgresql-supabase`, `mongodb`, `sqlite`, `firebase`
- MemoryBridge local query uses `matches_context()` which checks `set(tech_stacks) & set(tech_stack)` for overlap
- Supabase query uses PostgreSQL `overlaps()` operator on the `tech_stacks` array column

### Known Gotchas
- Tech names in lesson tags use mixed formats: "react", "React", "supabase", "Supabase" — normalize to lowercase
- Some lessons are generic (e.g., "Scope Creep") and genuinely apply to all tech stacks — these should keep `tech_stacks: []` empty or use a sentinel like `["general"]`
- The tag "shadcn" implies React ecosystem; "rls" implies Supabase; "jwt" implies backend auth
- Don't confuse lesson tags (free-form) with tech_stacks (controlled vocabulary matching orchestrator values)

### Relevant Patterns
- Orchestrator tech values are the canonical vocabulary. Map tag synonyms to these values:
  - `react`, `React`, `shadcn`, `react-hook-form` → `react-vite` or `nextjs`
  - `supabase`, `rls`, `row-level-security` → `postgresql-supabase`
  - `fastapi`, `python`, `pydantic` → `fastapi`
  - `next.js`, `Next.js`, `nextjs` → `nextjs`
  - `express`, `node`, `nodejs` → `express`

## Implementation Blueprint

### Data Models
No new models. Use existing `LessonLearned.tech_stacks: list[str]`.

### Tasks

#### Task 1: Define tech stack inference mapping
**Files:** `scripts/backfill_tech_stacks.py` (new file)
**Pseudocode:**
```python
# Mapping from keywords found in tags/title/description → canonical tech_stack values
TECH_INFERENCE_MAP = {
    # Frontend
    "react": "react-vite",
    "shadcn": "react-vite",
    "react-hook-form": "react-vite",
    "vite": "react-vite",
    "nextjs": "nextjs",
    "next.js": "nextjs",
    "next": "nextjs",
    "vue": "vue-nuxt",
    "nuxt": "vue-nuxt",

    # Backend
    "fastapi": "fastapi",
    "python": "fastapi",  # Most Python lessons in our context are FastAPI
    "pydantic": "fastapi",
    "express": "express",
    "node": "express",
    "django": "django",

    # Database
    "supabase": "postgresql-supabase",
    "rls": "postgresql-supabase",
    "row-level-security": "postgresql-supabase",
    "postgresql": "postgresql-supabase",
    "postgres": "postgresql-supabase",
    "mongodb": "mongodb",
    "firebase": "firebase",
    "sqlite": "sqlite",
}

def infer_tech_stacks(lesson: dict) -> list[str]:
    """Analyze lesson fields to infer tech_stacks."""
    searchable = " ".join([
        lesson.get("title", ""),
        lesson.get("description", ""),
        lesson.get("recommendation", ""),
        " ".join(lesson.get("tags", [])),
    ]).lower()

    inferred = set()
    for keyword, tech in TECH_INFERENCE_MAP.items():
        if keyword in searchable:
            inferred.add(tech)

    return sorted(inferred)
```

#### Task 2: Apply backfill to local lessons.json
**Files:** `scripts/backfill_tech_stacks.py`
**Depends on:** Task 1
**Pseudocode:**
```python
def backfill_local():
    lessons_file = Path("data/lessons.json")
    data = json.loads(lessons_file.read_text(encoding="utf-8"))

    updated = 0
    for lesson in data["lessons"]:
        if not lesson.get("tech_stacks"):  # Only fill empty ones
            inferred = infer_tech_stacks(lesson)
            if inferred:
                lesson["tech_stacks"] = inferred
                updated += 1

    # Save back
    lessons_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Updated {updated}/{len(data['lessons'])} lessons with tech_stacks")
```

#### Task 3: Apply backfill to Supabase lessons
**Files:** `scripts/backfill_tech_stacks.py`
**Depends on:** Task 1
**Pseudocode:**
```python
def backfill_supabase():
    load_dotenv()
    db = configure_supabase(...)

    # Fetch all team lessons
    result = db.client.table("lessons_learned").select("*").eq("team_id", db.team_id).execute()

    updated = 0
    for row in result.data:
        if not row.get("tech_stacks"):
            inferred = infer_tech_stacks(row)
            if inferred:
                db.client.table("lessons_learned").update(
                    {"tech_stacks": inferred}
                ).eq("id", row["id"]).execute()
                updated += 1

    print(f"Updated {updated} Supabase lessons with tech_stacks")
```

#### Task 4: Also fix auto-capture to populate tech_stacks
**Files:** `agent/meta_learning/capture.py`
**Depends on:** Task 1
**Pseudocode:**
```python
# In auto_capture_phase_lesson(), the tech_stack from project.tech_stack is already
# being passed to new LessonLearned objects. Verify this is correct.
#
# Current code (line 362):
#   tech_stacks=tech_stack  (where tech_stack = [frontend, backend, database])
#
# This IS correct — new auto-captured lessons will have tech_stacks populated.
# The problem is only with EXISTING lessons that were captured before this was consistent.
# No code change needed here — just verify.
```

### Integration Points
- **Connects to:** `data/lessons.json`, Supabase `lessons_learned` table
- **Called by:** One-time migration script (manual execution)
- **Depends on:** PRP-07 (if running after Supabase sync, ensures Supabase has all lessons to backfill)

## Validation Loop

### Level 1: Syntax & Style
```bash
ruff check scripts/backfill_tech_stacks.py --fix
ruff format scripts/backfill_tech_stacks.py
```

### Level 2: Type Safety
```bash
mypy scripts/backfill_tech_stacks.py --ignore-missing-imports
```

### Level 3: Unit Tests
```bash
# Test inference logic
.venv/Scripts/python.exe -c "
from scripts.backfill_tech_stacks import infer_tech_stacks

# Test React lesson
lesson = {'title': 'Controlled Tabs for State Persistence', 'tags': ['react', 'shadcn', 'ui']}
result = infer_tech_stacks(lesson)
print(f'React lesson: {result}')
assert 'react-vite' in result

# Test Supabase lesson
lesson = {'title': 'Supabase Nested Relations', 'description': 'RLS with supabase', 'tags': ['supabase']}
result = infer_tech_stacks(lesson)
print(f'Supabase lesson: {result}')
assert 'postgresql-supabase' in result

# Test generic lesson (no tech)
lesson = {'title': 'Scope Creep', 'description': 'Project scope expanded', 'tags': ['pitfall']}
result = infer_tech_stacks(lesson)
print(f'Generic lesson: {result}')
assert result == []

print('All inference tests passed!')
"
```

### Level 4: Integration Tests
```bash
# Dry run on real data (read-only)
.venv/Scripts/python.exe -c "
import json
from pathlib import Path

data = json.loads(Path('data/lessons.json').read_text(encoding='utf-8'))
empty = sum(1 for l in data['lessons'] if not l.get('tech_stacks'))
print(f'Before: {empty}/{len(data[\"lessons\"])} lessons have empty tech_stacks')
"
```

### Level 5: Build Verification
```bash
.venv/Scripts/python.exe -c "from scripts.backfill_tech_stacks import infer_tech_stacks; print('OK')"
```

## Final Validation Checklist
- [ ] Inference mapping covers all tech stacks from orchestrator DISCOVERY_QUESTIONS
- [ ] Local lessons.json updated — 90%+ have tech_stacks populated
- [ ] Supabase lessons updated (after PRP-07 sync)
- [ ] Generic lessons (no tech) remain with empty tech_stacks (not force-filled)
- [ ] Script is idempotent (running twice gives same result)
- [ ] MemoryBridge filtering returns more results after backfill

## Anti-Patterns
- Do NOT overwrite existing non-empty tech_stacks — only fill empty ones
- Do NOT force a tech_stack on generic lessons (like "Scope Creep") — keep them generic
- Do NOT use fuzzy matching — use exact keyword presence in lowercase text
- Do NOT map "python" → "fastapi" for lessons that are clearly about Django or general Python (check context)
- Do NOT modify lesson content (title, description) — only modify the tech_stacks field
