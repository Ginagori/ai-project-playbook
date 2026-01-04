# 🤖 AI Project Playbook Unificado

**Tu Sistema Completo para Desarrollo con AI Coding Assistants**

---

## 📖 ¿Qué es este Playbook?

Este es tu **sistema definitivo** para desarrollar aplicaciones y agentes IA de forma estructurada, escalable y profesional.

No es solo teoría - es el sistema que diferencia al **top 5%** de developers que tienen **88% code acceptance** del **90%** que tiene solo **30% acceptance**.

---

## 🎯 Para Quién es Este Playbook

✅ **Perfecto para ti si:**
- Usas AI coding assistants (Claude, Cursor, Copilot, etc.)
- Quieres construir aplicaciones que escalen a millones de usuarios
- Necesitas un sistema reproducible para cada proyecto
- Buscas integrar prototipos (Lovable, v0, Bolt) con producción profesional
- Desarrollas SaaS, agentes IA, o aplicaciones multi-tenant

❌ **NO es para ti si:**
- Prefieres "vibe-based coding" sin estructura
- Solo haces proyectos one-off sin escalabilidad
- No quieres invertir tiempo en crear sistemas

---

## 🏗️ Estructura del Playbook

```
📁 ai-project-playbook/
│
├── 📂 00-overview/           ← EMPIEZA AQUÍ
│   ├── README.md             # Esta página
│   ├── philosophy.md         # El "por qué" detrás del sistema
│   └── quick-start.md        # Guía rápida de 15 minutos
│
├── 📂 01-discovery/          ← FASE 1: Define el QUÉ
│   ├── requirement-gathering.md
│   ├── technology-research.md
│   ├── prd-creation.md       # Crea tu PRD (Product Requirements Document)
│   └── mvp-scoping.md
│
├── 📂 02-planning/           ← FASE 2: Configura el SISTEMA
│   ├── claude-md-creation.md      # Tu archivo de "reglas del juego"
│   ├── global-rules.md            # Las 7 secciones esenciales
│   ├── tech-stack-selection.md
│   ├── architecture-patterns.md   # VSA, MVC, Clean Architecture
│   └── reference-guides.md        # Guías de contexto para la AI
│
├── 📂 03-roadmap/            ← FASE 3: Planifica FEATURES
│   ├── feature-breakdown.md
│   ├── planning-prompts.md        # Plantillas de prompts reutilizables
│   ├── slash-commands.md          # /plan, /execute, /validate
│   └── plan-templates.md          # Estructura agent-to-agent
│
├── 📂 04-implementation/     ← FASE 4: Ejecuta el PIV LOOP
│   ├── piv-loop-workflow.md       # Plan → Implement → Validate → Iterate
│   ├── planning-phase.md          # Research, vibe planning, structured plan
│   ├── implementation-phase.md    # /execute command, step-by-step
│   ├── validation-pyramid.md      # 5 niveles de validación
│   ├── iteration-strategies.md    # Qué hacer cuando falla
│   ├── ai-ready-codebases.md      # 7 Pilares para código AI-friendly ← NUEVO
│   ├── architecture-patterns-guide.md  # 6 patrones comparados ← NUEVO
│   └── vertical-slice-guide.md    # Guía completa VSA ← NUEVO
│
├── 📂 05-deployment/         ← FASE 5: Escala de MVP a MILLONES
│   ├── 01-deployment-phases.md           # Las 4 fases de crecimiento
│   ├── 02-multi-tenancy-design.md        # Multi-tenancy desde día 1
│   ├── 03-mvp-deployment.md              # Netlify + Railway ($300-500/mes)
│   ├── 04-growth-deployment.md           # Netlify + Cloud Run ($1,500-3K/mes)
│   ├── 05-scale-deployment.md            # Netlify + GKE ($8K-15K/mes)
│   ├── 06-enterprise-deployment.md       # Multi-cloud ($50K-150K/mes)
│   ├── netlify/                          # Configuraciones Netlify
│   ├── docker/                           # Dockerfiles optimizados
│   ├── kubernetes/                       # Manifests de K8s
│   └── ci-cd/                            # Pipelines de CI/CD
│
├── 📂 06-advanced/           ← TEMAS AVANZADOS
│   ├── lovable-to-production.md   # Migrar prototipos a producción
│   ├── design-system-creation.md  # Sistema de diseño robusto
│   ├── frontend-backend-split.md  # Workflows separados
│   ├── context-engineering.md     # 52+ comandos, PRP, hooks
│   ├── archon-architecture.md     # Multi-agent orchestration
│   ├── meta-reasoning.md          # Mejora continua del sistema
│   ├── subagents-framework.md     # Subagentes para research paralelo ← NUEVO
│   └── parallel-implementation.md # Git worktrees y trabajo paralelo ← NUEVO
│
├── 📂 templates/             ← PLANTILLAS LISTAS PARA USAR
│   ├── CLAUDE.md.template
│   ├── prd-template.md
│   ├── plan-template.md
│   ├── validate-command.md
│   ├── code-review.md
│   └── docker-compose.yml
│
├── 📂 .claude/commands/      ← SLASH COMMANDS AUTOMATIZADOS
│   ├── start-project.md      # /start-project - Inicialización guiada
│   ├── migrate-lovable.md    # /migrate-lovable - PM para migración
│   ├── new-worktree.md       # /new-worktree - Setup worktrees ← NUEVO
│   └── merge-worktrees.md    # /merge-worktrees - Merge con validation ← NUEVO
│
└── 📂 examples/              ← EJEMPLOS REALES
    ├── veterinaria-saas/     # Sistema de gestión veterinaria
    ├── agencia-empleados/    # Agencia de empleados digitales (escala millones)
    └── capacitaciones/       # App de capacitaciones (tu proyecto)
```

---

## 🚀 Cómo Usar Este Playbook

### 🟢 Opción 1: Quick Start (15 minutos)
**Para proyectos pequeños o aprendizaje rápido:**

1. Lee `00-overview/quick-start.md`
2. Crea tu CLAUDE.md usando `templates/CLAUDE.md.template`
3. Ejecuta tu primer PIV Loop con `04-implementation/piv-loop-workflow.md`

### 🟡 Opción 2: Proyecto Completo (2-4 horas setup inicial)
**Para SaaS, agentes IA, o proyectos profesionales:**

1. **Discovery** (30-60 min):
   - Define requisitos con `01-discovery/requirement-gathering.md`
   - Crea tu PRD con `01-discovery/prd-creation.md`

2. **Planning** (60-90 min):
   - Configura CLAUDE.md con `02-planning/claude-md-creation.md`
   - Define arquitectura con `02-planning/architecture-patterns.md`
   - Crea guías de referencia con `02-planning/reference-guides.md`

3. **Roadmap** (30-60 min):
   - Descompón features con `03-roadmap/feature-breakdown.md`
   - Configura slash commands con `03-roadmap/slash-commands.md`

4. **Implementation** (iterativo):
   - Ejecuta PIV Loops con `04-implementation/piv-loop-workflow.md`
   - Valida con `04-implementation/validation-pyramid.md`

5. **Deployment** (según fase):
   - Empieza MVP con `05-deployment/03-mvp-deployment.md`
   - Escala según crecimiento con fases 4-6

### 🔵 Opción 3: Migración de Prototipos
**Si ya tienes un prototipo en Lovable/v0/Bolt:**

1. Lee `06-advanced/lovable-to-production.md`
2. Crea sistema de diseño con `06-advanced/design-system-creation.md`
3. Implementa arquitectura profesional con `02-planning/architecture-patterns.md`
4. Despliega con estrategia de fases `05-deployment/01-deployment-phases.md`

---

## 📊 El Framework PIV Loop (Core del Playbook)

Todo en este Playbook gira alrededor del **PIV Loop** - el framework mental que diferencia al top 5%:

```
┌─────────────────────────────────────────────┐
│  🔄 EL PIV LOOP                             │
├─────────────────────────────────────────────┤
│                                             │
│  📋 PLAN                                    │
│  ├─ Research (contexto existente)          │
│  ├─ Vibe Planning (brainstorm)             │
│  └─ Structured Plan (plan formal)          │
│                                             │
│  ⬇️                                          │
│                                             │
│  🔨 IMPLEMENT                               │
│  ├─ Read context references                │
│  ├─ Execute step-by-step                   │
│  ├─ Write tests                            │
│  └─ No TODOs, no improvisation             │
│                                             │
│  ⬇️                                          │
│                                             │
│  ✅ VALIDATE                                │
│  ├─ Level 1: Syntax & Style                │
│  ├─ Level 2: Type Safety                   │
│  ├─ Level 3: Unit Tests                    │
│  ├─ Level 4: Integration Tests             │
│  └─ Level 5: Human Review                  │
│                                             │
│  ⬇️                                          │
│                                             │
│  🔁 ITERATE                                 │
│  ├─ Si falla → mejora el SISTEMA           │
│  ├─ Actualiza CLAUDE.md                    │
│  ├─ Mejora prompts/comandos                │
│  └─ Documenta patrones                     │
│                                             │
└─────────────────────────────────────────────┘
```

**Ver detalles completos en:** `04-implementation/piv-loop-workflow.md`

---

## 🎓 Filosofía del Playbook

### 1. **Sistema sobre Talento**
El 90% de developers usa AI sin sistema → 30% code acceptance.
El top 5% tiene sistemas → 88% code acceptance.

**La diferencia no es el talento. Es el SISTEMA.**

### 2. **AI-First, pero Human-Guided**
La AI ejecuta el trabajo técnico, pero tú:
- Defines la visión y requisitos
- Creas el sistema (CLAUDE.md, commands, validation)
- Revisas alineación estratégica (Level 5: Human Review)

### 3. **Escalabilidad desde Día 1**
No construyas MVP que luego hay que rehacer.
Diseña arquitectura que escale:
- Multi-tenancy desde el inicio
- TypeScript + Python (tipado estricto)
- Patterns reproducibles (VSA, Clean Architecture)
- 4 fases de deployment claras (MVP → Enterprise)

### 4. **"Fix the System, Not Just the Bug"**
Cuando algo falla, pregunta:
- ¿Por qué mi CLAUDE.md no previno esto?
- ¿Qué prompt/comando necesito crear?
- ¿Qué validación falta en mi pyramid?

**Cada bug es una oportunidad de mejorar el sistema.**

### 5. **Documentation as Code**
- CLAUDE.md = reglas automáticas para la AI
- Reference guides = contexto cargado on-demand
- Slash commands = prompts reutilizables
- Plan templates = agent-to-agent communication

**Ver filosofía completa en:** `00-overview/philosophy.md`

---

## 🛠️ Tech Stack Recomendado

Este Playbook asume (pero no requiere) el siguiente stack:

### Frontend
- **TypeScript** (type safety non-negotiable)
- **React** (componentes, hooks)
- **Vite/Next.js** (bundling, SSR)
- **Tailwind CSS** (styling rápido, design system)
- **shadcn/ui** (componentes pre-built, customizables)

### Backend
- **Python 3.13+** (async, type hints)
- **FastAPI** (API moderna, async, OpenAPI auto-docs)
- **Pydantic AI** (AI agents framework)
- **PostgreSQL** (multi-tenancy con RLS)
- **Structlog** (logging para AI consumption)

### DevOps
- **UV** (Python package manager ultra-rápido)
- **Docker** (containerización)
- **Docker Compose** (desarrollo local)
- **Kubernetes** (producción scale/enterprise)
- **GitHub Actions** (CI/CD)

### Validación
- **ruff, black** (Python linting/formatting)
- **mypy, pyright** (type checking)
- **pytest** (testing)
- **eslint, prettier** (TypeScript linting/formatting)
- **vitest** (TypeScript testing)

**Puedes adaptar este stack - ver:** `02-planning/tech-stack-selection.md`

---

## 📚 Recursos Complementarios

### Del Curso Original
- [Agentic Coding Course](https://github.com/dynamous-community/agentic-coding-course)
- [Dynamous Community](https://community.dynamous.ai)

### Templates Incluidos
- FastAPI + Pydantic AI Starter (con VSA)
- CLAUDE.md para diferentes tipos de proyectos
- Plan templates optimizados para agents
- Validation commands listos para usar

### Ejemplos Reales
- Sistema veterinario multi-tenant
- Agencia de empleados digitales (escala millones)
- App de capacitaciones en salud/seguridad

---

## 🎯 Próximos Pasos

1. **Si es tu primera vez:**
   - Lee `00-overview/philosophy.md` (10 min)
   - Lee `00-overview/quick-start.md` (5 min)
   - Crea tu primer CLAUDE.md (15 min)

2. **Si vas a empezar un proyecto nuevo:**
   - Sigue `01-discovery/` completo (30-60 min)
   - Configura con `02-planning/` (60-90 min)
   - Ejecuta primer PIV Loop con `04-implementation/` (1-2 horas)

3. **Si tienes un prototipo existente:**
   - Lee `06-advanced/lovable-to-production.md`
   - Implementa `06-advanced/design-system-creation.md`
   - Migra con estrategia de fases `05-deployment/`

---

## 💡 Mantente Actualizado

Este Playbook evoluciona con:
- Nuevos patrones descubiertos en proyectos reales
- Mejoras en prompts y comandos
- Nuevas herramientas y frameworks
- Feedback de la comunidad

**Version:** 1.1.0 (2026-01-03)
**Última actualización:** SESIÓN 6 - Módulos 8-12 integrados (7 Pilares AI-Ready, Arquitectura VSA, Subagents, Worktrees)
**Archivos totales:** 63 archivos, ~33,500 líneas

---

## 📞 Soporte

- Issues y mejoras: Tu repositorio de GitHub
- Comunidad: [Dynamous Community](https://community.dynamous.ai)
- Curso original: [Agentic Coding Course](https://github.com/dynamous-community/agentic-coding-course)

---

**🚀 ¡Ahora ve a construir aplicaciones increíbles con AI!**

Tu sistema está listo. Solo falta ejecutar.

**START HERE → `00-overview/quick-start.md`**
