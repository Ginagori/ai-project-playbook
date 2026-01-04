"""
AI Project Playbook MCP Server

Exposes the AI Project Playbook Agent as an MCP server for Claude Code integration.
Uses LangGraph orchestrator for phase management.
"""

import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from agent.orchestrator import (
    OrchestratorState,
    create_initial_state,
    run_orchestrator,
)
from agent.tools.playbook_rag import search_playbook as rag_search

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


def main():
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
