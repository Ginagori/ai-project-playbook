# PRP: PRP Template Compliance

## Goal
Rewrite `PRPBuilder.build_feature_prp()` to load the official PRP template from disk via `TemplateLoader` and inject lessons/gotchas from `MemoryBridge`, producing PRPs that follow the exact template structure instead of an improvised one.

## Why
The current `PRPBuilder` (1153 lines) generates PRPs with its own format that drifts from the official template at `playbook/templates/prp-template.md`:
- Missing "Codebase Context" subsection under Context
- Missing "Final Validation Checklist" section
- Missing "Data Models" subsection under Implementation Blueprint
- "Known Gotchas" is hardcoded (5 generic items) instead of project-specific
- No lessons from MemoryBridge are ever injected
- The section order doesn't match the template

After this PRP, every generated PRP will have the exact structure: Goal > Why > What > Success Criteria > Context (Must-Read Files, Codebase Context, Known Gotchas, Relevant Patterns) > Implementation Blueprint (Data Models, Tasks, Integration Points) > Validation Loop (5 levels) > Final Validation Checklist > Anti-Patterns — with domain-specific gotchas and lessons injected.

## What
Modify `PRPBuilder.build_feature_prp()` to:
1. Load the PRP template structure via `TemplateLoader` to know the expected sections and order
2. Query `MemoryBridge` for gotchas relevant to the feature's tech stack and project type
3. Query `MemoryBridge` for architecture patterns relevant to the feature
4. Add "Codebase Context" subsection from CLAUDE.md architecture + discovery_context
5. Add "Data Models" subsection in Implementation Blueprint
6. Add "Final Validation Checklist" section
7. Replace generic gotchas with project-specific ones from lessons
8. Keep backward compatibility — if TemplateLoader/MemoryBridge unavailable, fall back to current behavior

## Success Criteria
- [ ] Generated PRP has all sections defined in `playbook/templates/prp-template.md`
- [ ] Generated PRP includes "Codebase Context" subsection with architectural decisions
- [ ] Generated PRP includes "Data Models" subsection with Pydantic pseudocode
- [ ] Generated PRP includes "Final Validation Checklist" section
- [ ] Known Gotchas are project-specific (from MemoryBridge) when lessons exist
- [ ] Section order matches the template: Goal → Why → What → Success Criteria → Context → Implementation Blueprint → Validation Loop → Final Validation Checklist → Anti-Patterns
- [ ] Backward compatible: if no lessons exist, generic gotchas are still present

## Context

### Must-Read Files
- `agent/prp_builder.py:795-875` — current `build_feature_prp()` method to rewrite
- `agent/prp_builder.py:1-86` — markdown parsing helpers (reusable)
- `agent/prp_builder.py:335-389` — `_compute_file_paths()` (keep)
- `agent/prp_builder.py:394-681` — `_generate_pseudocode()` (keep)
- `agent/prp_builder.py:687-746` — `_build_validation_commands()` (keep)
- `agent/prp_builder.py:752-789` — `_determine_integration_points()` (keep)
- `playbook/templates/prp-template.md` — the official template structure (160 lines)
- `agent/template_loader.py` — TemplateLoader (from PRP 01)
- `agent/memory_bridge.py` — MemoryBridge (from PRP 02)
- `agent/models/project.py` — ProjectState with `discovery_context`

### Codebase Context
- `PRPBuilder.__init__()` parses PRD and CLAUDE.md into sections at construction time
- Helper methods `_find_requirements_for_feature()`, `_find_success_criteria_for_feature()`, `_find_relevant_patterns()` already extract context — these should be kept and augmented
- The `_generate_pseudocode()` method is 287 lines of tech-specific code generation — do NOT touch it, just call it
- `build_execution_package()` calls `build_feature_prp()` for each feature — the execution package benefits automatically from template compliance

### Known Gotchas
- The PRP template has code fences inside its markdown code block — `TemplateLoader` must handle nested fences (PRP 01 already addresses this)
- `build_feature_prp()` is called inside a loop by `build_execution_package()` — keep it fast, don't query MemoryBridge per-feature; query once in `__init__` and cache
- The template has `[BRACKET]` placeholders — these MUST be replaced with real content, never left as-is in output
- Don't make PRPs too long — the template defines the structure, but not every section needs to be verbose. Data Models can be 5-10 lines.

### Relevant Patterns
- The existing `build_feature_prp()` already assembles sections with f-strings — extend, don't replace
- `PRPBuilder.__init__()` caches parsed sections — add MemoryBridge queries there too
- PRP 04 (Enriched Planning) follows the same pattern: query MemoryBridge in the generator, inject as sections

## Implementation Blueprint

### Tasks

#### Task 1: Cache MemoryBridge data in `__init__`
**Files:** `agent/prp_builder.py`
**Pseudocode:**
```python
class PRPBuilder:
    def __init__(self, project: ProjectState):
        # ... existing init code ...

        # NEW: Cache lessons from MemoryBridge
        self._cached_gotchas: list[str] = []
        self._cached_arch_lessons: list = []
        self._cached_patterns: list = []
        try:
            from agent.memory_bridge import MemoryBridge
            bridge = MemoryBridge.get_instance()
            tech_list = [t for t in [self.tech_stack.frontend, self.tech_stack.backend, self.tech_stack.database] if t]
            pt_value = project.project_type.value if project.project_type else "saas"

            self._cached_gotchas = bridge.get_gotchas(pt_value, tech_list)
            self._cached_arch_lessons = bridge.get_architecture_lessons(pt_value)
            self._cached_patterns = bridge.get_patterns_for_feature(pt_value, tech_list)
        except Exception:
            pass  # Fall back to empty — backward compatible
```

#### Task 2: Add `_build_codebase_context()` method
**Files:** `agent/prp_builder.py`
**Pseudocode:**
```python
def _build_codebase_context(self, feature: Feature) -> str:
    """Build Codebase Context subsection from CLAUDE.md + discovery_context."""
    lines = []

    # Architecture from CLAUDE.md
    if self.architecture_pattern:
        lines.append(f"- **Architecture:** {self.architecture_pattern[:200]}")

    # Discovery context
    if self.project.discovery_context:
        domain = self.project.discovery_context.get("domain", "")
        if domain:
            lines.append(f"- **Domain:** {domain}")
        regulations = self.project.discovery_context.get("regulations", "")
        if regulations:
            lines.append(f"- **Regulatory:** {regulations}")

    # Arch lessons from MemoryBridge
    if self._cached_arch_lessons:
        for lesson in self._cached_arch_lessons[:2]:
            lines.append(f"- **Learned:** {lesson.title} — {lesson.recommendation}")

    if not lines:
        lines.append("- Follow patterns defined in CLAUDE.md")

    return "\n".join(lines)
```

#### Task 3: Add `_build_data_models_section()` method
**Files:** `agent/prp_builder.py`
**Pseudocode:**
```python
def _build_data_models_section(self, feature: Feature) -> str:
    """Build Data Models subsection for Implementation Blueprint."""
    slug = feature.name.lower().replace(" ", "_").replace("-", "_")
    class_name = feature.name.replace(" ", "").replace("-", "")

    if self.is_python:
        return f"""```python
class {class_name}(BaseModel):
    \"\"\"Data model for {feature.name}.\"\"\"
    id: UUID
    # Add fields based on PRD requirements
    created_at: datetime
    updated_at: datetime
```"""
    else:
        return f"""```typescript
interface {class_name} {{
  id: string;
  // Add fields based on PRD requirements
  createdAt: Date;
  updatedAt: Date;
}}
```"""
```

#### Task 4: Add `_build_gotchas_section()` method
**Files:** `agent/prp_builder.py`
**Pseudocode:**
```python
def _build_gotchas_section(self, feature: Feature) -> str:
    """Build Known Gotchas from MemoryBridge + defaults."""
    gotchas = []

    # Add project-specific gotchas from MemoryBridge
    if self._cached_gotchas:
        gotchas.extend(self._cached_gotchas[:3])

    # Add feature-specific gotchas from patterns
    for pattern in self._cached_patterns:
        if hasattr(pattern, 'recommendation'):
            gotchas.append(f"- {pattern.title}: {pattern.recommendation}")

    # Always include baseline gotchas
    defaults = [
        "- Do NOT leave TODOs or placeholder code",
        "- Do NOT skip error handling at API boundaries",
        "- Do NOT hardcode configuration values (use environment variables)",
    ]

    # Combine, deduplicate, limit to 6
    all_gotchas = gotchas + [d for d in defaults if d not in gotchas]
    return "\n".join(all_gotchas[:6])
```

#### Task 5: Add `_build_final_validation_checklist()` method
**Files:** `agent/prp_builder.py`
**Pseudocode:**
```python
def _build_final_validation_checklist(self, feature: Feature) -> str:
    """Build Final Validation Checklist section."""
    return f"""## Final Validation Checklist
- [ ] All tasks completed (no TODOs in code)
- [ ] All validation levels pass (syntax, types, unit, integration, build)
- [ ] Integration points tested with dependent features
- [ ] Error paths covered (not just happy path)
- [ ] {feature.name} is fully functional end-to-end"""
```

#### Task 6: Rewrite `build_feature_prp()` to follow template order
**Files:** `agent/prp_builder.py`
**Depends on:** Tasks 1-5
**Pseudocode:**
```python
def build_feature_prp(self, feature: Feature) -> str:
    """Build a complete PRP following the official template structure."""
    requirements = self._find_requirements_for_feature(feature)
    criteria = self._find_success_criteria_for_feature(feature)
    file_paths = self._compute_file_paths(feature)
    pseudocode = self._generate_pseudocode(feature, requirements)
    validation = self._build_validation_commands(feature)
    integration = self._determine_integration_points(feature)
    patterns = self._find_relevant_patterns(feature)

    # NEW sections
    codebase_context = self._build_codebase_context(feature)
    data_models = self._build_data_models_section(feature)
    gotchas = self._build_gotchas_section(feature)
    final_checklist = self._build_final_validation_checklist(feature)

    # Build helpers
    depends_str = f"\n**Depends on:** {', '.join(feature.depends_on)}\n" if feature.depends_on else ""
    files_create = "\n".join(f"- `{f}`" for f in file_paths["create"]) or "- (determined during implementation)"
    files_modify = "\n".join(f"- `{f}`" for f in file_paths["modify"]) if file_paths["modify"] else ""
    reqs_list = "\n".join(f"- {r}" for r in requirements)
    criteria_list = "\n".join(f"- [ ] {c}" for c in criteria)

    # Assemble following EXACT template order
    prp = f"""# PRP: {feature.name}

## Goal
{feature.description}
{depends_str}
## Why
Required for the project: {self.project.objective}. Priority: **{feature.priority.upper()}**.

## What
{reqs_list}

## Success Criteria
{criteria_list}

## Context

### Must-Read Files
{files_modify}
- `CLAUDE.md` — Project rules, architecture pattern, code style
- `docs/PRD.md` — Full product requirements

### Codebase Context
{codebase_context}

### Known Gotchas
{gotchas}

### Relevant Patterns
{patterns}

## Implementation Blueprint

### Data Models
{data_models}

### Tasks

#### Task 1: Implement {feature.name}
**Files:** {', '.join(f'`{f}`' for f in file_paths["create"][:3]) or '(see Files to Create)'}
**Pseudocode:**
{pseudocode}

### Files to Create
{files_create}

### Files to Modify
{files_modify if files_modify else "- (none for this feature)"}

### Integration Points
{integration}

{validation}

{final_checklist}

## Anti-Patterns
- Do NOT leave placeholder code or TODOs
- Do NOT skip tests for "simple" features
- Do NOT hardcode configuration values
- Do NOT commit secrets or environment variables
- Do NOT ignore type safety for "speed"
- Do NOT create files outside the defined architecture structure
"""
    return prp
```

### Integration Points
- **Depends on:** PRP 01 (Template Loader for structure awareness), PRP 02 (Memory Bridge for lessons/gotchas)
- **Modifies:** `agent/prp_builder.py`
- **Consumed by:** `agent/orchestrator.py` implementation_node → PRPBuilder
- **Consumed by:** `agent/handoff.py` → writes PRPs to disk
- **Consumed by:** `playbook_get_prp` and `playbook_execution_package` MCP tools

## Validation Loop

### Level 1: Syntax & Style
```bash
ruff check agent/prp_builder.py --fix
ruff format agent/prp_builder.py
```

### Level 2: Type Safety
```bash
mypy agent/prp_builder.py --ignore-missing-imports
```

### Level 3: Unit Tests
```bash
.venv/Scripts/python.exe -c "
from agent.prp_builder import PRPBuilder
from agent.models.project import ProjectState, TechStack, ProjectType, ScalePhase, Feature

# Create a test project
project = ProjectState(
    id='test-prp-compliance',
    objective='Build a workplace safety SaaS',
    project_type=ProjectType.SAAS,
    scale=ScalePhase.MVP,
    tech_stack=TechStack(frontend='nextjs', backend='fastapi', database='postgresql-supabase'),
    features=[
        Feature(name='Authentication', description='User signup, login, logout with JWT'),
        Feature(name='Dashboard', description='Main dashboard with metrics'),
    ],
    claude_md='# Test CLAUDE.md\n## Architecture\nMonolith with clean layers',
    prd='# PRD\n## Core Features\n- Authentication\n- Dashboard',
    discovery_context={'domain': 'occupational health', 'regulations': 'Decreto 1072/2015'},
)

builder = PRPBuilder(project)

# Test PRP generation
prp = builder.build_feature_prp(project.features[0])

# Verify template compliance
assert '## Goal' in prp
assert '## Why' in prp
assert '## What' in prp  # NOT 'What (Requirements from PRD)'
assert '## Success Criteria' in prp
assert '### Must-Read Files' in prp
assert '### Codebase Context' in prp  # NEW
assert '### Known Gotchas' in prp
assert '### Relevant Patterns' in prp
assert '### Data Models' in prp  # NEW
assert '## Final Validation Checklist' in prp  # NEW
assert '## Anti-Patterns' in prp
assert '[BRACKET]' not in prp  # No template placeholders

print(f'PRP length: {len(prp)} chars, {len(prp.splitlines())} lines')
print('All PRP template compliance tests passed!')
"
```

### Level 5: Build Verification
```bash
.venv/Scripts/python.exe -c "from agent.prp_builder import PRPBuilder; print('Import OK')"
```

## Final Validation Checklist
- [ ] Generated PRP follows exact template section order
- [ ] "Codebase Context" subsection present and populated
- [ ] "Data Models" subsection present with pseudocode
- [ ] "Final Validation Checklist" section present
- [ ] Known Gotchas are from MemoryBridge when lessons exist
- [ ] No `[BRACKET]` placeholders left in output
- [ ] Backward compatible when MemoryBridge returns empty
- [ ] `build_execution_package()` still works (calls `build_feature_prp()` internally)

## Anti-Patterns
- Do NOT change the pseudocode generation methods (`_python_pseudocode`, `_node_pseudocode`) — they work fine
- Do NOT query MemoryBridge inside `build_feature_prp()` — cache in `__init__` for performance
- Do NOT make all sections verbose — keep PRPs actionable, not bloated
- Do NOT lose existing pattern matching from CLAUDE.md — `_find_relevant_patterns()` should augment, not replace
- Do NOT break `build_execution_package()` — it depends on `build_feature_prp()` output format
