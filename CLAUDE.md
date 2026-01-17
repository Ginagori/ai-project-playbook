# AI Project Playbook - Development Guidelines

## Project Overview

This is an **MCP Server** that exposes an AI PM Agent for Claude Code. The agent guides users from idea to deployment using the PIV Loop methodology.

**Repository:** `C:\Users\natal\Proyectos\ai-project-playbook\`
**Team:** Nivanta AI
**Status:** Production (27 MCP tools)

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Language** | Python 3.12 |
| **MCP Framework** | FastMCP |
| **Orchestration** | LangGraph (state machine) |
| **Models** | Pydantic v2 |
| **Database** | Supabase (PostgreSQL + pgvector) |
| **Package Manager** | uv |

---

## Architecture

```
ai-project-playbook/
├── agent/                    # Core agent logic
│   ├── models/               # Pydantic models (project.py)
│   ├── orchestrator.py       # LangGraph state machine
│   ├── tools/                # Agent tools (playbook_rag, file_operations)
│   ├── factory/              # Multi-agent patterns (6 patterns)
│   ├── specialized/          # Specialized agents (researcher, coder, etc.)
│   ├── meta_learning/        # Pattern capture & recommendations
│   └── supabase_client.py    # Database operations
├── mcp_server/
│   └── playbook_mcp.py       # MCP Server (27 tools)
├── playbook/                 # Methodology content (63 markdown files)
├── supabase/
│   ├── schema.sql            # Database schema
│   └── migrations/           # SQL migrations
├── docs/
│   └── ONBOARDING.md         # Team setup guide
└── scripts/
    └── index_playbook.py     # RAG indexer
```

---

## Code Style

### Naming Conventions

```python
# Functions: snake_case, verb prefix
async def start_project(objective: str) -> str:
async def get_project_status(session_id: str) -> dict:

# Classes: PascalCase
class OrchestratorState:
class SupabaseClient:

# Constants: SCREAMING_SNAKE_CASE
SUPABASE_ENABLED = True
PLAYBOOK_DIR = Path(__file__).parent
```

### Type Hints

Always use type hints for function signatures:

```python
async def link_repo(self, session_id: str, repo_url: str) -> bool:
    """Link a GitHub repository URL to a project."""
    ...
```

### Async/Await

All database operations and MCP tools are async:

```python
@mcp.tool(name="playbook_start_project")
async def start_project(objective: str, mode: str = "supervised") -> str:
    ...
```

### Error Handling

Use try/except with informative messages:

```python
try:
    result = self.client.table("projects").upsert(data).execute()
    return bool(result.data)
except Exception as e:
    print(f"Error saving to Supabase: {e}")
    return False
```

---

## MCP Tools Structure

Each MCP tool follows this pattern:

```python
@mcp.tool(name="playbook_tool_name")
async def tool_name(required_param: str, optional_param: str = "") -> str:
    """
    Brief description of what the tool does.

    Args:
        required_param: Description of the parameter
        optional_param: Description with default behavior

    Returns:
        Markdown-formatted string for Claude Code display
    """
    # 1. Validate inputs
    if not SUPABASE_ENABLED:
        return "## Error\n\nSupabase not configured."

    # 2. Execute logic
    result = await some_operation()

    # 3. Return formatted markdown
    return f"""## Success

**Result**: {result}
"""
```

---

## Testing

### Running Tests

```bash
# From project root
cd ai-project-playbook
.venv/Scripts/python.exe -c "
import asyncio
async def test():
    from mcp_server.playbook_mcp import start_project
    result = await start_project('Test project', 'supervised')
    print(result[:500])
asyncio.run(test())
"
```

### Test Patterns

- Test each MCP tool independently
- Verify Supabase operations with HTTP status codes
- Check that markdown output is well-formatted

---

## Supabase Operations

### Schema

Main tables:
- `teams` - Team information
- `team_members` - User-team associations
- `projects` - Project state and artifacts
- `lessons_learned` - Shared knowledge base
- `project_outcomes` - Completed project data

### Row Level Security

All tables have RLS enabled. Data is isolated by `team_id`.

### Adding New Columns

1. Create migration in `supabase/migrations/`
2. Run SQL in Supabase Dashboard
3. Update `supabase_client.py` with new methods
4. Add MCP tool in `playbook_mcp.py`

---

## Lessons Learned System

**IMPORTANT**: Always use `playbook_share_lesson` (NOT `playbook_add_lesson`) to save lessons.

- `playbook_add_lesson` → saves locally only (session-scoped, NOT persistent)
- `playbook_share_lesson` → saves to Supabase (shared with team, persistent)

When capturing learnings from development sessions, ALWAYS use `playbook_share_lesson` so they are stored in Supabase and available to the entire team.

---

## Common Patterns

### Adding a New MCP Tool

1. Add function to `mcp_server/playbook_mcp.py`:
```python
@mcp.tool(name="playbook_new_tool")
async def new_tool(param: str) -> str:
    """Tool description."""
    # Implementation
    return "## Result\n\n..."
```

2. Update documentation:
   - `README.md` - Add to tools table
   - `docs/ONBOARDING.md` - Add to commands list

3. Test the tool manually

### Adding Supabase Operations

1. Add method to `agent/supabase_client.py`:
```python
async def new_operation(self, param: str) -> bool:
    """Description."""
    if not self.client:
        return False
    result = self.client.table("table").select("*").execute()
    return bool(result.data)
```

2. Create MCP tool that uses it

---

## Environment Variables

Required for full functionality:

```env
# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
PLAYBOOK_TEAM_ID=uuid-here

# User identification
PLAYBOOK_USER=your_name
```

---

## Git Workflow

### Commit Messages

Use conventional commits:
```
feat: Add new feature
fix: Fix bug
docs: Update documentation
refactor: Restructure code
```

### Before Committing

1. Test imports: `.venv/Scripts/python.exe -c "from mcp_server.playbook_mcp import mcp"`
2. Verify MCP tools work
3. Update documentation if adding features

---

## Current State (Session 10)

- **27 MCP Tools** functional
- **Supabase** integration complete
- **Project sync** between team members
- **Repository linking** for projects
- **Meta-learning** from completed projects

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `uv pip install -r requirements.txt` | Install dependencies |
| `.venv/Scripts/python.exe -m mcp_server.playbook_mcp` | Run MCP server |
| `git status && git diff` | Check changes |

---

## UI Agent Integration

The Playbook Agent integrates with **UI Agent** for frontend component generation.

### How It Works

When you create a project with Playbook Agent, it generates:
- `CLAUDE.md` - Project rules and conventions
- `docs/PRD.md` - Product requirements document
- `.playbook/session.json` - Session state

When you run `ui-agent chat` in that project, UI Agent **automatically detects** these files and:
1. Reads the tech stack from CLAUDE.md
2. Uses project rules for component generation
3. Follows the PRD requirements
4. Generates components that match the established architecture

### Workflow

```
1. Start project with Playbook:
   playbook_start_project "Build a veterinary clinic SaaS"

2. Complete Discovery & Planning phases:
   → Generates CLAUDE.md with tech stack
   → Generates PRD.md with requirements

3. When ready for frontend:
   cd your-project
   ui-agent chat
   → UI Agent reads Playbook context automatically
   → "ℹ Playbook context detected - using project rules"

4. Generate components:
   "Create a login form with email and social login"
   → Component follows project's tech stack
   → Uses established styling (Tailwind, etc.)
```

### UI Agent Repository

**GitHub:** https://github.com/Ginagori/ui-agent

Install globally:
```bash
git clone https://github.com/Ginagori/ui-agent.git
cd ui-agent
./scripts/install-global.sh  # or .ps1 for Windows
```

### Design Inspiration MCP

UI Agent includes a **design-mcp** for searching design inspiration before generating components.

**Available tools:**
- `search_dribbble` - Search Dribbble for design shots
- `search_behance` - Search Behance for projects
- `search_awwwards` - Search award-winning websites
- `get_ui_pattern` - Best practices for UI patterns (dashboard, login, pricing, form, table, modal, sidebar, card, notification, settings)
- `get_design_recommendations` - Tailored suggestions for a use case

**Recommended workflow:**
1. Use `get_design_recommendations` with the project use case
2. Search Dribbble/Behance for visual inspiration
3. Get UI pattern best practices
4. Generate components with UI Agent following the inspiration

---

*Built by Nivanta AI Team*
