# PRP: Experience-Informed Roadmap

## Goal
Rewrite `roadmap_node()` to query `MemoryBridge` for patterns from past projects and use `discovery_context` to generate domain-specific feature breakdowns instead of hardcoded feature lists.

## Why
The current `roadmap_node()` (lines 599-698) has 5 hardcoded feature lists — one per ProjectType. Every SaaS gets the same 7 features, every agent gets the same 5. This ignores:
- **Domain knowledge**: A Colombian SST SaaS needs "Gestión Documental" and "Matriz de Riesgos GTC-45" — the generic list has "Dashboard" and "API Endpoints"
- **Past project patterns**: NOVA, KOMPLIA, and KidSpark all needed Triple-Layer Soul + 4 Engines — but the agent feature list doesn't suggest this architecture
- **Discovery context**: The user already told us their domain, regulations, and target users in Discovery — but roadmap_node() ignores all of it
- **Team experience**: If the team has built 3 SaaS projects with Supabase, the roadmap should include "Supabase Setup" instead of generic "Project Setup"

After this PRP, a SST SaaS will get features like "Worker Registry", "Risk Matrix (GTC-45)", "Document Management" — because the discovery_context says `domain: "occupational health and safety"` and MemoryBridge knows past SST projects.

## What
Modify `roadmap_node()` to:
1. Query `MemoryBridge` for successful feature patterns from similar projects
2. Use `discovery_context` domain/regulations to customize feature names and descriptions
3. Keep the hardcoded feature lists as **fallback defaults** (not primary source)
4. Add domain-specific features when discovery_context provides domain info
5. Inject learned patterns as additional features when MemoryBridge has relevant data
6. Preserve feature enrichment via `enrich_features_from_prd()` (it already works)

## Success Criteria
- [ ] `roadmap_node()` queries MemoryBridge for similar project patterns
- [ ] Feature breakdown includes domain-specific features when `discovery_context["domain"]` exists
- [ ] Feature descriptions reference domain terms (e.g., "worker health records" not "core data models")
- [ ] Hardcoded feature lists are still used as defaults when no context/lessons available
- [ ] Feature count is appropriate (5-10 features for MVP, not more)
- [ ] Feature dependencies are correctly computed (setup → auth → domain features → dashboard)
- [ ] Backward compatible: without discovery_context or lessons, output matches current behavior

## Context

### Must-Read Files
- `agent/orchestrator.py:599-698` — current `roadmap_node()` with 5 hardcoded feature lists
- `agent/models/project.py` — `Feature` model with name, description, status, depends_on, priority
- `agent/prp_builder.py:1076-1153` — `enrich_features_from_prd()` and `_compute_feature_dependencies()`
- `agent/memory_bridge.py` — MemoryBridge (from PRP 02)
- `agent/meta_learning/suggest.py` — `find_similar_projects()`, `get_recommendations()`

### Codebase Context
- `roadmap_node()` is a LangGraph node — it receives `OrchestratorState` and returns `OrchestratorState`
- After generating features, it calls `enrich_features_from_prd()` which adds PRD requirements and computes dependencies — this should still happen
- `auto_capture_phase_lesson("roadmap", project)` is called at the end — keep it
- `discovery_context` is a dict with keys: "domain", "regulations", "target_users", "similar_projects" (populated by PRP 03)
- The `Feature` model has: name, description, status, depends_on, priority, prd_requirements, success_criteria

### Known Gotchas
- Don't generate too many features — MVP should have 5-10, not 15. More features = more implementation time
- The `_compute_feature_dependencies()` function in `prp_builder.py` uses keyword matching — custom feature names must contain recognizable keywords ("auth", "model", "api", "dashboard") for dependencies to be detected
- `Feature.depends_on` is a list of feature *names* (strings) — dependency resolution is by name matching, not by ID
- Discovery context may be None or empty dict — always check before accessing

### Relevant Patterns
- `roadmap_node()` currently creates Feature objects with name + description — keep this pattern
- `enrich_features_from_prd()` adds prd_requirements and success_criteria after features are created — don't duplicate this
- The existing hardcoded lists are actually good *base templates* — augment them with domain-specific features, don't start from scratch

## Implementation Blueprint

### Tasks

#### Task 1: Add `_get_domain_features()` helper function
**Files:** `agent/orchestrator.py`
**Pseudocode:**
```python
def _get_domain_features(discovery_context: dict) -> list[Feature]:
    """Generate domain-specific features from discovery context."""
    domain = discovery_context.get("domain", "").lower()
    regulations = discovery_context.get("regulations", "")
    target_users = discovery_context.get("target_users", "")

    domain_features = []

    # Map known domains to features
    if "health" in domain or "safety" in domain or "sst" in domain or "sgsst" in domain:
        domain_features = [
            Feature(name="Worker Registry", description=f"Manage worker profiles, health records, and employment data"),
            Feature(name="Document Management", description=f"Upload, version, and manage compliance documents"),
            Feature(name="Risk Assessment", description=f"Risk matrix and hazard identification following GTC-45"),
        ]
        if regulations:
            domain_features.append(
                Feature(name="Compliance Tracking", description=f"Track compliance with {regulations}")
            )

    elif "education" in domain or "learning" in domain or "tutoring" in domain:
        domain_features = [
            Feature(name="Student Profiles", description="Manage student data, learning preferences, and progress"),
            Feature(name="Activity Engine", description="Generate and deliver personalized learning activities"),
            Feature(name="Progress Tracking", description="Track learning milestones, scores, and growth over time"),
        ]

    elif "ecommerce" in domain or "commerce" in domain or "shop" in domain:
        domain_features = [
            Feature(name="Product Catalog", description="Product listing, categories, search, and inventory"),
            Feature(name="Shopping Cart", description="Cart management with persistent state"),
            Feature(name="Checkout & Payments", description="Checkout flow with payment gateway integration"),
        ]

    # Generic domain features for unrecognized domains
    elif domain:
        domain_features = [
            Feature(name=f"{domain.title()} Core Module", description=f"Core functionality for {domain} domain"),
        ]

    return domain_features
```

#### Task 2: Add `_get_learned_features()` helper function
**Files:** `agent/orchestrator.py`
**Pseudocode:**
```python
def _get_learned_features(project_type: str, tech_stack: list[str]) -> list[Feature]:
    """Get feature suggestions from MemoryBridge based on past projects."""
    try:
        from agent.memory_bridge import MemoryBridge
        bridge = MemoryBridge.get_instance()

        # Get architecture patterns from past projects
        arch_lessons = bridge.get_architecture_lessons(project_type)

        features = []
        seen_names = set()

        for lesson in arch_lessons[:3]:  # Limit to top 3 lessons
            # Convert architecture lessons to feature suggestions
            if lesson.category.value == "architecture" and lesson.title not in seen_names:
                features.append(Feature(
                    name=lesson.title,
                    description=f"{lesson.recommendation} (learned from past projects)",
                ))
                seen_names.add(lesson.title)

        return features
    except Exception:
        return []
```

#### Task 3: Rewrite `roadmap_node()` to merge defaults + domain + learned features
**Files:** `agent/orchestrator.py`
**Depends on:** Tasks 1, 2
**Pseudocode:**
```python
def roadmap_node(state: OrchestratorState) -> OrchestratorState:
    """Handle Roadmap phase — context-aware feature breakdown."""
    project = state.project

    # Step 1: Get base features (existing hardcoded lists as defaults)
    if project.project_type == ProjectType.SAAS:
        base_features = [
            Feature(name="Project Setup", description="Initialize project with tech stack, create folder structure, configure tooling"),
            Feature(name="Authentication", description="Implement user signup, login, logout, password reset with JWT"),
            Feature(name="Core Data Models", description="Define database schema, create ORM models, implement CRUD operations"),
        ]
    elif project.project_type == ProjectType.AGENT:
        base_features = [
            Feature(name="Project Setup", description="Initialize project with agent framework, configure environment"),
            Feature(name="Agent Core", description="Create main agent with system prompt and configuration"),
            Feature(name="Tools", description="Implement agent tools for required functionality"),
        ]
    elif project.project_type == ProjectType.MULTI_AGENT:
        base_features = [
            Feature(name="Project Setup", description="Initialize project with LangGraph, configure environment"),
            Feature(name="Agent Registry", description="Create agent registry and factory pattern"),
            Feature(name="Orchestrator", description="Create supervisor/router for agent coordination"),
        ]
    elif project.project_type == ProjectType.PLATFORM:
        base_features = [
            Feature(name="Project Setup", description="Initialize project with monorepo structure, configure tooling"),
            Feature(name="Authentication", description="Implement user auth with role-based access"),
            Feature(name="Plugin Architecture", description="Create plugin registry and dynamic loading"),
        ]
    else:
        base_features = [
            Feature(name="Project Setup", description="Initialize project with tech stack"),
            Feature(name="Core Data Models", description="Define database schema, create ORM models"),
            Feature(name="API Endpoints", description="Create REST endpoints for core functionality"),
        ]

    # Step 2: Get domain-specific features from discovery_context
    domain_features = []
    if project.discovery_context:
        domain_features = _get_domain_features(project.discovery_context)

    # Step 3: Get learned features from MemoryBridge
    tech_list = [t for t in [project.tech_stack.frontend, project.tech_stack.backend, project.tech_stack.database] if t]
    pt_value = project.project_type.value if project.project_type else "saas"
    learned_features = _get_learned_features(pt_value, tech_list)

    # Step 4: Add closing features (always at the end)
    closing_features = []
    if project.project_type in (ProjectType.SAAS, ProjectType.PLATFORM):
        closing_features = [
            Feature(name="Dashboard", description="Create main dashboard with key metrics and navigation"),
            Feature(name="API Endpoints", description="Create REST endpoints for all modules"),
        ]
    elif project.project_type in (ProjectType.AGENT, ProjectType.MULTI_AGENT):
        closing_features = [
            Feature(name="API Interface", description="Create FastAPI endpoints to interact with agent system"),
        ]

    # Step 5: Merge — base + domain + learned + closing, deduplicate by name
    all_features = base_features + domain_features + learned_features + closing_features
    seen = set()
    features = []
    for f in all_features:
        if f.name not in seen:
            features.append(f)
            seen.add(f.name)

    # Cap at 10 features for MVP
    if len(features) > 10:
        features = features[:10]

    project.features = features

    # Enrich features with PRD context (requirements, criteria, dependencies)
    if project.prd:
        from agent.prp_builder import enrich_features_from_prd
        enrich_features_from_prd(
            project.features, project.prd,
            project_type=project.project_type.value if project.project_type else None,
        )

    project.current_phase = Phase.IMPLEMENTATION
    project.needs_user_input = True

    # Auto-capture roadmap lessons
    from agent.meta_learning.capture import auto_capture_phase_lesson
    auto_capture_phase_lesson("roadmap", project)

    # ... rest of output formatting (same as current) ...
```

### Integration Points
- **Depends on:** PRP 02 (Memory Bridge), PRP 03 (Smart Discovery for discovery_context)
- **Modifies:** `agent/orchestrator.py`
- **Consumed by:** `implementation_node()` — iterates over `project.features`
- **Consumed by:** `PRPBuilder` — generates PRPs for each feature
- **Consumed by:** `HandoffWriter` — writes per-feature PRPs to disk

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
from agent.orchestrator import _get_domain_features, _get_learned_features
from agent.models.project import Feature

# Test domain features for SST
sst_context = {'domain': 'occupational health and safety', 'regulations': 'Decreto 1072/2015'}
sst_features = _get_domain_features(sst_context)
assert len(sst_features) >= 3, f'Expected 3+ SST features, got {len(sst_features)}'
assert any('worker' in f.name.lower() or 'registry' in f.name.lower() for f in sst_features)
print(f'SST features: {[f.name for f in sst_features]}')

# Test domain features for education
edu_context = {'domain': 'education and tutoring'}
edu_features = _get_domain_features(edu_context)
assert len(edu_features) >= 2, f'Expected 2+ education features, got {len(edu_features)}'
print(f'Education features: {[f.name for f in edu_features]}')

# Test empty context (backward compatibility)
empty_features = _get_domain_features({})
assert len(empty_features) == 0, 'Empty context should produce no domain features'

# Test learned features (may be empty if no lessons exist)
learned = _get_learned_features('saas', ['nextjs', 'fastapi', 'supabase'])
print(f'Learned features: {[f.name for f in learned]}')

print('All roadmap tests passed!')
"
```

### Level 5: Build Verification
```bash
.venv/Scripts/python.exe -c "from agent.orchestrator import roadmap_node; print('Import OK')"
```

## Final Validation Checklist
- [ ] SST SaaS discovery_context produces domain-specific features (Worker Registry, etc.)
- [ ] Education discovery_context produces education features (Student Profiles, etc.)
- [ ] Empty discovery_context produces same features as before (backward compatible)
- [ ] Features list is capped at 10 for MVP
- [ ] Feature dependencies are correctly computed after merge
- [ ] `enrich_features_from_prd()` still runs after feature generation
- [ ] MemoryBridge failure doesn't crash roadmap_node
- [ ] `auto_capture_phase_lesson()` still runs at the end

## Anti-Patterns
- Do NOT remove the hardcoded feature lists entirely — they are the fallback defaults
- Do NOT generate more than 10 features for MVP — more features = more complexity = less likely to complete
- Do NOT create features with names that `_compute_feature_dependencies()` can't parse — use recognizable keywords
- Do NOT make MemoryBridge queries blocking or failure-critical — wrap in try/except
- Do NOT duplicate features — always check `seen` set before adding
- Do NOT add domain features that overlap with base features (e.g., don't add "User Auth" if "Authentication" already exists)
