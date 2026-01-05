# AI Project Playbook Agent

An autonomous AI PM Agent that guides you from idea to deployment using the PIV Loop methodology.

## What Is This?

The AI Project Playbook Agent is a **Project Manager AI** that can:

1. **Discovery**: Ask questions to understand your project requirements
2. **Planning**: Generate CLAUDE.md (global rules) and PRD automatically
3. **Roadmap**: Break down the project into implementable features
4. **Implementation**: Execute PIV Loop (Plan → Implement → Validate) for each feature
5. **Deployment**: Generate deployment configs for MVP → Growth → Scale → Enterprise

## Quick Start

### 1. Install Dependencies

```bash
cd ai-project-playbook
uv venv
uv pip install -r requirements.txt
```

### 2. Index the Playbook

```bash
uv run python scripts/index_playbook.py
```

### 3. Configure Claude Code (Global)

Add this to your **global** Claude Code config at `~/.claude.json` (Linux/Mac) or `C:\Users\<USER>\.claude.json` (Windows):

> **Important:** The file is `.claude.json` in your home directory, NOT `.claude/settings.json`

```json
{
  "mcpServers": {
    "playbook": {
      "command": "C:\\path\\to\\ai-project-playbook\\.venv\\Scripts\\python.exe",
      "args": ["-m", "mcp_server.playbook_mcp"],
      "cwd": "C:\\path\\to\\ai-project-playbook"
    }
  }
}
```

For Linux/Mac:
```json
{
  "mcpServers": {
    "playbook": {
      "command": "/path/to/ai-project-playbook/.venv/bin/python",
      "args": ["-m", "mcp_server.playbook_mcp"],
      "cwd": "/path/to/ai-project-playbook"
    }
  }
}
```

> **Note:** Replace the paths with the actual path where you cloned this repo.
>
> After saving, **restart Claude Code** for the changes to take effect.

Optionally, add permissions in `~/.claude/settings.json`:
```json
{
  "permissions": {
    "allow": ["mcp__playbook__*"]
  }
}
```

### 4. Use the Agent

In Claude Code, you can now use these tools:

- `playbook_start_project "Build a SaaS for X"` - Start a new project
- `playbook_continue session_id` - Continue where you left off
- `playbook_search "deployment"` - Search the playbook
- `playbook_get_status session_id` - Check project status

## Autonomy Modes

| Mode | Behavior |
|------|----------|
| **Supervised** (default) | Asks for confirmation before each action |
| **Autonomous** | Executes without asking (say "modo autónomo") |
| **Plan-only** | Only generates plans, no execution (say "solo planea") |

## Project Structure

```
ai-project-playbook/
├── SKILL.md                # Anthropic Skill definition
├── playbook/               # Complete methodology (63 files)
│   ├── 00-overview/
│   ├── 01-discovery/
│   ├── 02-planning/
│   ├── 03-roadmap/
│   ├── 04-implementation/
│   ├── 05-deployment/
│   ├── 06-advanced/
│   ├── templates/
│   └── examples/
├── agent/                  # Agent implementation
│   ├── models/             # Pydantic models
│   ├── phases/             # Phase implementations
│   ├── tools/              # Agent tools
│   └── factory/            # Multi-agent patterns
├── mcp_server/             # MCP Server
│   └── playbook_mcp.py     # Main server
├── scripts/                # Utilities
│   └── index_playbook.py   # RAG indexer
└── references/             # Quick navigation guides
```

## MCP Tools

### Project Management Tools

| Tool | Description |
|------|-------------|
| `playbook_start_project` | Start a new project with an objective |
| `playbook_continue` | Continue from where you left off |
| `playbook_answer` | Answer agent's question |
| `playbook_search` | Search the playbook |
| `playbook_get_status` | Get project status |
| `playbook_list_sessions` | List all active sessions |
| `playbook_get_claude_md` | Get generated CLAUDE.md |
| `playbook_get_prd` | Get generated PRD |

### Agent Factory Tools

| Tool | Description |
|------|-------------|
| `playbook_run_task` | Route task to best agent automatically |
| `playbook_run_pipeline` | Run full pipeline: Research→Plan→Code→Review→Test |
| `playbook_code_review` | Run parallel code reviews (quality + security) |
| `playbook_supervised_task` | Run with supervisor orchestrating multiple agents |
| `playbook_research` | Research a topic using the playbook |
| `playbook_plan_feature` | Create implementation plan for a feature |
| `playbook_generate_code` | Generate code (API, service, component, etc.) |
| `playbook_generate_tests` | Generate tests for code |

## Supported Project Types

- **SaaS Applications**: Multi-tenant web apps
- **API Backends**: REST/GraphQL APIs
- **Agent Systems**: Single AI agents
- **Multi-Agent Systems**: Orchestrated agent workflows

## Scale Phases

| Phase | Users | Cost/Month | Stack |
|-------|-------|------------|-------|
| MVP | <100 | $300-500 | Netlify + Railway |
| Growth | 100-10K | $1,500-3K | Netlify + Cloud Run |
| Scale | 10K-100K | $8K-15K | Netlify + GKE |
| Enterprise | 100K+ | $50K+ | Multi-cloud |

## Agent Factory

The Agent Factory provides 6 multi-agent patterns:

| Pattern | Use Case |
|---------|----------|
| **Sequential** | Pipeline workflows (Research→Plan→Code→Review→Test) |
| **Parallel** | Fan-out/fan-in (multiple reviewers in parallel) |
| **Supervisor** | Dynamic orchestration based on task state |
| **Router** | Cost-optimized routing to specialized agents |
| **Handoff** | Complete delegation to another agent |
| **Agent-as-Tool** | Wrap agent as callable tool |

### Specialized Agents

- **Researcher**: Searches playbook for relevant information
- **Planner**: Creates detailed implementation plans
- **Coder**: Generates code (API, service, component, tests)
- **Reviewer**: Reviews code for quality, security, patterns
- **Tester**: Generates tests and validation commands

## Future Plans

- [ ] Supabase integration for persistent state
- [ ] RAG with pgvector for semantic search
- [ ] Multi-user support with RLS
- [x] Agent Factory for creating specialized agents ✓
- [ ] Meta-Learning from completed projects

## License

MIT - Built by Nivanta AI
