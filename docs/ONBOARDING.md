# AI Project Playbook - Onboarding para Nivanta AI Team

## Requisitos Previos

- Docker Desktop instalado y corriendo
- Claude Code (CLI o VSCode Extension)
- Credenciales de Supabase (compartidas por el equipo)

## Instalación Rápida (10 minutos)

### Paso 1: Descargar la imagen Docker

```bash
docker pull ghcr.io/ginagori/ai-project-playbook:latest
```

### Paso 2: Configurar Variables de Entorno

Crea un archivo `.env` en tu directorio home o en el proyecto con:

```env
# Supabase - Shared Team Database
SUPABASE_URL=https://lnuyanxodyuoadawvjle.supabase.co
SUPABASE_ANON_KEY=<pedir a Natalia>
PLAYBOOK_TEAM_ID=9f1c0ad9-3ba3-4ccf-8a02-fcbb94fcab6d

# Tu identificador de usuario
PLAYBOOK_USER=tu_nombre
```

> **IMPORTANTE:** Pide la `SUPABASE_ANON_KEY` a Natalia. No la compartas fuera del equipo.

### Paso 3: Configurar Claude Code

#### Opción A: VSCode Extension (Recomendado)

Edita el archivo `%APPDATA%\Code\User\mcp.json` (Windows) o `~/.config/Code/User/mcp.json` (Linux/Mac):

```json
{
  "servers": {
    "playbook": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-e", "SUPABASE_URL",
        "-e", "SUPABASE_ANON_KEY",
        "-e", "PLAYBOOK_TEAM_ID",
        "-e", "PLAYBOOK_USER",
        "ghcr.io/ginagori/ai-project-playbook:latest"
      ],
      "type": "stdio",
      "env": {
        "SUPABASE_URL": "https://lnuyanxodyuoadawvjle.supabase.co",
        "SUPABASE_ANON_KEY": "<tu_anon_key>",
        "PLAYBOOK_TEAM_ID": "9f1c0ad9-3ba3-4ccf-8a02-fcbb94fcab6d",
        "PLAYBOOK_USER": "tu_nombre"
      }
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
      "args": [
        "run", "--rm", "-i",
        "-e", "SUPABASE_URL=https://lnuyanxodyuoadawvjle.supabase.co",
        "-e", "SUPABASE_ANON_KEY=<tu_anon_key>",
        "-e", "PLAYBOOK_TEAM_ID=9f1c0ad9-3ba3-4ccf-8a02-fcbb94fcab6d",
        "-e", "PLAYBOOK_USER=tu_nombre",
        "ghcr.io/ginagori/ai-project-playbook:latest"
      ]
    }
  }
}
```

#### Opción C: Desarrollo Local (sin Docker)

Si prefieres correr el MCP server localmente:

1. Clona el repo:
```bash
git clone https://github.com/Ginagori/ai-project-playbook.git
cd ai-project-playbook
```

2. Crea el entorno virtual:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

3. Configura `.env` en el directorio del proyecto

4. Configura Claude Code (`~/.claude.json`):
```json
{
  "mcpServers": {
    "playbook": {
      "command": "C:\\ruta\\a\\ai-project-playbook\\.venv\\Scripts\\python.exe",
      "args": ["-m", "mcp_server.playbook_mcp"],
      "cwd": "C:\\ruta\\a\\ai-project-playbook"
    }
  }
}
```

### Paso 4: Reiniciar Claude Code

Cierra y vuelve a abrir VSCode o la terminal de Claude Code.

### Paso 5: Verificar instalación

En Claude Code, escribe:

```
Usa playbook_team_status para verificar la conexión
```

Deberías ver:

```
✓ Supabase Connected
✓ Team: Nivanta AI
✓ Lessons in database: X
```

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

### Comandos disponibles (27 tools)

#### Project Management (10 tools)
| Tool | Descripción |
|------|-------------|
| `playbook_start_project` | Iniciar proyecto nuevo |
| `playbook_answer` | Responder preguntas del agente |
| `playbook_continue` | Continuar sesión existente |
| `playbook_search` | Buscar en el playbook |
| `playbook_get_status` | Ver estado del proyecto |
| `playbook_list_sessions` | Listar sesiones activas (locales + equipo) |
| `playbook_get_claude_md` | Obtener CLAUDE.md generado |
| `playbook_get_prd` | Obtener PRD generado |
| `playbook_link_repo` | Vincular repositorio GitHub al proyecto |
| `playbook_get_repo` | Obtener URL del repositorio |

#### Agent Factory (8 tools)
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

#### Meta-Learning (6 tools)
| Tool | Descripción |
|------|-------------|
| `playbook_complete_project` | Completar proyecto y guardar lecciones |
| `playbook_get_recommendations` | Obtener recomendaciones basadas en proyectos anteriores |
| `playbook_find_similar` | Buscar proyectos similares del equipo |
| `playbook_suggest_stack` | Sugerencias de tech stack |
| `playbook_learning_stats` | Estadísticas de aprendizaje del equipo |
| `playbook_add_lesson` | Agregar lección manualmente |

#### Team Collaboration (3 tools)
| Tool | Descripción |
|------|-------------|
| `playbook_team_status` | Ver estado de conexión al equipo |
| `playbook_share_lesson` | Compartir una lección con el equipo |
| `playbook_team_lessons` | Ver lecciones del equipo |

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

8. Al completar:
   - playbook_complete_project guarda lecciones aprendidas
   - Lecciones quedan disponibles para TODO el equipo Nivanta
```

---

## Cómo Funciona el Meta-Learning Compartido

### Las lecciones se comparten automáticamente

Cuando completas un proyecto:
1. `playbook_complete_project` extrae patrones exitosos
2. Las lecciones se guardan en Supabase con tu nombre
3. Tu compañero puede ver esas lecciones inmediatamente
4. Las recomendaciones se basan en proyectos de TODO el equipo

### Ejemplo de flujo compartido

```
Natalia completa un proyecto de "veterinaria SaaS" con Next.js + Supabase
  → Se guardan 3 lecciones aprendidas

Al día siguiente, su compañero inicia un proyecto "clínica dental SaaS"
  → playbook_get_recommendations sugiere usar Supabase para auth
  → La sugerencia viene de la lección de Natalia
```

### Agregar lecciones manualmente

Si descubres algo útil durante el desarrollo:

```
Usa playbook_add_lesson con:
- title: "RLS requiere políticas para INSERT separadas"
- description: "Supabase RLS no aplica SELECT policies a INSERT"
- recommendation: "Crear policies explícitas para INSERT y UPDATE"
- category: "pitfall"
- tags: "supabase, rls, security"
```

---

## Troubleshooting

### "playbook tools not found"

1. Verifica que Docker está corriendo
2. Verifica que la imagen existe: `docker images | grep playbook`
3. Reinicia Claude Code

### "Supabase not connected"

1. Verifica las variables de entorno en tu configuración
2. Asegúrate de tener la ANON_KEY correcta (pide a Natalia)
3. Prueba con `playbook_team_status`

### "connection refused"

1. Prueba manualmente: `docker run --rm -i ghcr.io/ginagori/ai-project-playbook:latest`
2. Si falla, actualiza: `docker pull ghcr.io/ginagori/ai-project-playbook:latest`

### Los datos no aparecen entre miembros del equipo

1. Verifica que ambos usan el mismo `PLAYBOOK_TEAM_ID`
2. Verifica conexión con `playbook_team_status`
3. Los proyectos se sincronizan automáticamente con Supabase
4. Usa `playbook_list_sessions` para ver proyectos de todo el equipo

---

## Colaboración en Equipo

### Proyectos Compartidos

Los proyectos se sincronizan automáticamente con Supabase:
- Cuando inicias un proyecto, se guarda en la nube
- Tus compañeros pueden ver y continuar tus proyectos
- Cada proyecto muestra quién lo creó (`created_by`)

### Vincular Repositorios

Para que el equipo sepa dónde está el código de cada proyecto:

```
playbook_link_repo session_id="abc123" repo_url="https://github.com/Nivanta/mi-proyecto"
```

Esto hace que `playbook_list_sessions` muestre un link clickeable al repo:

```
## Active Sessions
### Team Sessions (shared via Supabase)
- **abc123**: Mi Proyecto (planning, by natalia) | [repo](https://github.com/...)
```

### Continuar el proyecto de un compañero

```
# Ver proyectos del equipo
playbook_list_sessions

# Continuar cualquier proyecto (tuyo o de un compañero)
playbook_continue session_id="abc123"
```

---

## Seguridad

- **NO compartir** la `SUPABASE_ANON_KEY` fuera del equipo Nivanta
- **NO commitear** archivos `.env` a repositorios públicos
- Los datos de proyectos se almacenan por equipo con Row Level Security
- Cada miembro ve solo los datos de su equipo

---

## Soporte

- GitHub: https://github.com/Ginagori/ai-project-playbook
- Issues: https://github.com/Ginagori/ai-project-playbook/issues

---

*Built by Nivanta AI Team*
