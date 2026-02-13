"""
AI Project Playbook Orchestrator

LangGraph-based state machine that orchestrates the project lifecycle:
Discovery → Planning → Roadmap → Implementation → Deployment

Each phase is a node that processes user input and generates outputs.
"""

from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field

from agent.models.project import (
    ProjectState,
    Phase,
    AutonomyMode,
    ProjectType,
    ScalePhase,
    Feature,
)


class OrchestratorState(BaseModel):
    """
    State that flows through the LangGraph orchestrator.
    Extends ProjectState with orchestration-specific fields.
    """
    # Core project state
    project: ProjectState

    # Orchestration control
    user_input: str | None = None
    agent_output: str | None = None
    should_continue: bool = True
    error: str | None = None

    # Phase-specific counters
    discovery_question_index: int = 0

    class Config:
        arbitrary_types_allowed = True


# Discovery phase questions
DISCOVERY_QUESTIONS = [
    {
        "id": "project_type",
        "question": """**Question 1 of 5: What type of project is this?**

1. **SaaS Application** - Multi-tenant web app with users, subscriptions, etc.
2. **API Backend** - REST/GraphQL API for mobile apps or integrations
3. **Agent System** - Single AI agent with tools and memory
4. **Multi-Agent System** - Multiple AI agents working together
5. **Platform** - Complex multi-component system (marketplace, plugins, multi-channel)

Please respond with the number (1-5) or describe if it's something else.""",
        "options": {"1": "saas", "2": "api", "3": "agent", "4": "multi-agent", "5": "platform"},
    },
    {
        "id": "scale",
        "question": """**Question 2 of 5: What scale do you expect?**

1. **MVP** (<100 users) - Validate idea, $300-500/month
2. **Growth** (100-10K users) - Scaling up, $1,500-3,000/month
3. **Scale** (10K-100K users) - Established product, $8,000-15,000/month
4. **Enterprise** (100K+ users) - Large scale, $50,000+/month

Which phase are you targeting initially?""",
        "options": {"1": "mvp", "2": "growth", "3": "scale", "4": "enterprise"},
    },
    {
        "id": "frontend",
        "question": """**Question 3 of 5: Frontend preference?**

1. **React + Vite** - Modern, fast, great ecosystem
2. **Next.js** - Full-stack React with SSR
3. **Vue + Nuxt** - Progressive framework
4. **None** - API only, no frontend

Which do you prefer?""",
        "options": {"1": "react-vite", "2": "nextjs", "3": "vue-nuxt", "4": "none"},
    },
    {
        "id": "backend",
        "question": """**Question 4 of 5: Backend preference?**

1. **FastAPI (Python)** - Modern async, great for AI integrations
2. **Express (Node.js)** - Simple, flexible, large ecosystem
3. **Django (Python)** - Batteries included, admin panel
4. **Serverless** - Cloud Functions / Lambda

Which fits your needs?""",
        "options": {"1": "fastapi", "2": "express", "3": "django", "4": "serverless"},
    },
    {
        "id": "database",
        "question": """**Question 5 of 5: Database preference?**

1. **PostgreSQL + Supabase** - Recommended for most projects
2. **MongoDB** - Document database, flexible schema
3. **SQLite** - Simple, file-based (MVP only)
4. **Firebase** - Google's BaaS, real-time sync

Which do you prefer?""",
        "options": {"1": "postgresql-supabase", "2": "mongodb", "3": "sqlite", "4": "firebase"},
    },
]


def create_initial_state(objective: str, mode: str = "supervised") -> OrchestratorState:
    """Create the initial orchestrator state for a new project."""
    import uuid

    project = ProjectState(
        id=str(uuid.uuid4())[:8],
        objective=objective,
        mode=AutonomyMode(mode),
        current_phase=Phase.DISCOVERY,
    )

    return OrchestratorState(project=project)


# =============================================================================
# Node Functions
# =============================================================================

def discovery_node(state: OrchestratorState) -> OrchestratorState:
    """
    Handle Discovery phase - ask questions to understand the project.
    """
    project = state.project
    question_index = state.discovery_question_index
    user_input = state.user_input

    # If we have user input, process the answer
    if user_input and question_index > 0:
        prev_question = DISCOVERY_QUESTIONS[question_index - 1]
        answer = user_input.strip()

        # Map the answer
        if prev_question["id"] == "project_type":
            mapped = prev_question["options"].get(answer, answer)
            try:
                project.project_type = ProjectType(mapped)
            except ValueError:
                project.project_type = ProjectType.SAAS  # Default

        elif prev_question["id"] == "scale":
            mapped = prev_question["options"].get(answer, "mvp")
            try:
                project.scale = ScalePhase(mapped)
            except ValueError:
                project.scale = ScalePhase.MVP

        elif prev_question["id"] == "frontend":
            mapped = prev_question["options"].get(answer, "react-vite")
            project.tech_stack.frontend = mapped

        elif prev_question["id"] == "backend":
            mapped = prev_question["options"].get(answer, "fastapi")
            project.tech_stack.backend = mapped

        elif prev_question["id"] == "database":
            mapped = prev_question["options"].get(answer, "postgresql-supabase")
            project.tech_stack.database = mapped

    # Check if discovery is complete
    if question_index >= len(DISCOVERY_QUESTIONS):
        # Move to planning phase
        project.current_phase = Phase.PLANNING
        project.needs_user_input = False

        # Auto-capture discovery lessons
        from agent.meta_learning.capture import auto_capture_phase_lesson
        auto_capture_phase_lesson("discovery", project)

        # Generate summary
        ts = project.tech_stack
        summary = f"""
## Discovery Complete!

**Project Summary:**
- **Objective**: {project.objective}
- **Type**: {project.project_type.value if project.project_type else "Not set"}
- **Scale**: {project.scale.value}
- **Tech Stack**:
  - Frontend: {ts.frontend or "N/A"}
  - Backend: {ts.backend or "N/A"}
  - Database: {ts.database or "N/A"}

---

## Moving to Planning Phase

I will now generate:
1. **CLAUDE.md** - Global rules for your project
2. **PRD** - Product Requirements Document

Reply with "continue" to proceed.
"""
        return OrchestratorState(
            project=project,
            agent_output=summary,
            discovery_question_index=question_index,
            should_continue=True,
        )

    # Ask the next question
    current_question = DISCOVERY_QUESTIONS[question_index]
    project.needs_user_input = True
    project.pending_question = current_question["question"]

    # Build output
    if question_index == 0:
        output = f"""
## Discovery Phase - Understanding Your Project

Based on your objective: **{project.objective}**

I need to understand a few things to recommend the best approach.

{current_question["question"]}
"""
    else:
        output = current_question["question"]

    return OrchestratorState(
        project=project,
        agent_output=output,
        discovery_question_index=question_index + 1,
        should_continue=True,
    )


def planning_node(state: OrchestratorState) -> OrchestratorState:
    """
    Handle Planning phase - generate CLAUDE.md and PRD.

    Generates project-type-specific artifacts and evaluates their quality.
    """
    from agent.evals import ArtifactEvaluator

    project = state.project
    evaluator = ArtifactEvaluator()

    # Generate CLAUDE.md
    claude_md = _generate_claude_md(project)

    # Generate PRD
    prd = _generate_prd(project)

    # Evaluate artifacts
    claude_eval = evaluator.evaluate_claude_md(claude_md)
    prd_eval = evaluator.evaluate_prd(prd)

    # Store evaluation scores
    project.validation_results["claude_md_score"] = claude_eval.score
    project.validation_results["prd_score"] = prd_eval.score
    project.validation_results["claude_md_passed"] = claude_eval.passed
    project.validation_results["prd_passed"] = prd_eval.passed

    project.claude_md = claude_md
    project.prd = prd
    project.current_phase = Phase.ROADMAP
    project.needs_user_input = True

    # Auto-capture planning lessons
    from agent.meta_learning.capture import auto_capture_phase_lesson
    auto_capture_phase_lesson("planning", project)

    # Build eval summary
    eval_summary = f"""
### Artifact Quality

{claude_eval.format_report()}

{prd_eval.format_report()}
"""

    output = f"""
## Planning Phase Complete!

### Generated CLAUDE.md

```markdown
{claude_md[:1500]}...
```

*(Truncated for display - full version will be saved to file)*

---

### Generated PRD

```markdown
{prd}
```

---

{eval_summary}

---

## Next: Roadmap Phase

I'll break this down into implementable features.

Reply with "continue" to proceed to Roadmap.
"""

    return OrchestratorState(
        project=project,
        agent_output=output,
        should_continue=True,
    )


def _generate_claude_md(project: ProjectState) -> str:
    """Generate CLAUDE.md content based on project type."""
    ts = project.tech_stack
    pt = project.project_type

    # Base principles (universal)
    principles = """- **TYPE_SAFETY**: All functions must have type hints
- **VERBOSE_NAMING**: Use descriptive names (get_user_by_email, not get_user)
- **AI_FRIENDLY_LOGGING**: JSON structured logs with fix_suggestion field
- **KISS**: Keep solutions simple, avoid over-engineering
- **YAGNI**: Don't build features until needed"""

    # Project-type-specific sections
    if pt == ProjectType.PLATFORM:
        arch_section = """- **Pattern**: Modular Platform Architecture (Plugin-based)
- **API Style**: REST with OpenAPI + WebSocket for real-time
- **Auth**: JWT with refresh tokens + API keys for service-to-service
- **Multi-tenancy**: Row-Level Security with tenant context
- **Plugin System**: Dynamic tool registration with schema validation
- **Agent Communication**: Message bus for inter-agent coordination
- **Memory**: Hybrid search (vector + keyword) with auto-capture"""

        extra_patterns = """
### Plugin Registration Pattern
```python
class PluginRegistry:
    def __init__(self):
        self._plugins: dict[str, PluginManifest] = {{}}

    def register(self, manifest: PluginManifest) -> None:
        self._plugins[manifest.id] = manifest

    def get_tools(self, plugin_id: str) -> list[Tool]:
        return self._plugins[plugin_id].tools
```

### Agent Message Pattern
```python
class AgentMessage(BaseModel):
    from_agent: str
    to_agent: str
    content: str
    message_type: str  # "request", "response", "broadcast"
    context: dict[str, Any] = {{}}
```

### Heartbeat Pattern
```python
class HeartbeatSchedule(BaseModel):
    schedule_type: str  # "every", "at", "cron"
    expression: str     # "5m", "09:00", "0 9 * * *"
    payload: dict[str, Any] = {{}}
```
"""
    elif pt == ProjectType.AGENT:
        arch_section = """- **Pattern**: Agent Core with Tool Registry
- **API Style**: REST with streaming support
- **Memory**: Conversation history + persistent memory
- **Tools**: Registered via decorator pattern
- **Guardrails**: Input/output validation gates"""

        extra_patterns = """
### Agent Tool Pattern
```python
@agent.tool
async def search_knowledge(query: str) -> str:
    results = await knowledge_base.search(query)
    return format_results(results)
```

### Memory Pattern
```python
class AgentMemory:
    def __init__(self, session_id: str):
        self.short_term: list[Message] = []
        self.long_term: VectorStore = VectorStore(session_id)

    async def recall(self, query: str) -> list[str]:
        return await self.long_term.search(query, limit=5)
```
"""
    elif pt == ProjectType.MULTI_AGENT:
        arch_section = """- **Pattern**: Supervisor + Specialized Agents
- **API Style**: REST with WebSocket for agent events
- **Orchestration**: LangGraph state machine
- **Communication**: Shared state + message passing
- **Factory**: Agent Registry with dynamic instantiation"""

        extra_patterns = """
### Supervisor Pattern
```python
class Supervisor:
    def __init__(self, agents: dict[str, BaseAgent]):
        self.agents = agents

    async def route(self, task: str) -> AgentResult:
        agent_name = self._select_agent(task)
        return await self.agents[agent_name].execute(task)
```

### Agent Factory Pattern
```python
class AgentRegistry:
    _agents: dict[str, type[BaseAgent]] = {{}}

    @classmethod
    def register(cls, name: str):
        def decorator(agent_cls):
            cls._agents[name] = agent_cls
            return agent_cls
        return decorator
```
"""
    else:  # SAAS, API, default
        arch_section = """- **Pattern**: Vertical Slice Architecture
- **API Style**: REST with OpenAPI documentation
- **Auth**: JWT with refresh tokens
- **Multi-tenancy**: Row-Level Security (if applicable)"""

        extra_patterns = """
### Service Pattern (Python)
```python
class UserService:
    def __init__(self, db: Database):
        self.db = db

    async def get_user_by_email(self, email: str) -> User | None:
        return await self.db.users.find_one({{"email": email}})
```

### API Handler Pattern
```python
@router.get("/users/{{user_id}}")
async def get_user(user_id: str, service: UserService = Depends()) -> UserResponse:
    user = await service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.from_orm(user)
```
"""

    # Determine package manager and test framework
    is_python = "python" in (ts.backend or "").lower() or "fastapi" in (ts.backend or "").lower() or "django" in (ts.backend or "").lower()
    pkg_manager = "uv (Python)" if is_python else "pnpm (Node)"
    test_framework = "pytest" if is_python else "vitest"

    claude_md = f"""# {project.objective}

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

- Use {"snake_case" if is_python else "camelCase"} for {"Python" if is_python else "TypeScript"}
- Maximum line length: 100 characters
- Docstrings required for public functions
- Type hints required for all function parameters and returns

## Testing

- Unit tests mirror source structure
- Integration tests in tests/integration/
- Minimum 80% coverage for core features
- {"Use pytest markers: @pytest.mark.unit, @pytest.mark.integration" if is_python else "Use vitest describe/it pattern with test.each for parameterized tests"}

## Common Patterns
{extra_patterns}"""

    return claude_md


def _generate_prd(project: ProjectState) -> str:
    """Generate PRD content based on project type."""
    ts = project.tech_stack
    pt = project.project_type

    # Project-type-specific features
    if pt == ProjectType.PLATFORM:
        core_features = """1. User authentication with role-based access (admin, developer, end-user)
2. Core platform engine (knowledge base, data management)
3. Agent/employee registry and lifecycle management
4. Plugin architecture for extensibility
5. Real-time communication (WebSocket)
6. Admin dashboard with platform metrics"""
        nice_to_have = """1. Marketplace for third-party agents/plugins
2. Token-based billing system
3. Multi-channel delivery (web, Slack, WhatsApp)
4. Agent observability dashboard (Langfuse)
5. Heartbeat/proactive agent scheduling"""
    elif pt == ProjectType.AGENT:
        core_features = """1. Agent with system prompt and tool execution
2. Conversation memory (short-term + long-term)
3. Tool registry with dynamic loading
4. API interface for agent interaction
5. Input/output validation guardrails"""
        nice_to_have = """1. Streaming responses
2. Multi-modal support
3. Memory search and curation
4. Usage analytics"""
    elif pt == ProjectType.MULTI_AGENT:
        core_features = """1. Agent registry and factory pattern
2. Supervisor/router for task coordination
3. Individual specialized agents (3-5)
4. Inter-agent communication protocol
5. Shared state management
6. API interface for system interaction"""
        nice_to_have = """1. Dynamic agent spawning
2. Agent performance metrics
3. Human-in-the-loop approval gates
4. Parallel execution optimization"""
    else:  # SAAS, API
        core_features = """1. User authentication (signup, login, password reset)
2. Core functionality based on objective
3. Basic admin dashboard
4. API with CRUD operations
5. Data validation and error handling"""
        nice_to_have = """1. Email notifications
2. User preferences and settings
3. Analytics dashboard
4. Export/import functionality"""

    prd = f"""# Product Requirements Document

## Executive Summary

**Product**: {project.objective}
**Type**: {pt.value if pt else "Application"}
**Target Scale**: {project.scale.value}

## Mission

Build a {pt.value if pt else "application"} that {project.objective}.

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

## Tech Stack

- Frontend: {ts.frontend or "N/A"}
- Backend: {ts.backend or "N/A"}
- Database: {ts.database or "N/A"}

## Known Gotchas

- Ensure environment variables are never committed to git
- Use atomic database operations for concurrent access
- Validate all user inputs at API boundary
- Test error paths, not just happy paths
"""

    return prd


def roadmap_node(state: OrchestratorState) -> OrchestratorState:
    """
    Handle Roadmap phase - break down into features.
    """
    project = state.project

    # Generate feature breakdown based on project type
    if project.project_type == ProjectType.SAAS:
        features = [
            Feature(name="Project Setup", description="Initialize project with tech stack, create folder structure, configure tooling"),
            Feature(name="Authentication", description="Implement user signup, login, logout, password reset with JWT"),
            Feature(name="Multi-Tenancy", description="Implement tenant isolation with Row-Level Security"),
            Feature(name="Core Data Models", description="Define database schema, create ORM models, implement CRUD operations"),
            Feature(name="API Endpoints", description="Create REST endpoints for core functionality"),
            Feature(name="Frontend Setup", description="Initialize frontend, configure routing, create layout components"),
            Feature(name="Dashboard", description="Create main dashboard with key metrics and navigation"),
        ]
    elif project.project_type == ProjectType.AGENT:
        features = [
            Feature(name="Project Setup", description="Initialize project with Pydantic AI, configure environment"),
            Feature(name="Agent Core", description="Create main agent with system prompt and configuration"),
            Feature(name="Tools", description="Implement agent tools for required functionality"),
            Feature(name="Memory", description="Add conversation memory and context management"),
            Feature(name="API Interface", description="Create FastAPI endpoints to interact with agent"),
        ]
    elif project.project_type == ProjectType.MULTI_AGENT:
        features = [
            Feature(name="Project Setup", description="Initialize project with LangGraph, configure environment"),
            Feature(name="Agent Registry", description="Create agent registry and factory pattern"),
            Feature(name="Individual Agents", description="Implement specialized agents for each task"),
            Feature(name="Orchestrator", description="Create supervisor/router for agent coordination"),
            Feature(name="Communication", description="Implement inter-agent messaging and state sharing"),
            Feature(name="API Interface", description="Create FastAPI endpoints to interact with system"),
        ]
    elif project.project_type == ProjectType.PLATFORM:
        features = [
            Feature(name="Project Setup", description="Initialize project with tech stack, monorepo structure, configure tooling"),
            Feature(name="Authentication", description="Implement user auth with role-based access (admin, developer, end-user)"),
            Feature(name="Core Data Models", description="Define database schema for platform entities, tenants, and relationships"),
            Feature(name="Plugin Architecture", description="Create plugin registry, dynamic tool loading, and SDK for extensions"),
            Feature(name="Agent Registry", description="Build agent/employee lifecycle management with factory pattern"),
            Feature(name="Real-time Communication", description="Implement WebSocket for agent events and inter-agent messaging"),
            Feature(name="Dashboard", description="Create admin dashboard with platform metrics, agent status, and user management"),
            Feature(name="API Endpoints", description="Create REST + WebSocket endpoints for all platform operations"),
        ]
    else:  # API or default
        features = [
            Feature(name="Project Setup", description="Initialize project with tech stack, create folder structure"),
            Feature(name="Core Data Models", description="Define database schema, create ORM models"),
            Feature(name="API Endpoints", description="Create REST endpoints for core functionality"),
            Feature(name="Authentication", description="Implement auth middleware and JWT handling"),
            Feature(name="Testing", description="Add unit and integration tests"),
        ]

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

    features_list = "\n".join([
        f"{i+1}. **{f.name}** - {f.description}"
        for i, f in enumerate(features)
    ])

    output = f"""
## Roadmap Phase Complete!

### Feature Breakdown ({len(features)} features)

{features_list}

---

## Ready for Implementation

I'll implement these features one by one using the PIV Loop:
- **P**lan: Create detailed implementation plan
- **I**mplement: Write the code
- **V**alidate: Run tests and linting

Reply with "start" to begin implementing Feature 1: {features[0].name}.
"""

    return OrchestratorState(
        project=project,
        agent_output=output,
        should_continue=True,
    )


def implementation_node(state: OrchestratorState) -> OrchestratorState:
    """
    Handle Implementation phase - execute PIV Loop for each feature.

    Generates detailed implementation plans with:
    - Files to create/modify
    - Step-by-step tasks
    - Validation commands
    - Relevant playbook references
    """
    from agent.tools.playbook_rag import search_keyword

    project = state.project
    current_idx = project.current_feature_index
    ts = project.tech_stack

    # Check if all features are done
    if current_idx >= len(project.features):
        project.current_phase = Phase.DEPLOYMENT
        output = """
## All Features Implemented!

Moving to Deployment phase.

Reply with "continue" to generate deployment configurations.
"""
        return OrchestratorState(
            project=project,
            agent_output=output,
            should_continue=True,
        )

    feature = project.features[current_idx]

    # Check user input for navigation
    user_input = state.user_input or ""
    if user_input.lower().strip() == "next":
        # Mark current as complete, move to next
        feature.status = "completed"
        project.current_feature_index += 1

        if project.current_feature_index >= len(project.features):
            project.current_phase = Phase.DEPLOYMENT
            output = """
## All Features Implemented!

Moving to Deployment phase.

Reply with "continue" to generate deployment configurations.
"""
        else:
            next_feature = project.features[project.current_feature_index]
            next_feature.status = "in_progress"
            output = f"""
## Feature {current_idx + 1} Complete!

Moving to Feature {project.current_feature_index + 1}: **{next_feature.name}**

{next_feature.description}

Reply with "plan" to see the implementation plan, or "next" when done.
"""
        return OrchestratorState(
            project=project,
            agent_output=output,
            should_continue=True,
        )

    # Start or continue current feature
    feature.status = "in_progress"

    # Generate feature-specific implementation plan (context-aware when PRD/CLAUDE.md available)
    plan = generate_feature_plan(
        feature.name, feature.description, ts, project.project_type,
        prd=project.prd, claude_md=project.claude_md, features=project.features,
    )

    # Evaluate the generated plan
    from agent.evals import ArtifactEvaluator
    evaluator = ArtifactEvaluator()
    plan_eval = evaluator.evaluate_plan(plan)

    # Store plan quality score
    project.validation_results[f"plan_{feature.name}_score"] = plan_eval.score

    # Search for relevant playbook content (using hybrid search)
    from agent.tools.playbook_rag import search_hybrid
    search_results = search_hybrid(feature.name, max_results=3)
    playbook_refs = ""
    if search_results:
        playbook_refs = "\n### Relevant Playbook References\n"
        for result in search_results[:3]:
            playbook_refs += f"- `{result.file}`: {result.title}\n"

    # Plan quality indicator
    quality_indicator = f"**Plan Quality**: {plan_eval.score:.0%}"
    if plan_eval.suggestions:
        quality_indicator += " | Suggestions: " + "; ".join(plan_eval.suggestions[:2])

    output = f"""
## PIV Loop - Feature {current_idx + 1}/{len(project.features)}: {feature.name}

### P - Plan

**Objective**: {feature.description}
{quality_indicator}

{plan}

### I - Implement

Execute the tasks above in order. For each task:
1. Read any referenced files first
2. Write the code following CLAUDE.md patterns
3. Don't leave TODOs - implement completely

### V - Validate

After implementation, run:
```bash
# Type checking
{"mypy src/ --ignore-missing-imports" if "python" in (ts.backend or "").lower() else "npx tsc --noEmit"}

# Linting
{"ruff check src/" if "python" in (ts.backend or "").lower() else "npm run lint"}

# Tests
{"pytest tests/ -v" if "python" in (ts.backend or "").lower() else "npm test"}
```
{playbook_refs}

---

**Commands:**
- `next` - Mark complete and move to next feature
- `plan` - Show this plan again
- `skip` - Skip this feature
"""

    return OrchestratorState(
        project=project,
        agent_output=output,
        should_continue=True,
    )


def generate_validation_loop(tech_stack) -> str:
    """Generate validation commands based on tech stack."""
    is_python = "python" in (tech_stack.backend or "").lower() or "fastapi" in (tech_stack.backend or "").lower()

    if is_python:
        return """
**Validation Loop:**
```bash
# Level 1: Syntax & Style
ruff check src/ --fix
ruff format src/

# Level 2: Type Safety
mypy src/ --ignore-missing-imports

# Level 3: Unit Tests
pytest tests/ -v --tb=short

# Level 4: Integration Tests (if applicable)
pytest tests/integration/ -v --tb=short

# Level 5: Build verification
python -c "from src.main import app; print('Build OK')"
```"""
    else:
        return """
**Validation Loop:**
```bash
# Level 1: Syntax & Style
npm run lint
npx prettier --check src/

# Level 2: Type Safety
npx tsc --noEmit

# Level 3: Unit Tests
npm test

# Level 4: Integration Tests (if applicable)
npm run test:integration

# Level 5: Build verification
npm run build
```"""


def generate_feature_plan(
    name: str,
    description: str,
    tech_stack,
    project_type,
    prd: str | None = None,
    claude_md: str | None = None,
    features: list | None = None,
) -> str:
    """Generate a detailed implementation plan for a feature.

    When prd and claude_md are available, uses PRPBuilder for context-aware plans.
    Otherwise falls back to hardcoded templates for backwards compatibility.
    """
    # Use PRPBuilder when full context is available
    if prd and claude_md:
        from agent.prp_builder import PRPBuilder
        from agent.models.project import ProjectState, Feature as FeatureModel

        # Build a minimal ProjectState for PRPBuilder
        project = ProjectState(
            id="plan-gen",
            objective="",
            tech_stack=tech_stack,
            project_type=project_type,
            prd=prd,
            claude_md=claude_md,
            features=features or [],
        )
        builder = PRPBuilder(project)

        # Find the matching feature or create a temporary one
        target_feature = None
        for f in (features or []):
            if f.name == name:
                target_feature = f
                break

        if not target_feature:
            target_feature = FeatureModel(name=name, description=description)

        return builder.build_feature_prp(target_feature)

    # Fallback: hardcoded templates when no PRD/CLAUDE.md context
    validation = generate_validation_loop(tech_stack)

    # Feature-specific plan templates
    plans = {
        "Project Setup": f"""
**Files to create:**
- `src/` - Source directory
- `tests/` - Test directory
- `{"pyproject.toml" if "python" in (tech_stack.backend or "").lower() else "package.json"}` - Dependencies
- `.env.example` - Environment variables template
- `CLAUDE.md` - Already generated
- `docs/PRD.md` - Already generated

**Tasks:**
1. Initialize project with `{"uv init" if "python" in (tech_stack.backend or "").lower() else "npm init -y"}`
2. Install dependencies from generated config
3. Create folder structure following Vertical Slice Architecture
4. Configure linting and formatting
5. Set up pre-commit hooks
""",

        "Authentication": f"""
**Files to create:**
- `src/auth/router.py` - Auth API endpoints
- `src/auth/service.py` - Auth business logic
- `src/auth/models.py` - User model, tokens
- `src/auth/schemas.py` - Pydantic schemas
- `tests/auth/test_auth.py` - Auth tests

**Tasks:**
1. Create User model with email, password_hash, created_at
2. Implement password hashing with bcrypt
3. Create signup endpoint (POST /auth/signup)
4. Create login endpoint (POST /auth/login) returning JWT
5. Create refresh token endpoint
6. Add auth middleware for protected routes
7. Write tests for each endpoint

**Database migrations:**
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```
""",

        "Core Data Models": f"""
**Files to create:**
- `src/models/` - Database models directory
- `src/schemas/` - Pydantic/TypeScript schemas
- `migrations/` - Database migrations

**Tasks:**
1. Analyze PRD to identify all entities
2. Create database models for each entity
3. Define relationships (foreign keys, many-to-many)
4. Create Pydantic schemas for API I/O
5. Write migration scripts
6. Create seed data for development

**Pattern to follow:**
```python
class BaseModel:
    id: UUID
    created_at: datetime
    updated_at: datetime

class YourEntity(BaseModel):
    # Add your fields
    tenant_id: UUID  # For multi-tenancy
```
""",

        "Dashboard": f"""
**Files to create:**
- `src/{"app" if "next" in (tech_stack.frontend or "").lower() else "pages"}/dashboard/page.tsx`
- `src/components/dashboard/` - Dashboard components
- `src/components/charts/` - Chart components
- `src/hooks/useDashboardData.ts` - Data fetching hook

**Tasks:**
1. Create dashboard layout with sidebar navigation
2. Add KPI cards (total count, growth %, etc.)
3. Implement charts using {"Recharts" if "react" in (tech_stack.frontend or "").lower() else "Chart.js"}
4. Add data table with sorting/filtering
5. Implement loading states and error handling
6. Make responsive for mobile

**Component structure:**
```
Dashboard/
├── DashboardLayout.tsx
├── KPICard.tsx
├── DataTable.tsx
└── Charts/
    ├── LineChart.tsx
    └── BarChart.tsx
```
""",

        "API Endpoints": f"""
**Files to create:**
- `src/api/` - API routes directory
- `src/api/v1/` - Version 1 endpoints
- `src/middleware/` - Auth, logging, error handling

**Tasks:**
1. Create base router with versioning (/api/v1/)
2. Implement CRUD endpoints for each model
3. Add pagination, filtering, sorting
4. Implement error handling middleware
5. Add request validation
6. Document with OpenAPI/Swagger

**Endpoint pattern:**
```
GET    /api/v1/resources      - List all
GET    /api/v1/resources/:id  - Get one
POST   /api/v1/resources      - Create
PUT    /api/v1/resources/:id  - Update
DELETE /api/v1/resources/:id  - Delete
```
""",
    }

    # Return specific plan or generate generic one
    if name in plans:
        return plans[name] + validation

    # Generic plan for unknown features
    feature_slug = name.lower().replace(" ", "_")
    return f"""
**Files to create:**
- `src/{feature_slug}/` - Feature directory
- `src/{feature_slug}/router.py` - API endpoints
- `src/{feature_slug}/service.py` - Business logic
- `src/{feature_slug}/models.py` - Data models
- `tests/{feature_slug}/` - Tests

**Tasks:**
1. Create feature directory structure
2. Define data models needed
3. Implement business logic in service layer
4. Create API endpoints
5. Write unit tests
6. Write integration tests
7. Update API documentation

**Integration Points:**
- Connects to database via ORM models
- Requires authentication middleware
- Exposes REST endpoints under `/api/v1/{feature_slug}`
{validation}
"""


def deployment_node(state: OrchestratorState) -> OrchestratorState:
    """
    Handle Deployment phase - generate deployment configs.

    Generates actual configuration files based on scale:
    - MVP: Netlify + Railway + Supabase
    - Growth: Netlify + Cloud Run + Cloud SQL
    - Scale/Enterprise: Kubernetes + Terraform
    """
    project = state.project
    scale = project.scale
    ts = project.tech_stack

    # Generate deployment configs based on scale
    configs = generate_deployment_configs(scale, ts, project.objective)

    # Store configs in project
    project.deployment_configs = configs

    if scale == ScalePhase.MVP:
        config_info = f"""
### MVP Deployment Stack ($5-50/month)

| Component | Service | Cost |
|-----------|---------|------|
| Frontend | Netlify Free | $0 |
| Backend | Railway | $5-20 |
| Database | Supabase Free | $0 |
| Auth | Supabase Auth | $0 |

### Generated Configuration Files

**1. netlify.toml** (Frontend)
```toml
{configs.get('netlify.toml', '# Not generated')}
```

**2. Dockerfile** (Backend)
```dockerfile
{configs.get('Dockerfile', '# Not generated')}
```

**3. .github/workflows/deploy.yml** (CI/CD)
```yaml
{configs.get('deploy.yml', '# Not generated')}
```

### Deployment Commands
```bash
# Frontend (Netlify)
npm run build
netlify deploy --prod

# Backend (Railway)
railway login
railway up

# Database (Supabase)
supabase db push
```
"""
    elif scale == ScalePhase.GROWTH:
        config_info = f"""
### Growth Deployment Stack ($100-500/month)

| Component | Service | Cost |
|-----------|---------|------|
| Frontend | Netlify Pro | $19 |
| Backend | Cloud Run | $50-200 |
| Database | Cloud SQL | $50-150 |
| CDN | Cloudflare | $20 |

### Generated Configuration Files

**1. cloudbuild.yaml** (GCP CI/CD)
```yaml
{configs.get('cloudbuild.yaml', '# Not generated')}
```

**2. Dockerfile** (Multi-stage)
```dockerfile
{configs.get('Dockerfile', '# Not generated')}
```

### Deployment Commands
```bash
# Deploy to Cloud Run
gcloud run deploy {project.objective.lower().replace(' ', '-')[:20]} \\
  --source . \\
  --region us-central1 \\
  --allow-unauthenticated
```
"""
    else:
        config_info = f"""
### Scale/Enterprise Stack ($1,000-10,000+/month)

| Component | Service | Cost |
|-----------|---------|------|
| Frontend | CDN + Edge | $100+ |
| Backend | GKE/EKS | $500+ |
| Database | Cloud SQL HA | $300+ |
| Monitoring | Datadog/New Relic | $100+ |

### Generated Configuration Files

**1. kubernetes/deployment.yaml**
```yaml
{configs.get('deployment.yaml', '# Not generated')}
```

**2. kubernetes/service.yaml**
```yaml
{configs.get('service.yaml', '# Not generated')}
```

### Deployment Commands
```bash
# Apply Kubernetes manifests
kubectl apply -f kubernetes/

# Check status
kubectl get pods -l app={project.objective.lower().replace(' ', '-')[:20]}
```
"""

    project.current_phase = Phase.COMPLETED

    # Auto-capture deployment lessons
    from agent.meta_learning.capture import auto_capture_phase_lesson
    auto_capture_phase_lesson("deployment", project)

    output = f"""
## Deployment Phase

Based on your scale target: **{scale.value}**

{config_info}

---

## Project Complete!

### Summary
| Item | Value |
|------|-------|
| Objective | {project.objective} |
| Type | {project.project_type.value if project.project_type else "N/A"} |
| Features | {len(project.features)} planned |
| Scale | {scale.value} |
| Tech Stack | {ts.frontend or "N/A"} + {ts.backend or "N/A"} + {ts.database or "N/A"} |

### Generated Artifacts
- `CLAUDE.md` - Global rules for AI coding
- `docs/PRD.md` - Product requirements document
- Feature Plans - {len(project.features)} implementation guides
- Deployment Configs - Ready for {scale.value}

### Next Steps
1. Copy generated configs to your project
2. Set up environment variables
3. Configure secrets in your CI/CD
4. Deploy and monitor

### Useful Commands
```bash
# Get CLAUDE.md content
playbook_get_claude_md "{project.id}"

# Get PRD content
playbook_get_prd "{project.id}"

# Check project status
playbook_get_status "{project.id}"
```
"""

    return OrchestratorState(
        project=project,
        agent_output=output,
        should_continue=False,  # End the workflow
    )


def generate_deployment_configs(scale: ScalePhase, tech_stack, objective: str) -> dict[str, str]:
    """Generate deployment configuration files based on scale."""

    app_name = objective.lower().replace(' ', '-')[:20]
    is_python = "python" in (tech_stack.backend or "").lower() or "fastapi" in (tech_stack.backend or "").lower()

    configs = {}

    # Netlify config (all scales)
    configs['netlify.toml'] = f"""[build]
  command = "npm run build"
  publish = "{"out" if "next" in (tech_stack.frontend or "").lower() else "dist"}"

[build.environment]
  NODE_VERSION = "20"

[[redirects]]
  from = "/api/*"
  to = "{f"https://{app_name}.railway.app/api/:splat" if scale == ScalePhase.MVP else f"https://{app_name}-api.a]run.app/api/:splat"}"
  status = 200

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-Content-Type-Options = "nosniff"
"""

    # Dockerfile
    if is_python:
        configs['Dockerfile'] = f"""FROM python:3.12-slim as builder

WORKDIR /app
RUN pip install uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

FROM python:3.12-slim

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY src/ ./src/

ENV PATH="/app/.venv/bin:$PATH"
ENV PORT=8080

EXPOSE 8080
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
"""
    else:
        configs['Dockerfile'] = f"""FROM node:20-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:20-alpine

WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY package*.json ./

ENV PORT=8080
EXPOSE 8080
CMD ["node", "dist/index.js"]
"""

    # CI/CD based on scale
    if scale == ScalePhase.MVP:
        configs['deploy.yml'] = f"""name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Deploy to Railway
        uses: railwayapp/railway-action@v1
        with:
          railway_token: ${{{{ secrets.RAILWAY_TOKEN }}}}
"""
    elif scale == ScalePhase.GROWTH:
        configs['cloudbuild.yaml'] = f"""steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/{app_name}:$COMMIT_SHA', '.']

  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/{app_name}:$COMMIT_SHA']

  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - '{app_name}'
      - '--image=gcr.io/$PROJECT_ID/{app_name}:$COMMIT_SHA'
      - '--region=us-central1'
      - '--platform=managed'
      - '--allow-unauthenticated'

images:
  - 'gcr.io/$PROJECT_ID/{app_name}:$COMMIT_SHA'
"""
    else:  # Scale/Enterprise
        configs['deployment.yaml'] = f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {app_name}
  labels:
    app: {app_name}
spec:
  replicas: 3
  selector:
    matchLabels:
      app: {app_name}
  template:
    metadata:
      labels:
        app: {app_name}
    spec:
      containers:
        - name: {app_name}
          image: gcr.io/PROJECT_ID/{app_name}:latest
          ports:
            - containerPort: 8080
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: {app_name}-secrets
                  key: database-url
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "512Mi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 10
            periodSeconds: 10
"""
        configs['service.yaml'] = f"""apiVersion: v1
kind: Service
metadata:
  name: {app_name}
spec:
  type: LoadBalancer
  ports:
    - port: 80
      targetPort: 8080
  selector:
    app: {app_name}
"""

    return configs


def error_node(state: OrchestratorState) -> OrchestratorState:
    """Handle errors in the workflow."""
    return OrchestratorState(
        project=state.project,
        agent_output=f"Error occurred: {state.error}",
        should_continue=False,
        error=state.error,
    )


# =============================================================================
# Router Function
# =============================================================================

def route_by_phase(state: OrchestratorState) -> str:
    """Route to the appropriate node based on current phase."""
    if state.error:
        return "error"

    phase = state.project.current_phase

    if phase == Phase.DISCOVERY:
        return "discovery"
    elif phase == Phase.PLANNING:
        return "planning"
    elif phase == Phase.ROADMAP:
        return "roadmap"
    elif phase == Phase.IMPLEMENTATION:
        return "implementation"
    elif phase == Phase.DEPLOYMENT:
        return "deployment"
    elif phase == Phase.COMPLETED:
        return END
    else:
        return "error"


def should_continue(state: OrchestratorState) -> str:
    """Determine if we should continue or end."""
    if not state.should_continue:
        return "end"
    if state.project.needs_user_input:
        return "end"  # Pause for user input
    return "continue"


# =============================================================================
# Build the Graph
# =============================================================================

def build_orchestrator() -> StateGraph:
    """Build and return the LangGraph orchestrator."""

    # Create the graph
    workflow = StateGraph(OrchestratorState)

    # Add nodes
    workflow.add_node("discovery", discovery_node)
    workflow.add_node("planning", planning_node)
    workflow.add_node("roadmap", roadmap_node)
    workflow.add_node("implementation", implementation_node)
    workflow.add_node("deployment", deployment_node)
    workflow.add_node("error", error_node)

    # Set entry point based on phase
    workflow.set_conditional_entry_point(
        route_by_phase,
        {
            "discovery": "discovery",
            "planning": "planning",
            "roadmap": "roadmap",
            "implementation": "implementation",
            "deployment": "deployment",
            "error": "error",
        }
    )

    # All phase nodes go to END (we run one step at a time)
    workflow.add_edge("discovery", END)
    workflow.add_edge("planning", END)
    workflow.add_edge("roadmap", END)
    workflow.add_edge("implementation", END)
    workflow.add_edge("deployment", END)
    workflow.add_edge("error", END)

    return workflow.compile()


# Create the compiled orchestrator
orchestrator = build_orchestrator()


def run_orchestrator(state: OrchestratorState) -> OrchestratorState:
    """Run the orchestrator with the given state."""
    # Convert to dict for LangGraph
    state_dict = state.model_dump()

    # Run the graph
    result = orchestrator.invoke(state_dict)

    # Convert back to OrchestratorState
    if isinstance(result, dict):
        # Reconstruct the state from dict
        return OrchestratorState(**result)
    return result
