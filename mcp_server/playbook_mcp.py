"""
AI Project Playbook MCP Server

Exposes the AI Project Playbook Agent as an MCP server for Claude Code integration.
"""

import os
import json
import uuid
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("playbook")

# Get playbook directory
PLAYBOOK_DIR = Path(__file__).parent.parent / "playbook"

# In-memory session storage (will be replaced with Supabase)
sessions: dict[str, dict[str, Any]] = {}


def generate_session_id() -> str:
    """Generate a unique session ID."""
    return str(uuid.uuid4())[:8]


def search_playbook_files(query: str, max_results: int = 5) -> list[dict[str, str]]:
    """
    Simple keyword search in playbook files.
    Will be replaced with RAG using Supabase pgvector.
    """
    results = []
    query_lower = query.lower()

    for md_file in PLAYBOOK_DIR.rglob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")
            if query_lower in content.lower():
                # Get first 500 chars as snippet
                snippet = content[:500].replace("\n", " ")
                results.append({
                    "file": str(md_file.relative_to(PLAYBOOK_DIR)),
                    "snippet": snippet,
                })
                if len(results) >= max_results:
                    break
        except Exception:
            continue

    return results


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
    session_id = generate_session_id()

    # Initialize session state
    sessions[session_id] = {
        "objective": objective,
        "mode": mode,
        "current_phase": "discovery",
        "project_type": None,
        "scale": None,
        "tech_stack": None,
        "claude_md": None,
        "prd": None,
        "features": [],
        "current_feature": 0,
        "files_created": [],
        "answers": {},
    }

    # Start Discovery phase
    first_question = """
## Discovery Phase - Understanding Your Project

Based on your objective: **{objective}**

I need to understand a few things to recommend the best approach.

**Question 1 of 5: What type of project is this?**

1. **SaaS Application** - Multi-tenant web app with users, subscriptions, etc.
2. **API Backend** - REST/GraphQL API for mobile apps or integrations
3. **Agent System** - Single AI agent with tools and memory
4. **Multi-Agent System** - Multiple AI agents working together

Please respond with the number (1-4) or describe if it's something else.
""".format(objective=objective)

    return f"""
**Session Started: `{session_id}`**
**Mode: {mode}**

{first_question}

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

    session = sessions[session_id]
    phase = session["current_phase"]

    if phase == "discovery":
        return await _handle_discovery(session_id, answer)
    elif phase == "planning":
        return await _handle_planning(session_id, answer)
    elif phase == "roadmap":
        return await _handle_roadmap(session_id, answer)
    elif phase == "implementation":
        return await _handle_implementation(session_id, answer)
    else:
        return f"Unknown phase: {phase}"


async def _handle_discovery(session_id: str, answer: str) -> str:
    """Handle Discovery phase questions."""
    session = sessions[session_id]
    answers = session["answers"]

    # Track which question we're on
    question_count = len(answers)
    answers[f"q{question_count + 1}"] = answer

    if question_count == 0:
        # Project type answered
        type_map = {"1": "saas", "2": "api", "3": "agent", "4": "multi-agent"}
        session["project_type"] = type_map.get(answer.strip(), answer)

        return """
**Question 2 of 5: What scale do you expect?**

1. **MVP** (<100 users) - Validate idea, $300-500/month
2. **Growth** (100-10K users) - Scaling up, $1,500-3,000/month
3. **Scale** (10K-100K users) - Established product, $8,000-15,000/month
4. **Enterprise** (100K+ users) - Large scale, $50,000+/month

Which phase are you targeting initially?
"""

    elif question_count == 1:
        # Scale answered
        scale_map = {"1": "mvp", "2": "growth", "3": "scale", "4": "enterprise"}
        session["scale"] = scale_map.get(answer.strip(), "mvp")

        return """
**Question 3 of 5: Frontend preference?**

1. **React + Vite** - Modern, fast, great ecosystem
2. **Next.js** - Full-stack React with SSR
3. **Vue + Nuxt** - Progressive framework
4. **None** - API only, no frontend

Which do you prefer?
"""

    elif question_count == 2:
        # Frontend answered
        frontend_map = {
            "1": "react-vite",
            "2": "nextjs",
            "3": "vue-nuxt",
            "4": "none"
        }
        session["tech_stack"] = {"frontend": frontend_map.get(answer.strip(), "react-vite")}

        return """
**Question 4 of 5: Backend preference?**

1. **FastAPI (Python)** - Modern async, great for AI integrations
2. **Express (Node.js)** - Simple, flexible, large ecosystem
3. **Django (Python)** - Batteries included, admin panel
4. **Serverless** - Cloud Functions / Lambda

Which fits your needs?
"""

    elif question_count == 3:
        # Backend answered
        backend_map = {
            "1": "fastapi",
            "2": "express",
            "3": "django",
            "4": "serverless"
        }
        session["tech_stack"]["backend"] = backend_map.get(answer.strip(), "fastapi")

        return """
**Question 5 of 5: Database preference?**

1. **PostgreSQL + Supabase** - Recommended for most projects
2. **MongoDB** - Document database, flexible schema
3. **SQLite** - Simple, file-based (MVP only)
4. **Firebase** - Google's BaaS, real-time sync

Which do you prefer?
"""

    elif question_count == 4:
        # Database answered - Discovery complete!
        db_map = {
            "1": "postgresql-supabase",
            "2": "mongodb",
            "3": "sqlite",
            "4": "firebase"
        }
        session["tech_stack"]["database"] = db_map.get(answer.strip(), "postgresql-supabase")
        session["current_phase"] = "planning"

        # Generate summary
        ts = session["tech_stack"]
        summary = f"""
## Discovery Complete!

**Project Summary:**
- **Objective**: {session["objective"]}
- **Type**: {session["project_type"]}
- **Scale**: {session["scale"]}
- **Tech Stack**:
  - Frontend: {ts.get("frontend", "N/A")}
  - Backend: {ts.get("backend", "N/A")}
  - Database: {ts.get("database", "N/A")}

---

## Moving to Planning Phase

I will now generate:
1. **CLAUDE.md** - Global rules for your project
2. **PRD** - Product Requirements Document

{"**Mode: Supervised** - I'll show you the generated content for approval." if session["mode"] == "supervised" else "**Mode: Autonomous** - Generating now..."}

Reply with "continue" to proceed.
"""
        return summary

    return "Discovery complete. Reply with 'continue' to proceed to Planning."


async def _handle_planning(session_id: str, answer: str) -> str:
    """Handle Planning phase - generate CLAUDE.md and PRD."""
    session = sessions[session_id]

    if answer.lower().strip() != "continue":
        return "Reply with 'continue' to proceed with Planning phase."

    # Generate CLAUDE.md based on tech stack
    ts = session["tech_stack"]
    claude_md = f"""# {session["objective"]}

## Core Principles

- **TYPE_SAFETY**: All functions must have type hints
- **VERBOSE_NAMING**: Use descriptive names (get_user_by_email, not get_user)
- **AI_FRIENDLY_LOGGING**: JSON structured logs with fix_suggestion field
- **KISS**: Keep solutions simple, avoid over-engineering
- **YAGNI**: Don't build features until needed

## Tech Stack

- **Frontend**: {ts.get("frontend", "N/A")}
- **Backend**: {ts.get("backend", "N/A")}
- **Database**: {ts.get("database", "N/A")}
- **Package Manager**: uv (Python) / pnpm (Node)
- **Testing**: pytest / vitest

## Architecture

- **Pattern**: Vertical Slice Architecture
- **API Style**: REST with OpenAPI documentation
- **Auth**: JWT with refresh tokens
- **Multi-tenancy**: Row-Level Security (if applicable)

## Code Style

- Use snake_case for Python, camelCase for TypeScript
- Maximum line length: 100 characters
- Docstrings required for public functions
- Type hints required for all function parameters and returns

## Testing

- Unit tests mirror source structure
- Integration tests in tests/integration/
- Minimum 80% coverage for core features
- Use pytest markers: @pytest.mark.unit, @pytest.mark.integration

## Common Patterns

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

    session["claude_md"] = claude_md

    # Generate basic PRD
    prd = f"""# Product Requirements Document

## Executive Summary

**Product**: {session["objective"]}
**Type**: {session["project_type"]}
**Target Scale**: {session["scale"]}

## Mission

Build a {session["project_type"]} application that {session["objective"]}.

## MVP Scope

### Core Features (P0)
1. User authentication (signup, login, password reset)
2. Core functionality based on objective
3. Basic admin dashboard

### Nice-to-Have (P1)
1. Email notifications
2. User preferences
3. Analytics dashboard

## Success Criteria

- [ ] Users can complete core workflow end-to-end
- [ ] System handles expected load for {session["scale"]} phase
- [ ] All critical paths have test coverage
- [ ] Deployment pipeline working

## Tech Stack

{json.dumps(ts, indent=2)}
"""

    session["prd"] = prd
    session["current_phase"] = "roadmap"

    return f"""
## Planning Phase Complete!

### Generated CLAUDE.md

```markdown
{claude_md}
```

---

### Generated PRD (Summary)

```markdown
{prd}
```

---

## Next: Roadmap Phase

I'll break this down into implementable features.

Reply with "continue" to proceed to Roadmap, or provide feedback to adjust.
"""


async def _handle_roadmap(session_id: str, answer: str) -> str:
    """Handle Roadmap phase - break down into features."""
    session = sessions[session_id]

    # Generate feature breakdown
    session["features"] = [
        {"name": "Project Setup", "status": "pending", "plan": "Initialize project with tech stack, create folder structure, configure tooling"},
        {"name": "Authentication", "status": "pending", "plan": "Implement user signup, login, logout, password reset with JWT"},
        {"name": "Core Data Models", "status": "pending", "plan": "Define database schema, create ORM models, implement CRUD operations"},
        {"name": "API Endpoints", "status": "pending", "plan": "Create REST endpoints for core functionality"},
        {"name": "Frontend Setup", "status": "pending", "plan": "Initialize frontend, configure routing, create layout components"},
    ]

    session["current_phase"] = "implementation"

    features_list = "\n".join([
        f"{i+1}. **{f['name']}** - {f['plan']}"
        for i, f in enumerate(session["features"])
    ])

    return f"""
## Roadmap Phase Complete!

### Feature Breakdown

{features_list}

---

## Ready for Implementation

I'll implement these features one by one using the PIV Loop:
- **P**lan: Create detailed implementation plan
- **I**mplement: Write the code
- **V**alidate: Run tests and linting

Reply with "start" to begin implementing Feature 1: Project Setup.
"""


async def _handle_implementation(session_id: str, answer: str) -> str:
    """Handle Implementation phase - execute PIV Loop."""
    session = sessions[session_id]
    current_idx = session["current_feature"]

    if current_idx >= len(session["features"]):
        return """
## All Features Implemented!

Your project is ready. Next steps:
1. Review the generated code
2. Run the test suite
3. Deploy to your target environment

Use `playbook_get_status` to see a summary.
"""

    feature = session["features"][current_idx]
    feature["status"] = "in_progress"

    return f"""
## Implementing Feature {current_idx + 1}: {feature["name"]}

### Plan
{feature["plan"]}

### PIV Loop Status
- [x] Plan created
- [ ] Implementation in progress
- [ ] Validation pending

---

*This is where the agent would use Claude Code to create files.*
*For now, this is a placeholder showing the workflow.*

Reply with "next" to proceed to the next feature, or "done" when finished.
"""


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

    session = sessions[session_id]

    return f"""
## Continuing Session: {session_id}

**Objective**: {session["objective"]}
**Current Phase**: {session["current_phase"]}
**Mode**: {session["mode"]}

**Progress**:
- Project Type: {session["project_type"] or "Not set"}
- Scale: {session["scale"] or "Not set"}
- Tech Stack: {json.dumps(session.get("tech_stack", {}), indent=2) if session.get("tech_stack") else "Not set"}
- Features: {len(session.get("features", []))} defined
- Current Feature: {session["current_feature"] + 1 if session.get("features") else "N/A"}

Reply with "continue" to proceed with the current phase.
"""


@mcp.tool(name="playbook_search")
async def search_playbook(query: str, max_results: int = 5) -> str:
    """
    Search the AI Project Playbook for relevant guides.

    Args:
        query: What you're looking for (e.g., "deployment", "testing", "auth")
        max_results: Maximum number of results (default 5)

    Returns:
        Matching sections from the playbook
    """
    results = search_playbook_files(query, max_results)

    if not results:
        return f"No results found for '{query}'. Try a different search term."

    output = f"## Search Results for '{query}'\n\n"
    for i, result in enumerate(results, 1):
        output += f"### {i}. {result['file']}\n"
        output += f"```\n{result['snippet']}...\n```\n\n"

    return output


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

    session = sessions[session_id]

    # Count feature progress
    total = len(session.get("features", []))
    completed = sum(1 for f in session.get("features", []) if f.get("status") == "completed")
    in_progress = sum(1 for f in session.get("features", []) if f.get("status") == "in_progress")

    status = f"""
## Project Status: {session_id}

### Overview
- **Objective**: {session["objective"]}
- **Type**: {session["project_type"] or "Not determined"}
- **Scale**: {session["scale"] or "Not determined"}
- **Mode**: {session["mode"]}

### Phase Progress
- **Current Phase**: {session["current_phase"]}
- **Features**: {completed}/{total} completed ({in_progress} in progress)

### Tech Stack
{json.dumps(session.get("tech_stack", {}), indent=2) if session.get("tech_stack") else "Not yet determined"}

### Generated Artifacts
- CLAUDE.md: {"Generated" if session.get("claude_md") else "Pending"}
- PRD: {"Generated" if session.get("prd") else "Pending"}
- Files Created: {len(session.get("files_created", []))}
"""

    if session.get("features"):
        status += "\n### Features\n"
        for i, f in enumerate(session["features"], 1):
            icon = {"pending": "⬜", "in_progress": "🔄", "completed": "✅"}.get(f["status"], "⬜")
            status += f"{icon} {i}. {f['name']}\n"

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
    for sid, session in sessions.items():
        output += f"- **{sid}**: {session['objective']} ({session['current_phase']})\n"

    return output


def main():
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
