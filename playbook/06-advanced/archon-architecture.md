# Archon Architecture - MCP Knowledge Management

**Persistent memory y task management con Archon MCP**

---

## 🎯 Qué es Archon

**Archon = Command Center MCP** (Model Context Protocol)

**Componentes:**
- Knowledge Management (persistent memory)
- Task Management (todos, subtasks)
- Project Context (cross-session state)
- Event System (hooks, triggers)

**NO es:** Framework de AI agents (eso es LangGraph, Pydantic AI)
**SÍ es:** Infraestructura para memoria persistente entre sesiones

---

## 📋 Cuándo Usar Archon

**Usa Archon si:**
- [ ] Proyecto complejo (>10K líneas código)
- [ ] Team de 3+ developers usando AI
- [ ] Múltiples agents que necesitan compartir context
- [ ] Sesiones de AI coding que duran semanas
- [ ] Necesitas "memory" entre conversaciones

**NO uses Archon si:**
- ❌ Proyecto simple (<5K líneas)
- ❌ Solo tú usando Claude Code
- ❌ CLAUDE.md + slash commands es suficiente
- ❌ No quieres mantener infraestructura extra

---

## 🚀 Setup Archon (1-2 días)

### Paso 1: Install Archon Server

```bash
# Archon requires Docker
git clone https://github.com/coleam00/archon-mcp
cd archon-mcp

# Start services (Postgres, Redis, API)
docker-compose up -d

# Verify
curl http://localhost:8080/health
# {"status": "healthy"}
```

### Paso 2: Configure MCP

```json
// claude_desktop_config.json
{
  "mcpServers": {
    "archon": {
      "command": "node",
      "args": ["/path/to/archon-mcp/dist/index.js"],
      "env": {
        "ARCHON_API_URL": "http://localhost:8080",
        "ARCHON_API_KEY": "your-key-here"
      }
    }
  }
}
```

### Paso 3: Initialize Project

```bash
# Create project in Archon
curl -X POST http://localhost:8080/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "myapp",
    "description": "SaaS app for X",
    "tech_stack": ["React", "FastAPI", "Supabase"]
  }'
```

---

## 💾 Knowledge Management

**Problema:** Claude olvida todo entre sesiones

**Solución:** Archon persiste knowledge

```python
# Add knowledge to Archon
@app.post("/archon/knowledge")
async def add_knowledge(item: dict):
    archon.knowledge.add({
        "type": "architecture_decision",
        "title": "Why we use Supabase RLS",
        "content": "Multi-tenancy from day 1, RLS policies...",
        "tags": ["database", "multi-tenancy"],
        "project_id": "myapp"
    })

# Query knowledge
knowledge = archon.knowledge.search(
    query="multi-tenancy",
    project_id="myapp",
    limit=5
)
```

**Uso en prompt:**
```
Claude, before implementing multi-tenancy:
1. Query Archon for "multi-tenancy" decisions
2. Follow existing patterns
3. Update Archon with new learnings
```

---

## ✅ Task Management

```python
# Create task
task = archon.tasks.create({
    "title": "Implement user authentication",
    "description": "JWT-based auth with refresh tokens",
    "status": "todo",
    "project_id": "myapp",
    "tags": ["backend", "auth"]
})

# Add subtasks
archon.tasks.create_subtask(task.id, {
    "title": "Create /auth/login endpoint",
    "status": "in_progress"
})

archon.tasks.create_subtask(task.id, {
    "title": "Implement JWT generation",
    "status": "todo"
})

# Query tasks
pending_tasks = archon.tasks.list(
    project_id="myapp",
    status="todo",
    tags=["backend"]
)
```

---

## 🔗 Integration con CLAUDE.md

**CLAUDE.md (global rules) + Archon (project memory) = Powerful combo**

```markdown
# CLAUDE.md

## Core Principles
(Static rules que nunca cambian)

## Architecture
(High-level architecture)

## Archon Integration
Before implementing ANY feature:
1. Query Archon for related decisions: `archon.knowledge.search(feature_name)`
2. Check existing tasks: `archon.tasks.related(feature_name)`
3. Follow discovered patterns
4. After implementation, update Archon with learnings

## Example Workflow
\`\`\`bash
# User: "Add email notifications"

# Claude internally:
1. Query Archon: "email notifications" → Find decision "Use SendGrid"
2. Query tasks: Find task "Email system setup" → already completed
3. Implement using SendGrid (from Archon decision)
4. Update Archon: Add "Email notification patterns" knowledge
\`\`\`
```

---

## 📊 Archon vs Simple CLAUDE.md

| Feature | CLAUDE.md Only | CLAUDE.md + Archon |
|---------|----------------|---------------------|
| **Global Rules** | ✅ Excellent | ✅ Excellent |
| **Cross-session memory** | ❌ No | ✅ Yes |
| **Task tracking** | Manual (markdown) | ✅ Automated (database) |
| **Team collaboration** | ⚠️ Git conflicts | ✅ Shared database |
| **Search knowledge** | ⚠️ Grep files | ✅ Semantic search |
| **Setup complexity** | ✅ Simple (1 file) | ❌ Complex (Docker, DB) |
| **Maintenance** | ✅ None | ❌ Server upkeep |

---

## 🎓 Decision Tree

```
¿Necesitas Archon?

├─ Proyecto simple (<5K líneas)? → NO, usa solo CLAUDE.md
├─ Solo developer? → NO, usa solo CLAUDE.md
├─ Sesiones cortas (<1 hora)? → NO, usa solo CLAUDE.md
└─ Proyecto complejo + Team + Long sessions?
   └─ SÍ, usa CLAUDE.md + Archon
```

---

## 🎓 Key Takeaways

1. **Archon ≠ Necesario** - Mayoría de proyectos NO lo necesitan
2. **CLAUDE.md first** - Empieza simple, agrega Archon si crece
3. **Persistent memory** - Valor real de Archon es cross-session knowledge
4. **Team collaboration** - Archon brilla en equipos de 3+ developers
5. **Infrastructure cost** - Requiere Docker + Postgres + mantenimiento

**Recomendación:** Empieza con CLAUDE.md solo. Agrega Archon solo si hit limits claros.
