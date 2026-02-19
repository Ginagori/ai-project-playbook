# PRP: Enriched Planning (CLAUDE.md + PRD)

## Goal
Rewrite `_generate_claude_md()` and `_generate_prd()` to use templates from disk + lessons from MemoryBridge, producing domain-specific artifacts instead of generic hardcoded ones.

## Why
The current generators produce the same output regardless of domain:
- `_generate_claude_md()` (line 320-501): 4 hardcoded templates → ~50-line CLAUDE.md
- `_generate_prd()` (line 504-596): 4 hardcoded feature lists → ~30-line PRD
- Meanwhile, `playbook/templates/prd-template.md` has 655 lines with personas, OKRs, user journeys, security, rollout plans
- Lessons from Supabase (domain-specific gotchas, architecture patterns, regulatory requirements) are never consulted

After this PRP, a Colombian SST SaaS will get a CLAUDE.md mentioning Decreto 1072/2015 and RLS by organization_id, and a PRD with worker health modules — because those patterns exist in the team's lesson history.

## What
Rewrite `planning_node()` and its helper functions to:
1. Load the PRD template structure from `TemplateLoader`
2. Query `MemoryBridge` for relevant lessons, gotchas, and architecture patterns
3. Use `discovery_context` (from PRP 03) for domain-specific content
4. Generate CLAUDE.md with template structure + injected lessons
5. Generate PRD with template structure + injected lessons
6. Keep backward compatibility — if templates/lessons unavailable, fall back to current behavior

## Success Criteria
- [ ] Generated CLAUDE.md includes architecture lessons from MemoryBridge (if any exist)
- [ ] Generated CLAUDE.md includes gotchas from past projects in a "Known Gotchas" section
- [ ] Generated PRD follows the template structure more closely (at minimum: Executive Summary, Users & Personas, Requirements with P0/P1/P2, Success Metrics, Technical Architecture, Security)
- [ ] `discovery_context["domain"]` is used to customize feature descriptions
- [ ] Generated PRD is at least 2x longer than current (~60+ lines vs current ~30)
- [ ] Backward compatible: if MemoryBridge returns no lessons, output is still valid

## Context

### Must-Read Files
- `agent/orchestrator.py:236-596` — current `planning_node()`, `_generate_claude_md()`, `_generate_prd()`
- `agent/template_loader.py` — TemplateLoader (from PRP 01)
- `agent/memory_bridge.py` — MemoryBridge (from PRP 02)
- `playbook/templates/prd-template.md` — the 655-line PRD template structure
- `agent/models/project.py` — `ProjectState` with `discovery_context`

### Codebase Context
- `planning_node()` calls `_generate_claude_md()` and `_generate_prd()`, runs evaluators, stores results
- The evaluator (`ArtifactEvaluator`) checks for required sections — enriched artifacts should score higher
- `discovery_context` has keys: "domain", "regulations", "target_users", "similar_projects", etc.

### Known Gotchas
- The PRD template has 12 major sections — don't try to fill ALL of them. Focus on: Executive Summary, Requirements (P0/P1/P2), Success Criteria, Technical Architecture, Security
- Keep the CLAUDE.md concise — it goes into every Claude Code context window. More than 200 lines is counterproductive.
- Template sections that have `[BRACKET]` placeholders need to be replaced with real content, not left as-is
- Don't lose the existing project-type-specific content (architecture patterns per type) — augment, don't replace

### Relevant Patterns
- The existing `_generate_claude_md()` structure (principles, tech stack, architecture, code style, testing) should remain the skeleton
- Lessons should be injected as additional sections, not replace existing ones

## Implementation Blueprint

### Files to Modify
- `agent/orchestrator.py` — rewrite `_generate_claude_md()`, `_generate_prd()`, modify `planning_node()`

### Tasks

#### Task 1: Enrich `_generate_claude_md()` with lessons
**Files:** `agent/orchestrator.py`
**Pseudocode:**
```python
def _generate_claude_md(project: ProjectState) -> str:
    """Generate CLAUDE.md with template structure + lessons from memory."""
    ts = project.tech_stack
    pt = project.project_type

    # --- Existing content generation (keep as-is) ---
    principles = """..."""  # existing
    arch_section = _get_arch_section(pt)  # existing logic, extracted
    extra_patterns = _get_extra_patterns(pt)  # existing logic, extracted

    # --- NEW: Query lessons from MemoryBridge ---
    from agent.memory_bridge import MemoryBridge
    bridge = MemoryBridge.get_instance()
    tech_stack_list = [t for t in [ts.frontend, ts.backend, ts.database] if t]
    pt_value = pt.value if pt else "saas"

    arch_lessons = bridge.get_architecture_lessons(pt_value)
    gotchas = bridge.get_gotchas(pt_value, tech_stack_list)

    # --- NEW: Domain context from discovery ---
    domain_section = ""
    if project.discovery_context:
        domain = project.discovery_context.get("domain", "")
        regulations = project.discovery_context.get("regulations", "")
        if domain:
            domain_section = f"\n## Domain: {domain}\n"
        if regulations:
            domain_section += f"\n### Regulatory Requirements\n- {regulations}\n"

    # --- NEW: Lessons-based sections ---
    lessons_section = ""
    if arch_lessons:
        lessons_section = "\n## Learned Patterns (from past projects)\n\n"
        for l in arch_lessons[:3]:
            lessons_section += f"- **{l.title}**: {l.recommendation}\n"

    gotchas_section = ""
    if gotchas:
        gotchas_section = "\n## Known Gotchas\n\n" + "\n".join(gotchas) + "\n"

    # --- Assemble ---
    claude_md = f"""# {project.objective}
{domain_section}
## Core Principles

{principles}

## Tech Stack

- **Frontend**: {ts.frontend or "N/A"}
- **Backend**: {ts.backend or "N/A"}
- **Database**: {ts.database or "N/A"}
- **Package Manager**: {pkg_manager}
- **Testing**: {test_framework}

## Architecture

{arch_section}

## Code Style
...

## Testing
...

## Common Patterns
{extra_patterns}
{lessons_section}
{gotchas_section}"""

    return claude_md
```

#### Task 2: Enrich `_generate_prd()` with template structure + lessons
**Files:** `agent/orchestrator.py`
**Pseudocode:**
```python
def _generate_prd(project: ProjectState) -> str:
    """Generate PRD using template structure + lessons from memory."""
    ts = project.tech_stack
    pt = project.project_type

    # --- Existing feature generation (keep) ---
    core_features = _get_core_features(pt)  # extract existing logic
    nice_to_have = _get_nice_to_have(pt)    # extract existing logic

    # --- NEW: Query lessons ---
    from agent.memory_bridge import MemoryBridge
    bridge = MemoryBridge.get_instance()
    tech_stack_list = [t for t in [ts.frontend, ts.backend, ts.database] if t]
    pt_value = pt.value if pt else "saas"

    all_lessons = bridge.get_relevant_lessons(pt_value, tech_stack_list, phase="planning")
    gotchas = bridge.get_gotchas(pt_value, tech_stack_list)

    # --- NEW: Domain-specific requirements from discovery_context ---
    domain = project.discovery_context.get("domain", "")
    target_users = project.discovery_context.get("target_users", "")
    regulations = project.discovery_context.get("regulations", "")

    users_section = ""
    if target_users:
        users_section = f"""
## Users & Personas

### Primary Users
{target_users}
"""

    security_section = f"""
## Security Considerations

- Validate all user inputs at API boundary
- Use atomic database operations for concurrent access
- Never commit environment variables to git
- Test error paths, not just happy paths
"""
    if regulations:
        security_section += f"- **Regulatory Compliance**: {regulations}\n"

    # --- NEW: Gotchas from lessons ---
    gotchas_section = ""
    if gotchas:
        gotchas_section = "\n## Known Gotchas (from past projects)\n\n"
        gotchas_section += "\n".join(gotchas) + "\n"

    lessons_section = ""
    if all_lessons:
        lessons_section = "\n## Lessons from Similar Projects\n\n"
        for l in all_lessons[:5]:
            lessons_section += f"- **{l.title}**: {l.recommendation}\n"

    # --- Assemble enriched PRD ---
    prd = f"""# Product Requirements Document

## Executive Summary

**Product**: {project.objective}
**Type**: {pt.value if pt else "Application"}
**Target Scale**: {project.scale.value}
{f"**Domain**: {domain}" if domain else ""}

## Mission

Build a {pt.value if pt else "application"} that {project.objective}.
{users_section}
## MVP Scope

### Core Features (P0)
{core_features}

### Nice-to-Have (P1)
{nice_to_have}

## Success Criteria

- [ ] Users can complete core workflow end-to-end
- [ ] System handles expected load for {project.scale.value} phase
- [ ] All critical paths have test coverage (>80%)
- [ ] Deployment pipeline working
- [ ] API documentation complete (OpenAPI)

## Technical Architecture

- Frontend: {ts.frontend or "N/A"}
- Backend: {ts.backend or "N/A"}
- Database: {ts.database or "N/A"}
{security_section}
{gotchas_section}
{lessons_section}"""

    return prd
```

#### Task 3: Modify `planning_node()` to wire it together
**Files:** `agent/orchestrator.py`
**Pseudocode:**
```python
def planning_node(state: OrchestratorState) -> OrchestratorState:
    # ... existing evaluator setup ...

    # Configure MemoryBridge if not already done
    from agent.memory_bridge import MemoryBridge
    bridge = MemoryBridge.get_instance()
    # (Supabase config happens at MCP server startup)

    # Generate enriched artifacts
    claude_md = _generate_claude_md(project)
    prd = _generate_prd(project)

    # ... rest is same (evaluate, store, output) ...
```

### Integration Points
- **Depends on:** PRP 01 (Template Loader), PRP 02 (Memory Bridge), PRP 03 (Smart Discovery for discovery_context)
- **Modifies:** `agent/orchestrator.py`
- **Consumed by:** PRP 05 (PRP Template Compliance), PRP 06 (Experience Roadmap)
- **Consumed by:** `agent/evals/` — enriched artifacts should score higher

## Validation Loop

### Level 1: Syntax & Style
```bash
ruff check agent/orchestrator.py --fix
ruff format agent/orchestrator.py
```

### Level 2: Type Safety
```bash
mypy agent/orchestrator.py --ignore-missing-imports
```

### Level 3: Unit Tests
```bash
.venv/Scripts/python.exe -c "
from agent.orchestrator import _generate_claude_md, _generate_prd
from agent.models.project import ProjectState, TechStack, ProjectType, ScalePhase

# Create a test project with discovery context
project = ProjectState(
    id='test-enriched',
    objective='Build a workplace safety SaaS for Colombia',
    project_type=ProjectType.SAAS,
    scale=ScalePhase.MVP,
    tech_stack=TechStack(frontend='nextjs', backend='fastapi', database='postgresql-supabase'),
    discovery_context={'domain': 'occupational health and safety', 'regulations': 'Decreto 1072/2015, Resolución 0312/2019'},
)

# Test CLAUDE.md generation
claude_md = _generate_claude_md(project)
assert 'Core Principles' in claude_md
assert 'Tech Stack' in claude_md
# Domain should be present if discovery_context provided
print(f'CLAUDE.md length: {len(claude_md)} chars')
print(f'Has domain: {\"Domain\" in claude_md or \"occupational\" in claude_md.lower()}')

# Test PRD generation
prd = _generate_prd(project)
assert 'Executive Summary' in prd
assert 'Core Features' in prd
assert 'Security' in prd
print(f'PRD length: {len(prd)} chars')

print('All enriched planning tests passed!')
"
```

### Level 5: Build Verification
```bash
.venv/Scripts/python.exe -c "from agent.orchestrator import planning_node; print('Import OK')"
```

## Final Validation Checklist
- [ ] CLAUDE.md includes lessons from MemoryBridge (when available)
- [ ] CLAUDE.md includes domain context from discovery_context (when available)
- [ ] PRD includes Security section
- [ ] PRD includes domain-specific content (when available)
- [ ] PRD is longer than before (~60+ lines vs ~30)
- [ ] Evaluator scores are same or better than before
- [ ] Falls back gracefully when no lessons/context available

## Anti-Patterns
- Do NOT replace existing content — augment it
- Do NOT make CLAUDE.md too long (>200 lines is counterproductive)
- Do NOT leave `[BRACKET]` placeholders from templates in output
- Do NOT make MemoryBridge queries blocking — wrap in try/except
