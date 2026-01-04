# Agent Capabilities

Complete list of what the AI Project Playbook Agent can do.

## Core Capabilities

### Project Management

| Capability | Description |
|------------|-------------|
| **Start Project** | Initialize a new project from an objective |
| **Discovery Phase** | Ask targeted questions to understand requirements |
| **Generate CLAUDE.md** | Create global rules for the project |
| **Generate PRD** | Create Product Requirements Document |
| **Feature Breakdown** | Decompose PRD into implementable features |
| **Create Plans** | Generate detailed implementation plans |
| **Execute PIV Loop** | Implement features with validation |
| **Track Progress** | Maintain state across sessions |

### Code Generation

| Capability | Description |
|------------|-------------|
| **Architecture Selection** | Choose appropriate patterns (VSA, MVC, etc.) |
| **Tech Stack Selection** | Recommend stack based on requirements |
| **Boilerplate Generation** | Create project structure and configs |
| **Feature Implementation** | Write code following plans |
| **Test Generation** | Create tests alongside code |
| **Validation Execution** | Run linting, type checking, tests |

### Deployment

| Capability | Description |
|------------|-------------|
| **Phase Assessment** | Determine current scale phase |
| **Config Generation** | Create deployment configs (Docker, K8s, etc.) |
| **CI/CD Setup** | Generate GitHub Actions workflows |
| **Migration Planning** | Plan phase transitions (MVP → Growth → Scale) |

### Multi-Agent

| Capability | Description |
|------------|-------------|
| **Agent Creation** | Create specialized agents |
| **Agent Registry** | Maintain list of available agents |
| **Workflow Building** | Create multi-agent workflows |
| **Pattern Selection** | Choose appropriate orchestration pattern |
| **Agent Communication** | Manage inter-agent messaging |

## Autonomy Modes

### Supervised Mode (Default)
- Proposes actions before executing
- Asks for confirmation on file changes
- Requests approval for commits
- Shows plan before implementation

### Autonomous Mode
- Executes without confirmation
- Only reports progress and results
- Ideal for repetitive tasks
- Activate with: "modo autónomo" or --autonomous

### Plan-Only Mode
- Generates plans without executing
- No file changes or commits
- Ideal for review and learning
- Activate with: "solo planea" or --plan-only

## Knowledge Base

The agent has access to the complete AI Project Playbook:

### Methodology
- PIV Loop (Plan → Implement → Validate)
- Global Rules system
- Slash Commands patterns
- Validation Pyramid

### Templates
- CLAUDE.md template
- PRD template
- Plan template
- Docker/K8s configs

### Examples
- Veterinaria SaaS
- Agencia Empleados
- Capacitaciones Platform

### Deployment Guides
- MVP (Netlify + Railway)
- Growth (Cloud Run)
- Scale (Kubernetes)
- Enterprise (Multi-cloud)

## Limitations

- Cannot access external APIs without MCP tools
- Cannot execute code outside the project directory
- Cannot make changes without Claude Code context
- Memory limited to session (uses Supabase for persistence)

## Integration Points

### MCP Tools
- File operations (create, edit, delete)
- Git operations (commit, push, branch)
- Playbook RAG search
- Project state management

### External Services (via Supabase)
- PostgreSQL for project state
- pgvector for RAG embeddings
- Auth for multi-user support
- RLS for data isolation
