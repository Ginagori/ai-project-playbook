# PRP Template — Project Requirements Plan

## Overview

PRP (Project Requirements Plan) is an enhanced planning format that bridges the gap between a PRD (what to build) and implementation (how to build it). It's designed for agent-to-agent communication — clear enough for an AI to execute without ambiguity.

## Template

```markdown
# PRP: [Feature Name]

## Goal
[One sentence: what this feature does and why it matters]

## Why
[Business justification — why build this now]

## What
[Detailed description of the feature behavior]

## Success Criteria
- [ ] [Measurable outcome 1]
- [ ] [Measurable outcome 2]
- [ ] [Measurable outcome 3]

## Context

### Must-Read Files
- `path/to/relevant/file.py` — [why this file matters]
- `path/to/another/file.ts` — [what to understand from it]

### Codebase Context
- [Key architectural decisions that affect this feature]
- [Existing patterns to follow]
- [Dependencies this feature has]

### Known Gotchas
- [Common mistake 1 and how to avoid it]
- [Edge case that's easy to miss]
- [Performance concern to watch for]

### Relevant Patterns
- [Pattern from CLAUDE.md to apply]
- [Similar feature in codebase to reference]

## Implementation Blueprint

### Data Models
```python
class YourModel(BaseModel):
    """Pseudocode for the data model."""
    field_name: type  # Description
```

### Tasks

#### Task 1: [Name]
**Files:** `src/path/to/file.py`
**Pseudocode:**
```python
# 1. Load dependencies
# 2. Implement core logic
# 3. Handle errors
# 4. Return result
```

#### Task 2: [Name]
**Files:** `src/path/to/another_file.py`
**Depends on:** Task 1
**Pseudocode:**
```python
# Steps...
```

### Integration Points
- **Connects to:** [database, auth service, external API]
- **Called by:** [which endpoints/components use this]
- **Depends on:** [what must exist first]

## Validation Loop

### Level 1: Syntax & Style
```bash
ruff check src/ --fix
ruff format src/
```

### Level 2: Type Safety
```bash
mypy src/ --ignore-missing-imports
```

### Level 3: Unit Tests
```bash
pytest tests/unit/ -v --tb=short
```

### Level 4: Integration Tests
```bash
pytest tests/integration/ -v --tb=short
```

### Level 5: Build Verification
```bash
python -c "from src.main import app; print('OK')"
```

## Final Validation Checklist
- [ ] All tasks completed (no TODOs in code)
- [ ] All validation levels pass
- [ ] Integration points tested
- [ ] Error paths covered
- [ ] Documentation updated

## Anti-Patterns
- Do NOT leave placeholder code or TODOs
- Do NOT skip error handling at API boundaries
- Do NOT hardcode configuration values
- Do NOT commit secrets or environment variables
- Do NOT ignore type safety for "speed"
```

## Usage

### With the Playbook Agent

```
# Get PRP for a specific feature
playbook_get_prp session_id="abc123" feature_name="Authentication"

# Get PRP overview for all features
playbook_get_prp session_id="abc123"
```

### Manually

1. Copy this template
2. Fill in each section based on your PRD and CLAUDE.md
3. Have an AI review it for completeness
4. Use `playbook_evaluate_artifact artifact_type="plan" content="..."` to check quality

## Why PRP Over Just a PRD?

| Aspect | PRD | PRP |
|--------|-----|-----|
| **Audience** | Humans (product team) | AI agents + humans |
| **Level** | What to build | How to build it |
| **Specificity** | Features and requirements | Files, pseudocode, commands |
| **Validation** | Success criteria | Validation pyramid (5 levels) |
| **Ambiguity** | Some acceptable | Zero tolerance |
| **Integration** | Standalone | References CLAUDE.md, codebase |

## Key Principles

1. **Zero ambiguity** — Every task has specific files and pseudocode
2. **Validation at every level** — From syntax to integration
3. **Context-rich** — References to existing code, patterns, gotchas
4. **Agent-to-agent** — One AI writes the PRP, another executes it
5. **Anti-patterns included** — Explicitly state what NOT to do
