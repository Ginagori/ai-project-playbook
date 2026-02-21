# PRP: Preferences Injection in Artifacts

## Goal
Wire existing learned preferences into CLAUDE.md and PRD generation so Archie's accumulated team preferences actively influence every new project.

## Why
The Memory Engine already has `get_active_preferences()` and `capture_preference()` — but the orchestrator's `_generate_claude_md()` and `_generate_prd()` completely ignore them. Preferences are stored but never used. This is the lowest-hanging fruit in Level 3: zero new infrastructure, just wire existing pieces together. The result: every new CLAUDE.md gets a "Team Preferences" section reflecting how Nivanta AI actually works.

## What
1. Inject active preferences into `_generate_claude_md()` as a "Team Preferences" section
2. Inject relevant preferences into `_generate_prd()` as context for tech decisions
3. Add preference surfacing in `discovery_node()` so Archie mentions preferences during discovery
4. Auto-capture a preference when the team picks the same tech stack 3+ times

## Success Criteria
- [ ] Generated CLAUDE.md includes "Team Preferences" section with active preferences
- [ ] Generated PRD references relevant preferences in tech stack rationale
- [ ] Discovery phase mentions applicable preferences ("based on team experience, we prefer X")
- [ ] Preferences with `status=approved` always appear; `pending` with confidence >= 0.8 appear
- [ ] No crash if preferences file is empty or missing

## Context

### Must-Read Files
- `agent/engines/memory_engine.py` — Has `get_active_preferences()`, `capture_preference()`, `LearnedPreference` model
- `agent/orchestrator.py` — Lines 680-707 (`_generate_claude_md`), lines 830-856 (`_generate_prd`), lines 220-356 (`discovery_node`)
- `data/preferences.json` — Current preferences file (may not exist yet)

### Codebase Context
- `_get_memory_engine()` helper already exists in orchestrator (line ~670)
- Memory Engine wraps MemoryBridge — uses same singleton pattern
- Preferences are `LearnedPreference` Pydantic models with `preference_type`, `content`, `confidence`, `status`
- Active preferences = `status == "approved"` OR (`status == "pending"` AND `confidence >= 0.8`)

### Known Gotchas
- `_get_memory_engine()` may return None if engines not initialized — always check
- Preferences file may not exist on first run — handle gracefully
- Don't inject preferences that contradict the user's explicit tech stack choice
- Keep preference section concise (max 5 items) to avoid bloating CLAUDE.md

### Relevant Patterns
- Current lesson injection pattern at orchestrator line 689-707 (follow same try/except structure)
- MemoryEngine delegation pattern (bridge.get_X → memory.get_X)

## Implementation Blueprint

### Tasks

#### Task 1: Inject preferences into _generate_claude_md()
**Files:** `agent/orchestrator.py`
**Pseudocode:**
```python
# After lessons_section and gotchas_section (line ~707)
preferences_section = ""
try:
    memory = _get_memory_engine()
    if memory:
        active_prefs = memory.get_active_preferences()
        if active_prefs:
            preferences_section = "\n## Team Preferences\n\n"
            for pref in active_prefs[:5]:
                status_badge = "[approved]" if pref.status == "approved" else f"[{pref.confidence:.0%}]"
                preferences_section += f"- {status_badge} {pref.content}\n"
except Exception:
    pass

# Add to claude_md template string (after gotchas_section)
```

#### Task 2: Inject preferences into _generate_prd()
**Files:** `agent/orchestrator.py`
**Depends on:** Task 1
**Pseudocode:**
```python
# After lessons_section (line ~856)
preferences_context = ""
try:
    memory = _get_memory_engine()
    if memory:
        active_prefs = memory.get_active_preferences()
        tech_prefs = [p for p in active_prefs if p.preference_type == "tech_stack"]
        if tech_prefs:
            preferences_context = "\n## Team Technology Preferences\n\n"
            for pref in tech_prefs[:3]:
                preferences_context += f"- {pref.content} (from: {pref.source_project})\n"
except Exception:
    pass

# Add to prd template string
```

#### Task 3: Surface preferences in discovery_node()
**Files:** `agent/orchestrator.py`
**Depends on:** Task 1
**Pseudocode:**
```python
# In discovery_node, after similar project lessons (line ~356)
# Add preference hints to discovery summary
memory = _get_memory_engine()
if memory:
    prefs = memory.get_active_preferences()
    if prefs:
        # Add to context for next discovery questions
        pref_hints = [f"Team preference: {p.content}" for p in prefs[:3]]
        # Inject into discovery context
```

### Integration Points
- **Connects to:** MemoryEngine (existing), preferences.json (existing)
- **Called by:** Orchestrator artifact generation pipeline
- **Depends on:** Memory Engine initialization (Level 1)

## Validation Loop

### Level 1: Syntax & Style
```bash
.venv/Scripts/python.exe -c "
import py_compile
py_compile.compile('agent/orchestrator.py', doraise=True)
print('Syntax OK')
"
```

### Level 2: Type Safety
```bash
.venv/Scripts/python.exe -c "
from agent.orchestrator import Orchestrator
print('Orchestrator imports OK')
"
```

### Level 3: Unit Tests
```bash
.venv/Scripts/python.exe -c "
from agent.engines.memory_engine import MemoryEngine, LearnedPreference

# Test preference filtering
engine = MemoryEngine()
engine._initialized = True
engine._preferences = [
    LearnedPreference(content='Use Supabase', confidence=0.9, status='pending'),
    LearnedPreference(content='Use Next.js', confidence=0.5, status='pending'),
    LearnedPreference(content='Use Tailwind', confidence=0.7, status='approved'),
]
active = engine.get_active_preferences()
assert len(active) == 2  # Supabase (>=0.8) + Tailwind (approved)
print(f'Active preferences: {len(active)} — correct!')
"
```

### Level 5: Build Verification
```bash
.venv/Scripts/python.exe -c "from mcp_server.playbook_mcp import mcp; print('MCP import OK')"
```

## Final Validation Checklist
- [ ] CLAUDE.md generation includes Team Preferences section
- [ ] PRD generation includes tech preferences context
- [ ] Discovery phase surfaces applicable preferences
- [ ] Empty preferences = no section (no empty headers)
- [ ] No crashes when preferences file doesn't exist

## Anti-Patterns
- Do NOT inject preferences that override user's explicit choices
- Do NOT show rejected preferences in artifacts
- Do NOT add more than 5 preferences to any section (keep concise)
- Do NOT make preferences mandatory — they're suggestions, not rules
- Do NOT duplicate preference content that's already in lessons section
