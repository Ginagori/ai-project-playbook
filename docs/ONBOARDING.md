# AI Project Playbook - Onboarding para Nivanta AI Team

## Requisitos Previos

- Docker Desktop instalado y corriendo
- Claude Code (CLI o VSCode Extension)
- Credenciales de Supabase (compartidas por el equipo)

## Instalacion Rapida (10 minutos)

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

#### Opcion A: VSCode Extension (Recomendado)

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

#### Opcion B: Claude Code CLI (Global)

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

#### Opcion C: Desarrollo Local (sin Docker)

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
      "command": "<ruta-absoluta-al-repo>\\.venv\\Scripts\\python.exe",
      "args": ["-m", "mcp_server.playbook_mcp"],
      "cwd": "<ruta-absoluta-al-repo>"
    }
  }
}
```

> Reemplaza `<ruta-absoluta-al-repo>` con la ruta donde clonaste el repositorio.

### Paso 4: Instalar el skill `/archie` (global)

Archie es el agente PM de Nivanta AI. Para invocarlo desde CUALQUIER proyecto:

```powershell
# Crear directorio global de commands
mkdir "$env:USERPROFILE\.claude\commands" -Force

# Copiar el skill desde el repo del Playbook (ajustar ruta segun tu maquina)
copy "<ruta-al-repo>\.claude\commands\archie.md" "$env:USERPROFILE\.claude\commands\archie.md"
```

> **NOTA:** Ajusta `<ruta-al-repo>` a la ruta donde tienes clonado `ai-project-playbook`.
> Cuando se actualice `archie.md` en el repo (git pull), hay que volver a copiar.
> Ver documentacion completa del agente: `docs/ARCHIE.md`

### Paso 5: Reiniciar Claude Code

Cierra y vuelve a abrir VSCode o la terminal de Claude Code.

### Paso 6: Verificar instalacion

En Claude Code, escribe:

```
Usa playbook_team_status para verificar la conexion
```

Deberias ver:

```
Supabase Connected
Team: Nivanta AI
Lessons in database: X
```

Tambien verifica que `/archie` aparece como skill disponible.

---

## Uso de Archie (recomendado)

La forma principal de interactuar con el Playbook es a traves de **Archie**, el agente PM:

```
/archie quiero construir un SaaS de gestion de inventarios
```

Archie inicia Discovery, cruza con proyectos anteriores, sugiere patterns, y te guia hasta el deployment.

Otros usos:
```
/archie estado de KOMPLIA          # consultar proyecto existente
/archie que aprendimos sobre RLS?  # buscar conocimiento acumulado
/archie                            # saludo + resumen de proyectos
```

> Ver documentacion completa: `docs/ARCHIE.md`

---

## Uso Directo (MCP tools)

### Iniciar un nuevo proyecto

```
Quiero crear una app de inventarios para una ferreteria
```

El agente iniciara el flujo de Discovery con preguntas sobre:
- Tipo de proyecto (SaaS, API, Agent, Multi-Agent, Platform)
- Tech stack preferido
- Funcionalidades principales
- Escala esperada

### Comandos disponibles (28 tools)

#### Project Management (13 tools)
| Tool | Descripcion |
|------|-------------|
| `playbook_start_project` | Iniciar proyecto nuevo |
| `playbook_answer` | Responder preguntas del agente |
| `playbook_continue` | Continuar sesion existente |
| `playbook_search` | Buscar en el playbook |
| `playbook_get_status` | Ver estado del proyecto |
| `playbook_list_sessions` | Listar sesiones activas (locales + equipo) |
| `playbook_get_claude_md` | Obtener CLAUDE.md generado |
| `playbook_get_prd` | Obtener PRD generado |
| `playbook_get_prp` | Obtener PRP de un feature (execution blueprint) |
| `playbook_execution_package` | Paquete completo para implementacion autonoma |
| `playbook_handoff` | Escribir todos los artefactos a disco |
| `playbook_link_repo` | Vincular repositorio GitHub al proyecto |
| `playbook_get_repo` | Obtener URL del repositorio |

#### Agent Factory (8 tools)
| Tool | Descripcion |
|------|-------------|
| `playbook_run_task` | Ejecutar tarea con el mejor agente |
| `playbook_run_pipeline` | Pipeline: Research -> Plan -> Code -> Review -> Test |
| `playbook_code_review` | Reviews paralelos de codigo |
| `playbook_supervised_task` | Tarea con supervisor |
| `playbook_research` | Investigar tema en el playbook |
| `playbook_plan_feature` | Planear implementacion de feature |
| `playbook_generate_code` | Generar codigo |
| `playbook_generate_tests` | Generar tests |

#### Meta-Learning (6 tools)
| Tool | Descripcion |
|------|-------------|
| `playbook_complete_project` | Completar proyecto y guardar lecciones |
| `playbook_get_recommendations` | Recomendaciones basadas en proyectos anteriores |
| `playbook_find_similar` | Buscar proyectos similares del equipo |
| `playbook_suggest_stack` | Sugerencias de tech stack |
| `playbook_learning_stats` | Estadisticas de aprendizaje del equipo |
| `playbook_add_lesson` | Agregar leccion localmente (ver nota abajo) |

> **IMPORTANTE:** `playbook_add_lesson` solo guarda localmente (se pierde entre sesiones).
> Para lecciones persistentes compartidas con el equipo, usa **`playbook_share_lesson`**.

#### Quality & Health (3 tools)
| Tool | Descripcion |
|------|-------------|
| `playbook_evaluate_artifact` | Evaluar calidad de CLAUDE.md, PRD o plan |
| `playbook_system_review` | Revision del proceso completo del proyecto |
| `playbook_health_check` | Dashboard de salud de todos los proyectos (Heartbeat Engine) |

#### Team Collaboration (3 tools)
| Tool | Descripcion |
|------|-------------|
| `playbook_team_status` | Ver estado de conexion al equipo |
| `playbook_share_lesson` | Compartir una leccion con el equipo (PERSISTENTE) |
| `playbook_team_lessons` | Ver lecciones del equipo |

---

## Flujo de Trabajo Tipico

```
1. Usuario: "Quiero crear un sistema de gestion de citas para veterinarias"

2. Agente (Discovery):
   - Tipo de proyecto? (SaaS, API, Agent)
   - Tech stack preferido?
   - Preguntas de seguimiento segun tipo
   - Cruza con proyectos similares (Memory Engine)

3. Usuario responde las preguntas

4. Agente (Planning):
   - Genera CLAUDE.md con global rules + lessons aprendidos
   - Genera PRD con features priorizados + gotchas de proyectos pasados

5. Agente (Roadmap):
   - Descompone en features implementables (max 10 para MVP)
   - Incluye features de dominio + features aprendidos

6. Agente (Implementation):
   - Genera PRPs (execution blueprints) por feature
   - PIV Loop: Plan -> Implement -> Validate

7. Handoff:
   - playbook_handoff escribe artefactos a disco
   - Claude Code puede ejecutar los PRPs autonomamente

8. Al completar:
   - playbook_complete_project guarda lecciones aprendidas
   - Lecciones quedan disponibles para TODO el equipo Nivanta
```

---

## Como Funciona el Meta-Learning Compartido

### Las lecciones se comparten automaticamente

Cuando completas un proyecto:
1. `playbook_complete_project` extrae patrones exitosos
2. Las lecciones se guardan en Supabase con tu nombre
3. Tu companero puede ver esas lecciones inmediatamente
4. Las recomendaciones se basan en proyectos de TODO el equipo

### Ejemplo de flujo compartido

```
Natalia completa un proyecto de "veterinaria SaaS" con Next.js + Supabase
  -> Se guardan 3 lecciones aprendidas

Al dia siguiente, su companero inicia un proyecto "clinica dental SaaS"
  -> playbook_get_recommendations sugiere usar Supabase para auth
  -> La sugerencia viene de la leccion de Natalia
```

### Agregar lecciones manualmente

Si descubres algo util durante el desarrollo, usa `playbook_share_lesson` para que persista:

```
Usa playbook_share_lesson con:
- title: "RLS requiere politicas para INSERT separadas"
- description: "Supabase RLS no aplica SELECT policies a INSERT"
- recommendation: "Crear policies explicitas para INSERT y UPDATE"
- category: "pitfall"
- tags: "supabase, rls, security"
```

> **NO uses `playbook_add_lesson`** para lecciones importantes — solo guarda localmente y se pierde.

---

## Troubleshooting

### "playbook tools not found"

1. Verifica que Docker esta corriendo
2. Verifica que la imagen existe: `docker images | grep playbook`
3. Reinicia Claude Code

### "Supabase not connected"

1. Verifica las variables de entorno en tu configuracion
2. Asegurate de tener la ANON_KEY correcta (pide a Natalia)
3. Prueba con `playbook_team_status`

### "connection refused"

1. Prueba manualmente: `docker run --rm -i ghcr.io/ginagori/ai-project-playbook:latest`
2. Si falla, actualiza: `docker pull ghcr.io/ginagori/ai-project-playbook:latest`

### Los datos no aparecen entre miembros del equipo

1. Verifica que ambos usan el mismo `PLAYBOOK_TEAM_ID`
2. Verifica conexion con `playbook_team_status`
3. Los proyectos se sincronizan automaticamente con Supabase
4. Usa `playbook_list_sessions` para ver proyectos de todo el equipo

### "CRITICAL: Core Soul integrity check FAILED"

Esto significa que `agent/core_soul.py` fue modificado sin seguir el Core Soul Change Protocol.
1. No modifiques `agent/core_soul.py` directamente
2. Cualquier cambio requiere 2 security leads approval (CODEOWNERS)
3. Contacta a Natalia si ves este error

### "/archie no aparece como skill"

1. Verifica que copiaste `archie.md` al directorio global:
   ```powershell
   ls "$env:USERPROFILE\.claude\commands\archie.md"
   ```
2. Reinicia Claude Code
3. Si no existe, vuelve a copiar desde el repo (Paso 4)

---

## Colaboracion en Equipo

### Proyectos Compartidos

Los proyectos se sincronizan automaticamente con Supabase:
- Cuando inicias un proyecto, se guarda en la nube
- Tus companeros pueden ver y continuar tus proyectos
- Cada proyecto muestra quien lo creo (`created_by`)

### Vincular Repositorios

Para que el equipo sepa donde esta el codigo de cada proyecto:

```
playbook_link_repo session_id="abc123" repo_url="https://github.com/Nivanta/mi-proyecto"
```

Esto hace que `playbook_list_sessions` muestre un link clickeable al repo.

### Continuar el proyecto de un companero

```
# Ver proyectos del equipo
playbook_list_sessions

# Continuar cualquier proyecto (tuyo o de un companero)
playbook_continue session_id="abc123"
```

---

## Seguridad

### Datos del equipo
- **NO compartir** la `SUPABASE_ANON_KEY` fuera del equipo Nivanta
- **NO commitear** archivos `.env` a repositorios publicos
- Los datos de proyectos se almacenan por equipo con Row Level Security
- Cada miembro ve solo los datos de su equipo

### Archie (Core Soul)
- `agent/core_soul.py` contiene la identidad inmutable de Archie (7 directivas)
- Protegido por CODEOWNERS — requiere 2 security leads para cualquier cambio
- SHA-256 hash verificado en cada startup del MCP server
- Si el hash no coincide, Archie se niega a arrancar
- Ver `docs/ARCHIE.md` para detalles completos

### Propiedad Intelectual
- Archie tiene acceso a TODOS los proyectos Nivanta AI (by design)
- Directiva 2 (IP Protection) impide filtrar detalles de proyectos
- Nunca incluir informacion propietaria en artefactos destinados a uso externo
- Los proyectos, PRDs, y arquitecturas son CONFIDENCIALES

---

## Soporte

- GitHub: https://github.com/Ginagori/ai-project-playbook
- Issues: https://github.com/Ginagori/ai-project-playbook/issues

---

*Built by Nivanta AI Team*
