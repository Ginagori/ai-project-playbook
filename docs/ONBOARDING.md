# AI Project Playbook - Onboarding para Nivanta AI Team

## Requisitos Previos

- Docker Desktop instalado y corriendo
- Claude Code (CLI o VSCode Extension)

## Instalación Rápida (5 minutos)

### Paso 1: Descargar la imagen Docker

```bash
docker pull ghcr.io/ginagori/ai-project-playbook:latest
```

### Paso 2: Configurar Claude Code

#### Opción A: VSCode Extension

Edita el archivo `%APPDATA%\Code\User\mcp.json` (Windows) o `~/.config/Code/User/mcp.json` (Linux/Mac):

```json
{
  "servers": {
    "playbook": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "ghcr.io/ginagori/ai-project-playbook:latest"],
      "type": "stdio"
    }
  }
}
```

#### Opción B: Claude Code CLI (Global)

Edita `~/.claude.json` (en tu home directory):

```json
{
  "mcpServers": {
    "playbook": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "ghcr.io/ginagori/ai-project-playbook:latest"]
    }
  }
}
```

### Paso 3: Reiniciar Claude Code

Cierra y vuelve a abrir VSCode o la terminal de Claude Code.

### Paso 4: Verificar instalación

En Claude Code, escribe:

```
playbook_learning_stats
```

Deberías ver estadísticas del sistema de meta-learning.

---

## Uso Básico

### Iniciar un nuevo proyecto

```
Quiero crear una app de inventarios para una ferretería
```

El agente iniciará el flujo de Discovery con preguntas sobre:
- Tipo de proyecto (SaaS, API, Agent)
- Tech stack preferido
- Funcionalidades principales
- Escala esperada

### Comandos disponibles (22 tools)

#### Project Management
| Tool | Descripción |
|------|-------------|
| `playbook_start_project` | Iniciar proyecto nuevo |
| `playbook_answer` | Responder preguntas del agente |
| `playbook_continue` | Continuar sesión existente |
| `playbook_search` | Buscar en el playbook |
| `playbook_get_status` | Ver estado del proyecto |
| `playbook_list_sessions` | Listar sesiones activas |
| `playbook_get_claude_md` | Obtener CLAUDE.md generado |
| `playbook_get_prd` | Obtener PRD generado |

#### Agent Factory
| Tool | Descripción |
|------|-------------|
| `playbook_run_task` | Ejecutar tarea con el mejor agente |
| `playbook_run_pipeline` | Pipeline: Research→Plan→Code→Review→Test |
| `playbook_code_review` | Reviews paralelos de código |
| `playbook_supervised_task` | Tarea con supervisor |
| `playbook_research` | Investigar tema en el playbook |
| `playbook_plan_feature` | Planear implementación de feature |
| `playbook_generate_code` | Generar código |
| `playbook_generate_tests` | Generar tests |

#### Meta-Learning
| Tool | Descripción |
|------|-------------|
| `playbook_complete_project` | Completar proyecto y guardar lecciones |
| `playbook_get_recommendations` | Obtener recomendaciones |
| `playbook_find_similar` | Buscar proyectos similares |
| `playbook_suggest_stack` | Sugerencias de tech stack |
| `playbook_learning_stats` | Estadísticas de aprendizaje |
| `playbook_add_lesson` | Agregar lección manualmente |

---

## Flujo de Trabajo Típico

```
1. Usuario: "Quiero crear un sistema de gestión de citas para veterinarias"

2. Agente (Discovery):
   - ¿Qué tipo de proyecto es? (SaaS, API, Agent)
   - ¿Qué tech stack prefieres?
   - ¿Cuáles son las funcionalidades principales?
   - ¿Cuántos usuarios esperas?
   - ¿Tienes experiencia previa relevante?

3. Usuario responde las 5 preguntas

4. Agente (Planning):
   - Genera CLAUDE.md con global rules
   - Genera PRD con features priorizados

5. Agente (Roadmap):
   - Descompone en features implementables
   - Crea plan por cada feature

6. Agente (Implementation):
   - Ejecuta PIV Loop por feature
   - Plan → Implement → Validate

7. Agente (Deployment):
   - Genera configs según escala (MVP/Growth/Scale/Enterprise)
```

---

## Troubleshooting

### "playbook tools not found"

1. Verifica que Docker está corriendo
2. Verifica que la imagen existe: `docker images | grep playbook`
3. Reinicia Claude Code

### "connection refused"

1. Prueba manualmente: `docker run --rm -i ghcr.io/ginagori/ai-project-playbook:latest`
2. Si falla, actualiza: `docker pull ghcr.io/ginagori/ai-project-playbook:latest`

### Los datos no persisten entre sesiones

La imagen Docker no persiste datos por defecto. Para persistir lecciones aprendidas:

```json
{
  "playbook": {
    "command": "docker",
    "args": [
      "run", "--rm", "-i",
      "-v", "playbook-data:/app/data",
      "ghcr.io/ginagori/ai-project-playbook:latest"
    ],
    "type": "stdio"
  }
}
```

---

## Soporte

- GitHub: https://github.com/Ginagori/ai-project-playbook
- Issues: https://github.com/Ginagori/ai-project-playbook/issues

---

*Built by Nivanta AI Team*
