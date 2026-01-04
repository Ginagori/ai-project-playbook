# Framework de Subagents: Ejecución Paralela con AI

> **Fuente:** Módulo 11 del Agentic Coding Course
> **Aplicable a:** Proyectos que requieren investigación paralela o workflows complejos

---

## 💡 La Idea Central

**El verdadero poder de los subagents no es solo aislamiento de contexto - es la capacidad de correr hasta 10 agentes en paralelo para investigación y exploración simultánea.**

Los subagents son ventanas de contexto aisladas con system prompts custom que permiten:
- Paralelizar trabajo de investigación
- Aislar contexto para tareas específicas
- Crear agentes especializados reutilizables

---

## Conceptos Fundamentales

### ¿Qué es un Subagent?

Un subagent es:
- Una instancia aislada de Claude con su propio contexto
- Un system prompt especializado para una tarea
- Una herramienta que el agente principal puede invocar

### El Flujo de Context Handoff

```
Tú → Main Agent → Subagent → Main Agent → Tú
         ↓              ↓
    Handoff #1     Handoff #2
   (Puede perder    (Puede perder
    contexto)        contexto)
```

**El problema:** Cada handoff puede perder contexto.

**La solución:** Controlar obsesivamente los formatos de output.

### Cuándo Usar Subagents

| ✅ Excelente Para | ❌ No Ideal Para |
|-------------------|------------------|
| Investigación paralela (5-10 exploraciones simultáneas) | Tareas secuenciales simples |
| Code review con feedback loops controlados | Priming del agente principal |
| Checks de compliance en múltiples módulos | Tareas que requieren TODO el contexto |
| Análisis de plan vs ejecución | |
| Tareas context-heavy que contaminarían el thread principal | |

---

## Estructura de Archivos

Los subagents viven en `.claude/agents/*.md` con configuración en frontmatter:

```markdown
---
name: Your Agent Name
description: Clear description of when to use this agent
model: haiku | sonnet | opus
tools: ["*"] # or specific tool list
---

# Tu system prompt del agente va aquí

Define su rol, approach, y formato de output
```

### Campos del Frontmatter

| Campo | Descripción | Valores |
|-------|-------------|---------|
| `name` | Nombre del agente | String descriptivo |
| `description` | Cuándo usar este agente (para el main agent) | Texto detallado con ejemplos |
| `model` | Modelo a usar | `haiku`, `sonnet`, `opus` |
| `tools` | Herramientas permitidas | `["*"]` para todas, o lista específica |
| `color` | Color en UI (opcional) | `red`, `blue`, `green`, etc. |

---

## Agentes Built-in

Claude Code incluye agentes built-in que puedes usar directamente:

| Agente | Propósito |
|--------|-----------|
| **Explore** | Navegación rápida del codebase |
| **Plan** | Diseño de planes de implementación |
| **General Purpose** | Investigación y tareas generales |

---

## Creando Subagents Custom

### Componentes Críticos

Cada subagent efectivo tiene 4 componentes:

1. **Role Definition** - Misión y propósito claros
2. **Context Gathering** - Qué archivos e info necesita
3. **Approach/Steps** - Instrucciones específicas
4. **Output Format** - Resultados estructurados y parseables

> **Insight clave:** El **formato de output** es el lever más crítico. Controla lo que el main agent ve y cómo responde.

---

## Template: Code Reviewer Agent

Este es un ejemplo completo de un subagent de code review:

```markdown
---
name: code-reviewer
description: Use this agent when you want to review newly written code or features before committing. This agent checks code against project standards including type safety, architecture compliance, logging standards, and KISS/YAGNI principles.
model: sonnet
tools: ["Read", "Glob", "Grep"]
---

You are an expert code reviewer specializing in Python FastAPI applications with vertical slice architecture.

## Core Review Responsibilities

### 1. Type Safety (CRITICAL)
- All functions MUST have complete type annotations
- No `Any` types without explicit justification
- Ensure code would pass MyPy and Pyright in strict mode
- Flag any missing return type annotations

### 2. Architecture Compliance
- **Vertical Slice**: Features properly isolated in separate directories
- **Naming**: Modules follow pattern: `models.py`, `schemas.py`, `routes.py`, `service.py`
- **Shared Logic**: Only shared across 3+ features
- **Database Patterns**: Models inherit from `Base` and `TimestampMixin`

### 3. Logging Standards
- Uses structured logging via `from app.core.logging import get_logger`
- Event names follow: `{domain}.{component}.{action}_{state}`
- Examples: `user.registration_completed`, `product.create_started`
- Exception logs include `exc_info=True`

### 4. Design Principles
- **KISS**: Prefer readable solutions over clever abstractions
- **YAGNI**: Don't add features until actually needed

## Review Process

1. **Initial Assessment**: Scan for obvious issues
2. **Detailed Analysis**: Review each component
3. **Type Checking**: Verify strict mode compliance
4. **Documentation Quality**: Check docstrings

## Output Format

Save report to `.agents/code-reviews/[review-name].md`

**✅ Strengths**
- List positive aspects

**⚠️ Issues Found**
- Category (Type Safety, Architecture, Logging)
- Severity (Critical, Major, Minor)
- Description and suggested fix

**🔍 Questions/Clarifications**
- Ask about unclear design decisions

**✨ Recommendations**
- Suggestions for improvements

**📋 Review Summary**
- Overall: Ready to commit / Needs revision / Needs major changes
- Number of issues by severity
- Critical blockers

## Important Guidelines

- Be thorough but constructive
- Prioritize type safety as critical
- Suggest concrete fixes, not just problems
- When done, instruct main agent to NOT fix without user approval
```

---

## Template: System Review Agent

Para analizar ejecución vs plan:

```markdown
---
name: system-reviewer
description: Use after completing a feature to analyze execution against the original plan. Checks for plan adherence, divergences, and system improvements.
model: sonnet
tools: ["Read", "Glob", "Grep"]
---

You are a system reviewer that analyzes execution reports against implementation plans.

## Review Responsibilities

### 1. Plan Adherence
- Compare executed steps vs planned steps
- Identify skipped or added tasks
- Note order changes

### 2. Divergence Classification
- **Good divergence**: Improvements discovered during implementation
- **Bad divergence**: Scope creep, missed requirements, shortcuts

### 3. Root Cause Analysis
For each divergence:
- Why did it happen?
- Was it necessary?
- Could it have been predicted?

### 4. System Improvement Recommendations
- What should be updated in CLAUDE.md?
- New patterns to document?
- Commands to create?

## Output Format

**📊 Execution Summary**
- Plan completion: X/Y tasks (Z%)
- Good divergences: N
- Bad divergences: N

**✅ Completed As Planned**
- List of tasks executed as specified

**🔄 Divergences**
For each:
- Type: Good/Bad
- Description
- Root cause
- Recommendation

**🔧 System Improvements**
- CLAUDE.md updates needed
- New patterns identified
- Commands to create

**📋 Final Assessment**
- Overall: Successful / Partial / Needs review
- Key learnings
- Next steps
```

---

## Workflows Paralelos

### Ejemplo: Research Paralelo

Correr 5+ agentes simultáneamente explorando diferentes aspectos:

```
Main Agent: "Necesito entender el sistema de autenticación"
  ↓
Subagent 1: "Investigar routes de auth"
Subagent 2: "Investigar models de usuarios"
Subagent 3: "Investigar middleware de auth"
Subagent 4: "Investigar tests de auth"
Subagent 5: "Investigar documentación existente"
  ↓
Main Agent: Combina resultados de los 5
```

**Beneficio:** 5x más rápido que investigación secuencial.

### Ejemplo: Code Review Multi-archivo

```
Main Agent: "Revisar el PR completo"
  ↓
Subagent 1: "Revisar cambios en models/"
Subagent 2: "Revisar cambios en routes/"
Subagent 3: "Revisar cambios en tests/"
  ↓
Main Agent: Consolida reviews en reporte final
```

---

## Best Practices

### 1. Paraleliza Research

No uses subagents secuencialmente cuando puedes correr 5-10 simultáneamente.

### 2. Controla el Output Format

Este es tu lever principal para workflows confiables:
- Estructurado y parseable
- Incluye metadata (archivos revisados, líneas, severidad)
- Explícito sobre qué debe hacer el main agent después
- Fácil de combinar con otros agentes downstream

### 3. Incluye Metadata

- Archivos analizados
- Números de línea
- Niveles de severidad
- Hacen los resultados accionables

### 4. Testea los Handoffs

Verifica que lo que el main agent recibe coincide con lo esperado.

### 5. Haz Outputs Parseables

Estructura findings para que otros comandos/agentes puedan consumirlos.

---

## Meta Agents: Generadores de Agentes

Considera crear un "meta agent" - tu propia versión de `/agents` que genera nuevos subagents siguiendo TUS estándares y patrones.

**Beneficio:** Consistencia across todos tus subagents y codifica tus preferencias en el proceso de creación.

### Ejemplo de Meta Agent

```markdown
---
name: agent-generator
description: Use to create new subagents that follow project standards
model: sonnet
---

You create subagents following our project's patterns:

## Required Structure
- Frontmatter with name, description, model, tools
- Role definition section
- Context gathering section
- Step-by-step approach
- Structured output format
- Guidelines section

## Naming Conventions
- Kebab-case for filenames
- Descriptive names indicating purpose
- Examples in description field

## Output Standards
- Always structured markdown
- Include severity levels
- Parseable by other agents
- Explicit next-step instructions

When creating a new agent:
1. Ask what task it should perform
2. Ask what context it needs
3. Generate the agent file
4. Save to .claude/agents/[name].md
```

---

## El Problema del Context Handoff

### Por Qué el Output Format es Crítico

```
Sin control de output:
Subagent: "Encontré algunos problemas..."
Main Agent: "OK, ¿qué hago ahora?" (contexto perdido)

Con output estructurado:
Subagent:
  "Issues: 3 Critical, 2 Major
   Files: auth/routes.py:45, auth/service.py:23
   Action: DO NOT FIX without user approval"
Main Agent: Sabe exactamente qué reportar
```

### Checklist de Output Efectivo

- [ ] Metadata incluida (archivos, líneas, severidad)
- [ ] Estructura parseable (markdown con headers claros)
- [ ] Instrucciones para main agent explícitas
- [ ] Resumen ejecutivo al final
- [ ] Formato consistente entre invocaciones

---

## Próximos Pasos

Después de dominar subagents, puedes:

1. **Correr 10+ investigaciones paralelas** - Explorar aspectos diferentes simultáneamente
2. **Reviews especializados en paralelo** - Revisar codebase entero rápidamente
3. **Mantener contexto limpio** - Thread principal sin contaminar
4. **Construir agentes expertos reutilizables** - Para tareas recurrentes

**La combinación de subagents + slash commands + validation crea un sistema de AI coding poderoso y confiable.**
