# AI Project Playbook Agent

An autonomous AI PM Agent that guides you from idea to deployment using the PIV Loop methodology.

## What Is This?

The AI Project Playbook Agent is a **Project Manager AI** that can:

1. **Discovery**: Ask questions to understand your project requirements
2. **Planning**: Generate CLAUDE.md (global rules) and PRD automatically
3. **Roadmap**: Break down the project into implementable features
4. **Implementation**: Execute PIV Loop (Plan → Implement → Validate) for each feature
5. **Deployment**: Generate deployment configs for MVP → Growth → Scale → Enterprise

### What's New (v2)

- **Artifact Evaluation**: Automatic quality checks on CLAUDE.md, PRD, and feature plans (0.0-1.0 scoring)
- **System Review**: Meta-analysis of plan vs execution with confidence scoring (1-10)
- **PRP Format**: Project Requirements Plan — enhanced planning for agent-to-agent communication
- **Hybrid Search**: Category-based relevance (70%) + keyword matching (30%) for smarter playbook search
- **Auto-Capture**: Automatically captures lessons at each phase transition
- **Platform Project Type**: Support for complex multi-component systems (marketplaces, agent platforms)
- **6 New Playbook Guides**: Agent Evals, Observability, Security, SaaS Monetization, Memory Architecture, Marketplace Development

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
├── playbook/               # Complete methodology (~71 files, ~39K lines)
│   ├── 00-overview/        # Philosophy, quick start
│   ├── 01-discovery/       # Discovery questions, tech stack selector
│   ├── 02-planning/        # CLAUDE.md creation, PRD, security
│   ├── 03-roadmap/         # Slash commands, plan templates, feature breakdown
│   ├── 04-implementation/  # PIV Loop, validation pyramid, system review guide
│   ├── 05-deployment/      # MVP → Enterprise deployment configs
│   ├── 06-advanced/        # Agent evals, observability, security, memory, marketplace, monetization
│   ├── templates/          # CLAUDE.md template, PRD template, PRP template
│   └── examples/           # Real project examples
├── agent/                  # Agent implementation
│   ├── models/             # Pydantic models (ProjectState, ProjectType)
│   ├── evals/              # Artifact evaluation (rules, scoring)
│   ├── tools/              # Agent tools (RAG with hybrid search)
│   ├── factory/            # Multi-agent patterns (6 patterns)
│   ├── specialized/        # Specialized agents (Researcher, Coder, etc.)
│   ├── meta_learning/      # Pattern capture, recommendations, auto-capture
│   └── system_review.py    # Meta-analysis of plan vs execution
├── mcp_server/             # MCP Server
│   └── playbook_mcp.py     # Main server (30 tools)
├── .claude/commands/       # Slash commands
│   └── system-review.md    # /system-review command
├── scripts/                # Utilities
│   └── index_playbook.py   # RAG indexer
└── references/             # Quick navigation guides
```

## MCP Tools (30 total)

### Project Management Tools (10)

| Tool | Description |
|------|-------------|
| `playbook_start_project` | Start a new project with an objective |
| `playbook_continue` | Continue from where you left off |
| `playbook_answer` | Answer agent's question |
| `playbook_search` | Search the playbook (hybrid: 70% category + 30% keyword) |
| `playbook_get_status` | Get project status |
| `playbook_list_sessions` | List all active sessions (local + team) |
| `playbook_get_claude_md` | Get generated CLAUDE.md |
| `playbook_get_prd` | Get generated PRD |
| `playbook_link_repo` | Link a GitHub repository to a project |
| `playbook_get_repo` | Get the repository URL for a project |

### Agent Factory Tools (8)

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

### Meta-Learning Tools (6)

| Tool | Description |
|------|-------------|
| `playbook_complete_project` | Complete a project and capture lessons learned |
| `playbook_get_recommendations` | Get recommendations based on past projects |
| `playbook_find_similar` | Find similar past projects |
| `playbook_suggest_stack` | Get tech stack suggestions for project type |
| `playbook_learning_stats` | View meta-learning database statistics |
| `playbook_add_lesson` | Manually add a lesson learned |

### Team Tools (3)

| Tool | Description |
|------|-------------|
| `playbook_team_status` | Check Supabase connection and team info |
| `playbook_share_lesson` | Share a lesson with the team |
| `playbook_team_lessons` | View team's shared lessons |

### Quality & Review Tools (3) — NEW

| Tool | Description |
|------|-------------|
| `playbook_evaluate_artifact` | Run quality checks on CLAUDE.md, PRD, or feature plans |
| `playbook_system_review` | Meta-analysis of plan vs execution (confidence 1-10) |
| `playbook_get_prp` | Get feature plan in PRP format (agent-to-agent ready) |

## Supported Project Types

| Type | Description | Example |
|------|-------------|---------|
| **SaaS** | Multi-tenant web applications | Veterinary clinic management |
| **API** | REST/GraphQL API backends | Payment processing API |
| **Agent** | Single AI agent systems | Customer support chatbot |
| **Multi-Agent** | Orchestrated agent workflows | Research pipeline |
| **Platform** | Complex multi-component systems | AI Operations Center, Agent Marketplace |

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

## Quality & Evaluation System

### Artifact Evaluation

The agent automatically evaluates generated artifacts using rule-based checks:

- **CLAUDE.md**: Required sections, tech stack specifics, code examples, architecture pattern
- **PRD**: Success criteria, feature prioritization, no placeholders, integration points
- **Feature Plans**: File references, validation commands, integration points

Each check has a severity level (critical/warning/info) and produces a weighted score (0.0-1.0).

### System Review

Run `/system-review session_id` to get a meta-analysis of your project:

- **Plan Fidelity**: Did the implementation follow the plan?
- **Artifact Quality**: Are CLAUDE.md and PRD good enough?
- **Phase Progression**: Are you moving through phases correctly?
- **Confidence Score**: Weighted 1-10 score for project health

### PRP Format

Enhanced planning format for agent-to-agent communication:
- Zero ambiguity: every task has specific files and pseudocode
- Validation at every level: from syntax to integration
- Context-rich: references to existing code, patterns, gotchas

## Playbook Knowledge Base

The playbook contains ~71 files covering:

### Core Methodology
- PIV Loop (Plan → Implement → Validate)
- Discovery questions, tech stack selection
- CLAUDE.md creation, PRD generation
- Feature breakdown, plan templates
- Validation pyramid (5 levels)

### Deployment (18 files)
- MVP → Growth → Scale → Enterprise configurations
- Docker, Kubernetes, CI/CD templates
- Multi-tenancy design

### Advanced Guides (15 files)
- **Agent Testing & Evals**: Golden datasets, pydantic-evals, LLM Judge, production evals, user feedback
- **Agent Observability**: Langfuse setup, traces/spans/scores, cost tracking, dashboards
- **Agent Security**: Fail-closed model, sandbox execution, approval workflows, environment blocking
- **SaaS Monetization**: Stripe integration, token billing, marketplace commission, pricing strategy
- **Agent Memory Architecture**: 4+1 file system, vector-first search, heartbeat/cron, context window guard
- **Marketplace Development**: Digital employees, plugin architecture, multi-channel delivery, quality gates
- **Context Engineering**: RAG optimization, prompt engineering
- **Subagents Framework**: Parallel execution with git worktrees
- **Meta-reasoning**: Scope creep detection, plan adjustment

## Meta-Learning

The agent learns from completed projects and uses that knowledge to improve recommendations:

- **Pattern Capture**: Automatically extracts successful patterns from completed projects
- **Auto-Capture**: Lessons captured at each phase transition (discovery, planning, roadmap, deployment)
- **Tech Stack Suggestions**: Recommends technologies based on past project success rates
- **Pitfall Detection**: Warns about common issues for specific project types
- **Similarity Matching**: Finds relevant lessons from similar past projects

### How It Works

1. When a project completes, call `playbook_complete_project` with a rating
2. The system extracts patterns: what worked, what didn't, tech choices, etc.
3. Future projects get personalized recommendations based on learned patterns
4. Categories tracked: tech_stack, architecture, workflow, tooling, testing, deployment, pitfall

## Team Collaboration (Supabase)

The agent supports team collaboration via Supabase:

- **Shared Projects**: Projects sync automatically to the cloud
- **Shared Lessons**: Lessons learned are shared across all team members
- **Repository Links**: Link GitHub repos so team knows where code lives
- **Row Level Security**: Each team's data is isolated

### Key Features

- **Continue any project**: Use `playbook_continue` to pick up where a teammate left off
- **See team projects**: `playbook_list_sessions` shows both local and team sessions
- **Track repositories**: `playbook_link_repo` associates GitHub URLs with projects

### Setup for Team Members

1. Get the Supabase credentials from your team lead
2. Configure environment variables:
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your-anon-key
   PLAYBOOK_TEAM_ID=your-team-uuid
   PLAYBOOK_USER=your_name
   ```
3. See [docs/ONBOARDING.md](docs/ONBOARDING.md) for full setup instructions

## UI Agent Integration

The Playbook Agent integrates with **UI Agent** for professional frontend component generation.

### How It Works

1. **Playbook creates project context**: When you run through Discovery and Planning phases, Playbook generates `CLAUDE.md` and `docs/PRD.md` with your project's tech stack, architecture, and requirements.

2. **UI Agent reads context automatically**: When you run `ui-agent chat` in your project folder, it detects the Playbook files and uses them to generate components that match your project.

3. **Coordinated development**: Components generated by UI Agent follow the rules and patterns established in your CLAUDE.md.

### Workflow Example

```bash
# 1. Start a project with Playbook
playbook_start_project "Build a SaaS for veterinary clinics"

# 2. Complete Discovery & Planning phases...
# Playbook generates CLAUDE.md and PRD.md

# 3. When ready for frontend work:
cd your-project
ui-agent chat

# UI Agent detects Playbook context:
# "ℹ Playbook context detected - using project rules"

# 4. Generate components following project rules:
# "Create a patient registration form"
# → Uses tech stack from CLAUDE.md
# → Follows architecture from PRD
```

### Install UI Agent

```bash
git clone https://github.com/Ginagori/ui-agent.git
cd ui-agent
./scripts/install-global.sh  # macOS/Linux
# or
.\scripts\install-global.ps1  # Windows
```

**Repository:** https://github.com/Ginagori/ui-agent

---

## Future Plans

- [x] Supabase integration for persistent state
- [x] Project sync across team members
- [x] Repository linking for projects
- [x] Multi-user support with RLS
- [x] Agent Factory for creating specialized agents
- [x] Meta-Learning from completed projects
- [x] UI Agent integration for frontend generation
- [x] Artifact evaluation with quality scoring
- [x] System review (meta-analysis)
- [x] PRP format for agent-to-agent communication
- [x] Hybrid search for playbook
- [x] Auto-capture of lessons per phase
- [x] Platform project type
- [x] Advanced guides: evals, observability, security, monetization, memory, marketplace
- [ ] RAG with pgvector for semantic search
- [ ] Langfuse integration for agent observability
- [ ] n8n workflow integration

## License

MIT - Built by Nivanta AI
