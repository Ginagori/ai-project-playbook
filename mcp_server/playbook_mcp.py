"""
AI Project Playbook MCP Server

Exposes the AI Project Playbook Agent as an MCP server for Claude Code integration.
Uses LangGraph orchestrator for phase management.
Includes Agent Factory for multi-agent patterns and specialized agents.
Supports Supabase for shared team knowledge base.
"""

import asyncio
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from agent.orchestrator import (
    OrchestratorState,
    create_initial_state,
    run_orchestrator,
)
from agent.tools.playbook_rag import search_playbook as rag_search
from agent.factory.base import AgentContext
from agent.factory.playbook_agents import (
    default_pipeline,
    default_router,
    default_supervisor,
    create_code_review_parallel,
    run_development_task,
    run_feature_pipeline,
)
from agent.meta_learning import (
    capture_project_outcome,
    find_similar_projects,
    get_recommendations,
    suggest_tech_stack,
    get_pitfalls_to_avoid,
    get_lessons_db,
    PatternCategory,
)
from agent.supabase_client import configure_supabase, get_supabase_client

# Load environment variables
load_dotenv()

# Initialize MCP server
mcp = FastMCP("playbook")

# Get playbook directory
PLAYBOOK_DIR = Path(__file__).parent.parent / "playbook"

# Configure Supabase if environment variables are set
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")
team_id = os.getenv("PLAYBOOK_TEAM_ID")

if supabase_url and supabase_key and team_id and team_id != "pending":
    db = configure_supabase(supabase_url, supabase_key, team_id)
    SUPABASE_ENABLED = db.is_configured
else:
    SUPABASE_ENABLED = False
    db = None

# In-memory session storage (fallback when Supabase not configured)
# Stores OrchestratorState objects
sessions: dict[str, OrchestratorState] = {}


async def _reconstruct_state_from_supabase(data: dict) -> OrchestratorState | None:
    """Reconstruct OrchestratorState from Supabase data."""
    from agent.models.project import (
        ProjectState,
        Phase,
        AutonomyMode,
        ProjectType,
        ScalePhase,
        TechStack,
        Feature,
    )

    try:
        phase_data = data.get("phase_data", {})

        # Reconstruct tech_stack
        tech_stack_data = data.get("tech_stack") or {}
        tech_stack = TechStack(
            frontend=tech_stack_data.get("frontend"),
            backend=tech_stack_data.get("backend"),
            database=tech_stack_data.get("database"),
            auth=tech_stack_data.get("auth"),
            deployment=tech_stack_data.get("deployment"),
            extras=tech_stack_data.get("extras", {}),
        )

        # Reconstruct features
        features = []
        for f_data in phase_data.get("features", []):
            features.append(Feature(
                name=f_data.get("name", ""),
                description=f_data.get("description", ""),
                status=f_data.get("status", "pending"),
                plan=f_data.get("plan"),
                files=f_data.get("files", []),
                tests=f_data.get("tests", []),
            ))

        # Reconstruct project type
        project_type = None
        if data.get("project_type"):
            try:
                project_type = ProjectType(data["project_type"])
            except ValueError:
                pass

        # Reconstruct project state
        project = ProjectState(
            id=data["session_id"],
            objective=data["objective"],
            current_phase=Phase(data.get("current_phase", "discovery")),
            mode=AutonomyMode(phase_data.get("mode", "supervised")),
            project_type=project_type,
            scale=ScalePhase(phase_data.get("scale", "mvp")),
            tech_stack=tech_stack,
            features=features,
            current_feature_index=phase_data.get("current_feature_index", 0),
            discovery_answers=phase_data.get("discovery_answers", {}),
            needs_user_input=phase_data.get("needs_user_input", True),
            claude_md=data.get("claude_md"),
            prd=data.get("prd"),
            roadmap=data.get("roadmap", []),
            implementation_plans=data.get("implementation_plans", {}),
            deployment_configs=data.get("deployment_configs", {}),
        )

        # Reconstruct orchestrator state
        return OrchestratorState(
            project=project,
            discovery_question_index=phase_data.get("discovery_question_index", 0),
        )
    except Exception as e:
        print(f"Error reconstructing state: {e}")
        return None


@mcp.tool(name="playbook_start_project")
async def start_project(objective: str, mode: str = "supervised") -> str:
    """
    Start a new project with the AI Project Playbook Agent.

    Args:
        objective: What you want to build (e.g., "a SaaS for veterinary clinics")
        mode: Autonomy mode - "supervised" (default), "autonomous", or "plan_only"

    Returns:
        Session ID and first question from Discovery phase
    """
    # Create initial state using the orchestrator
    state = create_initial_state(objective, mode)
    session_id = state.project.id

    # Run the orchestrator to get the first output
    result = run_orchestrator(state)

    # Store the state locally
    sessions[session_id] = result

    # Sync to Supabase if enabled (for team sharing)
    if SUPABASE_ENABLED and db:
        await db.save_orchestrator_state(result)

    return f"""
**Session Started: `{session_id}`**
**Mode: {mode}**
**Shared with team: {SUPABASE_ENABLED}**

{result.agent_output}

---
*Use `playbook_answer` with session_id="{session_id}" to respond.*
"""


@mcp.tool(name="playbook_answer")
async def answer_question(session_id: str, answer: str) -> str:
    """
    Answer a question from the agent and continue the workflow.

    Args:
        session_id: The session ID from start_project
        answer: Your answer to the agent's question

    Returns:
        Next question or action from the agent
    """
    # Try local first, then Supabase
    if session_id not in sessions:
        # Try to load from Supabase
        if SUPABASE_ENABLED and db:
            remote_data = await db.load_orchestrator_state(session_id)
            if remote_data:
                # Reconstruct state from Supabase data
                state = await _reconstruct_state_from_supabase(remote_data)
                if state:
                    sessions[session_id] = state

    if session_id not in sessions:
        return f"Error: Session '{session_id}' not found. Use `playbook_list_sessions` to see available sessions."

    # Get current state
    state = sessions[session_id]

    # Update state with user input and run orchestrator
    state.user_input = answer
    state.project.needs_user_input = False

    result = run_orchestrator(state)

    # Store updated state locally
    sessions[session_id] = result

    # Sync to Supabase
    if SUPABASE_ENABLED and db:
        await db.save_orchestrator_state(result)

    output = result.agent_output or "Processing..."

    if result.project.needs_user_input:
        output += f"\n\n---\n*Use `playbook_answer` with session_id=\"{session_id}\" to respond.*"

    return output


@mcp.tool(name="playbook_continue")
async def continue_project(session_id: str) -> str:
    """
    Continue a project from where it left off.

    Args:
        session_id: The session ID to continue

    Returns:
        Current state and next action
    """
    # Try local first, then Supabase
    if session_id not in sessions:
        # Try to load from Supabase
        if SUPABASE_ENABLED and db:
            remote_data = await db.load_orchestrator_state(session_id)
            if remote_data:
                state = await _reconstruct_state_from_supabase(remote_data)
                if state:
                    sessions[session_id] = state

    if session_id not in sessions:
        return f"Error: Session '{session_id}' not found. Use `playbook_list_sessions` to see available sessions."

    state = sessions[session_id]
    project = state.project

    # Build status summary
    ts = project.tech_stack
    tech_info = f"""
  - Frontend: {ts.frontend or "Not set"}
  - Backend: {ts.backend or "Not set"}
  - Database: {ts.database or "Not set"}
""" if ts.frontend or ts.backend or ts.database else "Not yet determined"

    features_count = len(project.features)
    current_feature = project.current_feature_index + 1 if project.features else "N/A"

    return f"""
## Continuing Session: {session_id}

**Objective**: {project.objective}
**Current Phase**: {project.current_phase.value}
**Mode**: {project.mode.value}

**Progress**:
- Project Type: {project.project_type.value if project.project_type else "Not set"}
- Scale: {project.scale.value}
- Tech Stack: {tech_info}
- Features: {features_count} defined
- Current Feature: {current_feature}

Reply with "continue" to proceed with the current phase.

---
*Use `playbook_answer` with session_id="{session_id}" to respond.*
"""


@mcp.tool(name="playbook_search")
async def search_playbook(query: str, search_type: str = "keyword", max_results: int = 5) -> str:
    """
    Search the AI Project Playbook for relevant guides.

    Args:
        query: What you're looking for (e.g., "deployment", "testing", "auth")
        search_type: Type of search - "keyword", "phase", or "topic"
        max_results: Maximum number of results (default 5)

    Returns:
        Matching sections from the playbook
    """
    return rag_search(query, search_type, max_results)


@mcp.tool(name="playbook_get_status")
async def get_project_status(session_id: str) -> str:
    """
    Get the current status of a project.

    Args:
        session_id: The session ID to check

    Returns:
        Detailed project status
    """
    if session_id not in sessions:
        return f"Error: Session '{session_id}' not found."

    state = sessions[session_id]
    project = state.project

    # Count feature progress
    total = len(project.features)
    completed = sum(1 for f in project.features if f.status == "completed")
    in_progress = sum(1 for f in project.features if f.status == "in_progress")

    # Tech stack info
    ts = project.tech_stack
    tech_info = json.dumps({
        "frontend": ts.frontend,
        "backend": ts.backend,
        "database": ts.database,
    }, indent=2) if ts.frontend or ts.backend or ts.database else "Not yet determined"

    status = f"""
## Project Status: {session_id}

### Overview
- **Objective**: {project.objective}
- **Type**: {project.project_type.value if project.project_type else "Not determined"}
- **Scale**: {project.scale.value}
- **Mode**: {project.mode.value}

### Phase Progress
- **Current Phase**: {project.current_phase.value}
- **Features**: {completed}/{total} completed ({in_progress} in progress)
- **Progress**: {project.progress_percentage:.0f}%

### Tech Stack
{tech_info}

### Generated Artifacts
- CLAUDE.md: {"Generated" if project.claude_md else "Pending"}
- PRD: {"Generated" if project.prd else "Pending"}
- Files Created: {len(project.files_created)}
"""

    if project.features:
        status += "\n### Features\n"
        for i, f in enumerate(project.features, 1):
            icon = {"pending": "[ ]", "in_progress": "[>]", "completed": "[x]"}.get(f.status, "[ ]")
            status += f"{icon} {i}. {f.name}\n"

    return status


@mcp.tool(name="playbook_list_sessions")
async def list_sessions() -> str:
    """
    List all active project sessions (local and team shared).

    Returns:
        List of session IDs and their objectives
    """
    output = "## Active Sessions\n\n"
    team_projects = []

    # Show local sessions
    if sessions:
        output += "### Local Sessions (this machine)\n"
        for sid, state in sessions.items():
            project = state.project
            progress = f"{project.progress_percentage:.0f}%" if project.features else "0%"
            output += f"- **{sid}**: {project.objective} ({project.current_phase.value}, {progress})\n"
        output += "\n"

    # Show team sessions from Supabase
    if SUPABASE_ENABLED and db:
        team_projects = await db.list_team_projects(limit=20, include_completed=False)
        if team_projects:
            output += "### Team Sessions (shared via Supabase)\n"
            for proj in team_projects:
                sid = proj["session_id"]
                obj = proj["objective"]
                phase = proj.get("current_phase", "discovery")
                created_by = proj.get("created_by", "unknown")
                repo_url = proj.get("repo_url", "")

                # Mark if already loaded locally
                local_mark = " *(loaded)*" if sid in sessions else ""
                repo_mark = f" | [repo]({repo_url})" if repo_url else ""
                output += f"- **{sid}**: {obj} ({phase}, by {created_by}){repo_mark}{local_mark}\n"

    if not sessions and not team_projects:
        return "No active sessions. Start a new project with `playbook_start_project`."

    output += "\n---\n*Use `playbook_continue` with a session_id to continue any project.*"
    return output


@mcp.tool(name="playbook_get_claude_md")
async def get_claude_md(session_id: str) -> str:
    """
    Get the generated CLAUDE.md content for a project.

    Args:
        session_id: The session ID

    Returns:
        CLAUDE.md content or error message
    """
    if session_id not in sessions:
        return f"Error: Session '{session_id}' not found."

    state = sessions[session_id]
    if not state.project.claude_md:
        return "CLAUDE.md has not been generated yet. Complete the Planning phase first."

    return f"""
## CLAUDE.md for Session {session_id}

```markdown
{state.project.claude_md}
```

*Copy this content to your project's CLAUDE.md file.*
"""


@mcp.tool(name="playbook_get_prp")
async def get_prp(session_id: str, feature_name: str = "") -> str:
    """
    Get a feature plan in PRP (Project Requirements Plan) format.

    If feature_name is provided, returns the plan for that specific feature.
    Otherwise returns the PRD with PRP annotations.

    Args:
        session_id: The session ID
        feature_name: Optional feature name to get specific plan

    Returns:
        PRP-formatted plan or error message
    """
    if session_id not in sessions:
        return f"Error: Session '{session_id}' not found."

    state = sessions[session_id]
    project = state.project

    if feature_name:
        # Find the specific feature
        feature = None
        for f in project.features:
            if f.name.lower() == feature_name.lower():
                feature = f
                break

        if not feature:
            available = ", ".join(f.name for f in project.features)
            return f"Feature '{feature_name}' not found. Available: {available}"

        # Generate PRP-style plan for the feature
        from agent.orchestrator import generate_feature_plan, generate_validation_loop
        plan = generate_feature_plan(
            feature.name, feature.description,
            project.tech_stack, project.project_type,
        )
        validation = generate_validation_loop(project.tech_stack)

        # Get quality score if available
        plan_score = project.validation_results.get(f"plan_{feature.name}_score", "N/A")

        return f"""## PRP: {feature.name}

### Goal
{feature.description}

### Context
- **Project**: {project.objective}
- **Type**: {project.project_type.value if project.project_type else "N/A"}
- **Tech Stack**: {project.tech_stack.frontend or "N/A"} + {project.tech_stack.backend or "N/A"} + {project.tech_stack.database or "N/A"}
- **Quality Score**: {plan_score}

### Implementation Blueprint
{plan}

### Validation Loop
{validation}

### Anti-Patterns
- Do NOT leave TODOs or placeholder code
- Do NOT skip tests for "simple" features
- Do NOT hardcode configuration values
- Do NOT ignore error handling at API boundaries
"""
    else:
        # Return PRD with PRP annotations
        if not project.prd:
            return "PRD has not been generated yet. Complete the Planning phase first."

        return f"""## PRP Overview for Session {session_id}

### Project
- **Objective**: {project.objective}
- **Type**: {project.project_type.value if project.project_type else "N/A"}
- **Features**: {len(project.features)} defined

### PRD Content
```markdown
{project.prd}
```

### Feature Plans Available
Use `playbook_get_prp session_id="{session_id}" feature_name="<name>"` for detailed PRP:

{chr(10).join(f'- **{f.name}**: {f.description}' for f in project.features)}
"""


@mcp.tool(name="playbook_get_prd")
async def get_prd(session_id: str) -> str:
    """
    Get the generated PRD content for a project.

    Args:
        session_id: The session ID

    Returns:
        PRD content or error message
    """
    if session_id not in sessions:
        return f"Error: Session '{session_id}' not found."

    state = sessions[session_id]
    if not state.project.prd:
        return "PRD has not been generated yet. Complete the Planning phase first."

    return f"""
## PRD for Session {session_id}

```markdown
{state.project.prd}
```

*Copy this content to your project's docs/PRD.md file.*
"""


# =============================================================================
# Artifact Evaluation Tools
# =============================================================================


@mcp.tool(name="playbook_system_review")
async def system_review(session_id: str) -> str:
    """
    Generate a system review for a project.

    Meta-analysis of plan vs execution that evaluates process quality,
    artifact quality, and execution confidence. Analyzes the SYSTEM,
    not just the code.

    Args:
        session_id: The session ID to review

    Returns:
        Comprehensive system review report with confidence score (1-10)
    """
    if session_id not in sessions:
        return f"Error: Session '{session_id}' not found."

    from agent.system_review import generate_system_review

    state = sessions[session_id]
    return generate_system_review(state.project)


@mcp.tool(name="playbook_evaluate_artifact")
async def evaluate_artifact(artifact_type: str, content: str) -> str:
    """
    Evaluate the quality of a generated artifact.

    Runs rule-based checks on CLAUDE.md, PRD, or feature plans to ensure
    they meet quality standards before use.

    Args:
        artifact_type: Type of artifact - "claude_md", "prd", or "plan"
        content: The artifact content to evaluate

    Returns:
        Quality report with score, checks passed/failed, and suggestions
    """
    from agent.evals import ArtifactEvaluator

    evaluator = ArtifactEvaluator()
    result = evaluator.evaluate(artifact_type, content)

    output = f"""## Artifact Evaluation

{result.format_report()}

### Summary
- **Type**: {artifact_type}
- **Score**: {result.score:.0%}
- **Status**: {"PASSED" if result.passed else "NEEDS IMPROVEMENT"}
- **Checks**: {sum(1 for c in result.checks if c.passed)}/{len(result.checks)} passed
"""

    if result.suggestions:
        output += "\n### How to Improve\n"
        for i, suggestion in enumerate(result.suggestions, 1):
            output += f"{i}. {suggestion}\n"

    return output


# =============================================================================
# Agent Factory Tools - Specialized Agents
# =============================================================================


@mcp.tool(name="playbook_run_task")
async def run_task(task: str) -> str:
    """
    Run a development task through the appropriate specialized agent.

    The task is automatically routed to the best agent based on keywords:
    - Research tasks: "find", "search", "lookup", "research", "what is", "how to"
    - Planning tasks: "plan", "design", "architect", "break down", "outline"
    - Coding tasks: "implement", "write", "code", "create", "build", "fix"
    - Review tasks: "review", "check", "analyze", "audit", "inspect"
    - Testing tasks: "test", "verify", "validate", "coverage"

    Args:
        task: Description of the task to perform

    Returns:
        Result from the specialized agent
    """
    result = await run_development_task(task)

    output = f"""## Task Result

**Agent Used**: {result.get("agent_used", "unknown")}
**Success**: {"✅" if result["success"] else "❌"}

### Output

{result["output"]}
"""

    if result.get("errors"):
        output += f"\n### Errors\n"
        for error in result["errors"]:
            output += f"- {error}\n"

    return output


@mcp.tool(name="playbook_run_pipeline")
async def run_pipeline(feature: str) -> str:
    """
    Run a feature through the full development pipeline.

    Pipeline stages: Research → Plan → Code → Review → Test

    Each stage builds on the previous one's output. The pipeline stops
    if any stage fails.

    Args:
        feature: Description of the feature to implement

    Returns:
        Results from all pipeline stages
    """
    result = await run_feature_pipeline(feature)

    output = f"""## Pipeline Result: {feature}

**Success**: {"✅" if result["success"] else "❌"}
**Stages Completed**: {result.get("stages_completed", 0)}/5

### Final Output

{result["output"]}

### Execution Log
"""

    for log_entry in result.get("execution_log", []):
        stage = log_entry.get("stage", "unknown")
        success = "✅" if log_entry.get("success") else "❌"
        output += f"- {success} {stage}\n"

    if result.get("errors"):
        output += f"\n### Errors\n"
        for error in result["errors"]:
            output += f"- {error}\n"

    return output


@mcp.tool(name="playbook_code_review")
async def code_review(code: str, code_type: str = "generic") -> str:
    """
    Run parallel code reviews on provided code.

    Runs multiple reviewers in parallel:
    - Quality Reviewer: Code quality, naming, structure
    - Security Reviewer: Security vulnerabilities, best practices

    Args:
        code: The code to review
        code_type: Type of code - "api_endpoint", "service", "component", "test", "generic"

    Returns:
        Combined review results from all reviewers
    """
    parallel_reviewers = create_code_review_parallel()

    context = AgentContext(
        task=f"Review this {code_type} code",
        shared_state={
            "generated_code": code,
            "code_type": code_type,
        }
    )

    result = await parallel_reviewers.execute(context)

    output = f"""## Parallel Code Review

**Success**: {"✅" if result.success else "❌"}

### Review Results

{result.output}
"""

    if result.errors:
        output += f"\n### Errors\n"
        for error in result.errors:
            output += f"- {error}\n"

    return output


@mcp.tool(name="playbook_supervised_task")
async def supervised_task(task: str, max_iterations: int = 5) -> str:
    """
    Run a task with the supervisor pattern.

    The supervisor coordinates multiple agents dynamically based on
    task requirements. It decides which agent to use at each step
    and orchestrates the workflow.

    Available agents:
    - researcher: Searches playbook for information
    - planner: Creates implementation plans
    - coder: Generates code
    - reviewer: Reviews code quality
    - tester: Generates tests

    Args:
        task: The task to complete
        max_iterations: Maximum number of agent invocations (default 5)

    Returns:
        Final result after supervisor coordination
    """
    # Configure supervisor with max iterations
    default_supervisor.max_iterations = max_iterations

    context = AgentContext(task=task)
    result = await default_supervisor.execute(context)

    output = f"""## Supervised Task Result

**Success**: {"✅" if result.success else "❌"}
**Iterations**: {result.metadata.get("iterations", 0)}/{max_iterations}

### Output

{result.output}

### Execution History
"""

    for entry in result.metadata.get("history", []):
        agent = entry.get("agent", "unknown")
        success = "✅" if entry.get("success") else "❌"
        output += f"- {success} {agent}: {entry.get('task', '')[:50]}...\n"

    if result.errors:
        output += f"\n### Errors\n"
        for error in result.errors:
            output += f"- {error}\n"

    return output


@mcp.tool(name="playbook_research")
async def research_topic(topic: str) -> str:
    """
    Research a topic using the Researcher agent.

    Searches the playbook for relevant information and synthesizes findings.

    Args:
        topic: What to research (e.g., "authentication best practices", "deployment strategies")

    Returns:
        Research findings with playbook references
    """
    from agent.specialized import ResearcherAgent

    researcher = ResearcherAgent()
    context = AgentContext(task=topic)
    result = await researcher.execute(context)

    output = f"""## Research: {topic}

{result.output}
"""

    if result.data.get("sources"):
        output += "\n### Sources\n"
        for source in result.data["sources"]:
            output += f"- {source}\n"

    return output


@mcp.tool(name="playbook_plan_feature")
async def plan_feature(feature: str) -> str:
    """
    Create an implementation plan for a feature.

    Generates a detailed, phased plan with:
    - Step-by-step tasks
    - Files to create/modify
    - Validation commands
    - Testing requirements

    Args:
        feature: The feature to plan (e.g., "user authentication", "API endpoints")

    Returns:
        Detailed implementation plan
    """
    from agent.specialized import PlannerAgent

    planner = PlannerAgent()
    context = AgentContext(task=feature)
    result = await planner.execute(context)

    return result.output


@mcp.tool(name="playbook_generate_code")
async def generate_code(task: str, code_type: str = "generic") -> str:
    """
    Generate code for a specific task.

    Supported code types:
    - api_endpoint: FastAPI router with Pydantic schemas
    - data_model: Pydantic models with base entity
    - service: Service class with repository pattern
    - component: React component with TypeScript
    - test: pytest test class
    - generic: Basic Python script

    Args:
        task: What to implement (e.g., "create user registration endpoint")
        code_type: Type of code to generate

    Returns:
        Generated code with implementation notes
    """
    from agent.specialized import CoderAgent

    coder = CoderAgent()
    context = AgentContext(
        task=task,
        shared_state={"code_type": code_type}
    )
    result = await coder.execute(context)

    return result.output


@mcp.tool(name="playbook_generate_tests")
async def generate_tests(code: str, code_type: str = "generic") -> str:
    """
    Generate tests for provided code.

    Creates appropriate tests based on code type:
    - api_endpoint: HTTP client tests with pytest-asyncio
    - service: Unit tests with mocks
    - data_model: Model validation tests
    - component: React Testing Library tests
    - generic: Basic pytest tests

    Args:
        code: The code to test
        code_type: Type of code being tested

    Returns:
        Generated test code with validation commands
    """
    from agent.specialized import TesterAgent

    tester = TesterAgent()
    context = AgentContext(
        task=f"Generate tests for {code_type} code",
        shared_state={
            "generated_code": code,
            "code_type": code_type,
        }
    )
    result = await tester.execute(context)

    return result.output


# =============================================================================
# Meta-Learning Tools - Learn from Past Projects
# =============================================================================


@mcp.tool(name="playbook_complete_project")
async def complete_project(session_id: str, user_rating: int = 4, notes: str = "") -> str:
    """
    Mark a project as complete and capture lessons learned.

    This triggers the meta-learning system to:
    - Analyze what worked and what didn't
    - Extract patterns for future projects
    - Store the outcome for recommendations

    Args:
        session_id: The session ID to complete
        user_rating: Rating from 1-5 (5 = excellent)
        notes: Optional notes about the project

    Returns:
        Summary of captured lessons
    """
    if session_id not in sessions:
        return f"Error: Session '{session_id}' not found."

    state = sessions[session_id]
    project = state.project

    # Capture outcome
    outcome = capture_project_outcome(project)

    # Update with user feedback
    outcome.user_rating = user_rating
    outcome.user_notes = notes if notes else None

    db = get_lessons_db()
    db.add_outcome(outcome)

    output = f"""## Project Completed: {session_id}

### Outcome Summary
- **Result**: {outcome.outcome.value}
- **Success Score**: {outcome.success_score:.0%}
- **Features Completed**: {len(outcome.features_completed)}/{len(outcome.features_planned)}
- **Your Rating**: {"⭐" * user_rating}

### What Worked
"""
    for item in outcome.what_worked:
        output += f"- ✅ {item}\n"

    output += "\n### What Didn't Work\n"
    for item in outcome.what_didnt_work:
        output += f"- ❌ {item}\n"

    # Get stats
    stats = db.get_stats()
    output += f"""
### Meta-Learning Stats
- **Total Lessons Captured**: {stats['total_lessons']}
- **Projects Analyzed**: {stats['total_outcomes']}
- **Overall Success Rate**: {stats['success_rate']:.0%}

_Lessons from this project will improve recommendations for future projects._
"""

    return output


@mcp.tool(name="playbook_get_recommendations")
async def get_project_recommendations(
    project_type: str,
    tech_stack: str = "",
    phase: str = "",
) -> str:
    """
    Get recommendations based on lessons from past projects.

    Args:
        project_type: Type of project (saas, api, agent, multi_agent)
        tech_stack: Comma-separated list of technologies (e.g., "Next.js, FastAPI, Supabase")
        phase: Current phase (discovery, planning, roadmap, implementation, deployment)

    Returns:
        Personalized recommendations based on learned patterns
    """
    tech_list = [t.strip() for t in tech_stack.split(",") if t.strip()] if tech_stack else []

    recommendations = get_recommendations(
        project_type=project_type,
        tech_stack=tech_list,
        current_phase=phase if phase else None,
    )

    output = f"""## Recommendations for {project_type.title()} Project

Based on patterns from previous projects:

"""
    for i, rec in enumerate(recommendations, 1):
        output += f"{i}. {rec}\n\n"

    # Add pitfalls
    pitfalls = get_pitfalls_to_avoid(project_type, tech_list)
    if pitfalls:
        output += "### Pitfalls to Avoid\n\n"
        for pitfall in pitfalls[:3]:
            output += f"{pitfall}\n\n"

    return output


@mcp.tool(name="playbook_find_similar")
async def find_similar(
    project_type: str,
    tech_stack: str = "",
    limit: int = 3,
) -> str:
    """
    Find similar past projects to learn from.

    Args:
        project_type: Type of project to match
        tech_stack: Comma-separated list of technologies
        limit: Maximum projects to return (default 3)

    Returns:
        Similar projects with their outcomes and lessons
    """
    tech_list = [t.strip() for t in tech_stack.split(",") if t.strip()] if tech_stack else []

    similar = find_similar_projects(
        project_type=project_type,
        tech_stack=tech_list,
        limit=limit,
    )

    if not similar:
        return f"""## No Similar Projects Found

No past projects match your criteria. This will be the first {project_type} project tracked!

As you complete projects, the system will learn patterns and provide better recommendations.
"""

    output = f"""## Similar Past Projects

Found {len(similar)} similar projects:

"""
    for i, proj in enumerate(similar, 1):
        stars = "⭐" * int(proj["success_score"] * 5)
        output += f"""### {i}. {proj['objective'][:50]}...

- **Type**: {proj['project_type']}
- **Tech Stack**: {', '.join(v for v in proj['tech_stack'].values() if v)}
- **Outcome**: {proj['outcome']} {stars}
- **Similarity**: {proj['similarity']:.0%}

**What Worked**: {', '.join(proj['what_worked']) if proj['what_worked'] else 'N/A'}

**What Didn't Work**: {', '.join(proj['what_didnt_work']) if proj['what_didnt_work'] else 'N/A'}

---

"""

    return output


@mcp.tool(name="playbook_suggest_stack")
async def suggest_stack(project_type: str) -> str:
    """
    Get tech stack suggestions based on successful past projects.

    Args:
        project_type: Type of project (saas, api, agent, multi_agent)

    Returns:
        Recommended technologies for each layer
    """
    suggestions = suggest_tech_stack(project_type)

    output = f"""## Suggested Tech Stack for {project_type.title()}

Based on successful past projects:

### Frontend
"""
    if suggestions["frontend"]:
        for i, tech in enumerate(suggestions["frontend"][:3], 1):
            output += f"{i}. {tech}\n"
    else:
        output += "_No frontend needed for this project type_\n"

    output += "\n### Backend\n"
    for i, tech in enumerate(suggestions["backend"][:3], 1):
        output += f"{i}. {tech}\n"

    output += "\n### Database\n"
    for i, tech in enumerate(suggestions["database"][:3], 1):
        output += f"{i}. {tech}\n"

    output += """
---

_Suggestions are based on patterns from successfully completed projects._
_Your specific requirements may warrant different choices._
"""

    return output


@mcp.tool(name="playbook_learning_stats")
async def learning_stats() -> str:
    """
    Get statistics about the meta-learning system.

    Returns:
        Summary of lessons learned and patterns captured
    """
    db = get_lessons_db()
    stats = db.get_stats()

    output = f"""## Meta-Learning Statistics

### Overview
- **Total Lessons Captured**: {stats['total_lessons']}
- **Projects Analyzed**: {stats['total_outcomes']}
- **Overall Success Rate**: {stats['success_rate']:.0%}

### Lessons by Category
"""
    for category, count in stats['lessons_by_category'].items():
        if count > 0:
            output += f"- **{category.replace('_', ' ').title()}**: {count} lessons\n"

    if stats['top_lessons']:
        output += "\n### Most Common Patterns\n"
        for lesson in stats['top_lessons']:
            output += f"- {lesson['title']} (seen {lesson['frequency']}x)\n"
    else:
        output += "\n_No patterns captured yet. Complete some projects to start learning!_\n"

    return output


@mcp.tool(name="playbook_add_lesson")
async def add_lesson(
    title: str,
    description: str,
    recommendation: str,
    category: str = "workflow",
    project_type: str = "",
    tags: str = "",
) -> str:
    """
    Manually add a lesson learned.

    Args:
        title: Short title for the lesson
        description: What happened or was observed
        recommendation: What to do differently
        category: Category (tech_stack, architecture, workflow, tooling, testing, deployment, pitfall)
        project_type: Where this applies (saas, api, agent, multi_agent)
        tags: Comma-separated tags

    Returns:
        Confirmation of added lesson
    """
    from agent.meta_learning.models import LessonLearned

    try:
        cat = PatternCategory(category)
    except ValueError:
        return f"Invalid category '{category}'. Valid options: {', '.join(c.value for c in PatternCategory)}"

    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
    project_types = [project_type] if project_type else []

    lesson = LessonLearned(
        category=cat,
        title=title,
        description=description,
        context="Manually added lesson",
        recommendation=recommendation,
        confidence=0.7,
        project_types=project_types,
        tags=tag_list,
    )

    db = get_lessons_db()
    db.add_lesson(lesson)

    return f"""## Lesson Added

**{title}**

- **Category**: {category}
- **Description**: {description}
- **Recommendation**: {recommendation}
- **Tags**: {', '.join(tag_list) if tag_list else 'None'}

_This lesson will be used in future recommendations._
"""


# ============================================
# SUPABASE TOOLS (Team Shared Knowledge)
# ============================================

@mcp.tool(name="playbook_team_status")
async def team_status() -> str:
    """
    Check Supabase connection and team configuration status.

    Returns:
        Connection status and team information
    """
    output = "## Team Configuration Status\n\n"

    if not SUPABASE_ENABLED:
        output += """### ❌ Supabase Not Configured

The agent is running in **local mode**. Lessons and projects are stored locally
and NOT shared with your team.

**To enable team sharing:**

1. Create a Supabase project at https://supabase.com
2. Run the schema SQL from `supabase/schema.sql`
3. Set environment variables:
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your-anon-key
   PLAYBOOK_TEAM_ID=your-team-uuid
   ```
4. Restart the MCP server

---

**Current Mode**: Local (JSON file storage)
"""
    else:
        # Try to get team info
        team_info = await db.get_team()
        lessons_stats = await db.get_lessons_stats()

        output += f"""### ✅ Supabase Connected

**Team**: {team_info['name'] if team_info else 'Unknown'}
**Team ID**: {team_id[:8]}...

### Shared Knowledge Base
- **Total Lessons**: {lessons_stats['total']}
- **By Category**:
"""
        for cat, count in lessons_stats.get('by_category', {}).items():
            output += f"  - {cat}: {count}\n"

        output += """
---

All lessons and project outcomes are shared with your team.
"""

    return output


@mcp.tool(name="playbook_share_lesson")
async def share_lesson(
    title: str,
    description: str,
    recommendation: str,
    category: str = "workflow",
    project_type: str = "",
    tech_stack: str = "",
    tags: str = "",
) -> str:
    """
    Share a lesson with the team (saves to Supabase).

    Args:
        title: Short title for the lesson
        description: What happened or was observed
        recommendation: What to do differently
        category: Category (tech_stack, architecture, workflow, tooling, testing, deployment, pitfall)
        project_type: Where this applies (saas, api, agent, multi_agent)
        tech_stack: Comma-separated technologies this applies to
        tags: Comma-separated tags

    Returns:
        Confirmation of shared lesson
    """
    if not SUPABASE_ENABLED:
        return """## ❌ Team Sharing Not Available

Supabase is not configured. The lesson will be saved locally only.

Use `playbook_team_status` to see how to configure team sharing.
"""

    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
    tech_list = [t.strip() for t in tech_stack.split(",") if t.strip()] if tech_stack else []
    project_types = [project_type] if project_type else []

    result = await db.add_lesson(
        category=category,
        title=title,
        description=description,
        recommendation=recommendation,
        project_types=project_types,
        tech_stacks=tech_list,
        tags=tag_list,
        contributed_by=os.getenv("PLAYBOOK_USER", "unknown"),
    )

    if result:
        return f"""## ✅ Lesson Shared with Team

**{title}**

- **Category**: {category}
- **Description**: {description}
- **Recommendation**: {recommendation}
- **Technologies**: {', '.join(tech_list) if tech_list else 'Any'}
- **Tags**: {', '.join(tag_list) if tag_list else 'None'}
- **Contributed by**: {os.getenv("PLAYBOOK_USER", "unknown")}

_This lesson is now available to all team members._
"""
    else:
        return "## ❌ Failed to share lesson. Check Supabase connection."


@mcp.tool(name="playbook_team_lessons")
async def team_lessons(
    category: str = "",
    project_type: str = "",
    limit: int = 10,
) -> str:
    """
    Get lessons shared by the team.

    Args:
        category: Filter by category (optional)
        project_type: Filter by project type (optional)
        limit: Maximum lessons to return (default 10)

    Returns:
        List of team lessons
    """
    if not SUPABASE_ENABLED:
        return """## ❌ Team Sharing Not Available

Supabase is not configured. Use `playbook_team_status` to see how to configure.
"""

    lessons = await db.get_lessons(
        category=category if category else None,
        project_type=project_type if project_type else None,
        limit=limit,
    )

    if not lessons:
        return f"""## No Lessons Found

No lessons match your criteria. Be the first to share one with `playbook_share_lesson`!
"""

    output = f"""## Team Lessons ({len(lessons)} found)

"""
    for lesson in lessons:
        votes = lesson.get('upvotes', 0) - lesson.get('downvotes', 0)
        vote_str = f"+{votes}" if votes > 0 else str(votes)

        output += f"""### {lesson['title']}

- **Category**: {lesson['category']}
- **Confidence**: {lesson['confidence']:.0%}
- **Votes**: {vote_str}
- **Used**: {lesson['frequency']}x

**Description**: {lesson['description']}

**Recommendation**: {lesson['recommendation']}

---

"""

    return output


@mcp.tool(name="playbook_link_repo")
async def link_repo(session_id: str, repo_url: str = "") -> str:
    """
    Link a GitHub repository URL to a project.

    This allows team members to know where the code lives for any project.
    If no repo_url is provided, it will try to detect the Git remote from
    the current directory.

    Args:
        session_id: The project session ID
        repo_url: GitHub repository URL (e.g., https://github.com/user/repo)
                  If empty, will try to auto-detect from git remote

    Returns:
        Confirmation message with the linked repo
    """
    if not SUPABASE_ENABLED:
        return """## ❌ Repository Linking Not Available

Supabase is not configured. Repository URLs are stored in the team database.
Use `playbook_team_status` to see how to configure.
"""

    # Validate session exists
    if session_id not in sessions:
        # Try to load from Supabase
        data = await db.load_orchestrator_state(session_id)
        if not data:
            return f"## ❌ Session `{session_id}` not found."

    # If no URL provided, try to get current repo URL
    final_url = repo_url.strip()
    if not final_url:
        return """## ❌ No Repository URL Provided

Please provide the repository URL. Example:
```
playbook_link_repo session_id="abc123" repo_url="https://github.com/user/repo"
```

Or run `git remote get-url origin` in your project directory to get the URL.
"""

    # Basic validation
    if not (final_url.startswith("https://github.com/") or
            final_url.startswith("git@github.com:") or
            final_url.startswith("https://gitlab.com/") or
            final_url.startswith("https://bitbucket.org/")):
        return f"""## ⚠️ Invalid Repository URL

The URL `{final_url}` doesn't look like a valid repository URL.

Expected formats:
- `https://github.com/username/repo`
- `git@github.com:username/repo.git`
- `https://gitlab.com/username/repo`
"""

    # Link the repo
    success = await db.link_repo(session_id, final_url)

    if success:
        return f"""## ✅ Repository Linked

**Session**: `{session_id}`
**Repository**: {final_url}

Team members can now see where the code lives when they list projects.
"""
    else:
        return "## ❌ Failed to link repository. Check Supabase connection."


@mcp.tool(name="playbook_get_repo")
async def get_repo(session_id: str) -> str:
    """
    Get the repository URL for a project.

    Args:
        session_id: The project session ID

    Returns:
        Repository URL or message if not linked
    """
    if not SUPABASE_ENABLED:
        return "## ❌ Supabase not configured."

    repo_url = await db.get_repo_url(session_id)

    if repo_url:
        return f"""## Repository for `{session_id}`

**URL**: {repo_url}

Clone with:
```bash
git clone {repo_url}
```
"""
    else:
        return f"""## No Repository Linked

Session `{session_id}` doesn't have a repository linked yet.

Use `playbook_link_repo` to associate a repository:
```
playbook_link_repo session_id="{session_id}" repo_url="https://github.com/..."
```
"""


def main():
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
