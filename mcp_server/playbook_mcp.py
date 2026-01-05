"""
AI Project Playbook MCP Server

Exposes the AI Project Playbook Agent as an MCP server for Claude Code integration.
Uses LangGraph orchestrator for phase management.
Includes Agent Factory for multi-agent patterns and specialized agents.
"""

import asyncio
import json
from pathlib import Path

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

# Initialize MCP server
mcp = FastMCP("playbook")

# Get playbook directory
PLAYBOOK_DIR = Path(__file__).parent.parent / "playbook"

# In-memory session storage (will be replaced with Supabase)
# Stores OrchestratorState objects
sessions: dict[str, OrchestratorState] = {}


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

    # Store the state
    sessions[session_id] = result

    return f"""
**Session Started: `{session_id}`**
**Mode: {mode}**

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
    if session_id not in sessions:
        return f"Error: Session '{session_id}' not found. Start a new project with playbook_start_project."

    # Get current state
    state = sessions[session_id]

    # Update state with user input and run orchestrator
    state.user_input = answer
    state.project.needs_user_input = False

    result = run_orchestrator(state)

    # Store updated state
    sessions[session_id] = result

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
    if session_id not in sessions:
        return f"Error: Session '{session_id}' not found."

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
    List all active project sessions.

    Returns:
        List of session IDs and their objectives
    """
    if not sessions:
        return "No active sessions. Start a new project with `playbook_start_project`."

    output = "## Active Sessions\n\n"
    for sid, state in sessions.items():
        project = state.project
        progress = f"{project.progress_percentage:.0f}%" if project.features else "0%"
        output += f"- **{sid}**: {project.objective} ({project.current_phase.value}, {progress})\n"

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


def main():
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
