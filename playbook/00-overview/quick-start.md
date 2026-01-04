# ⚡ Quick Start - Tu Primer PIV Loop en 15 Minutos

**Para desarrolladores que quieren empezar YA**

---

## 🎯 Qué Vas a Lograr

En los próximos 15 minutos vas a:

1. ✅ Crear tu primer CLAUDE.md (5 min)
2. ✅ Ejecutar un PIV Loop completo (10 min)
3. ✅ Experimentar el poder del sistema

**Después de esto, entenderás por qué el top 5% trabaja así.**

---

## ⏱️ Paso 1: Crea tu CLAUDE.md (5 minutos)

### Opción A: Usar Template (Recomendado)

1. Copia el template:
```bash
cp templates/CLAUDE.md.template ./CLAUDE.md
```

2. Edita las secciones básicas:

```markdown
# Project Rules

## Tech Stack
- Frontend: [TypeScript, React, Vite]
- Backend: [Python, FastAPI]
- Database: [PostgreSQL]

## Architecture
- Pattern: [Vertical Slice Architecture]

## Core Principles
1. TYPE SAFETY IS NON-NEGOTIABLE
2. KISS (Keep It Simple, Stupid)
3. YAGNI (You Aren't Gonna Need It)
```

3. Guarda el archivo en la raíz de tu proyecto.

**¡Listo!** Ya tienes tu primera capa de contexto automático.

---

### Opción B: Crear desde Cero (Si tienes 10 min extra)

Usa este prompt con Claude Code:

```
Ayúdame a crear un CLAUDE.md para mi proyecto.

Proyecto: [Descripción breve - ej: "SaaS de gestión de inventario"]

Tech Stack:
- Frontend: [tus tecnologías]
- Backend: [tus tecnologías]

Usa las 6 secciones esenciales:
1. Core Principles
2. Tech Stack
3. Architecture
4. Code Style
5. Testing
6. Common Patterns

Hazlo conciso (<150 líneas) para empezar.
```

---

## ⏱️ Paso 2: Tu Primer PIV Loop (10 minutos)

Vamos a implementar una feature simple para experimentar el proceso.

### 🔍 Feature de Ejemplo: "Health Check Endpoint"

Un endpoint `/health` que retorne el status de tu API.

---

### 📋 P - PLAN (3 minutos)

**Prompt para Claude Code:**

```
Lee nuestro CLAUDE.md y planifica:

Feature: Health check endpoint

Requirements:
- GET /health que retorne: {"status": "ok", "version": "1.0.0"}
- Include timestamp en la respuesta
- Escribe tests

Sigue nuestro CLAUDE.md para architecture y testing patterns.
```

**Output esperado:** Plan estructurado con:
- Archivos a crear/modificar
- Steps específicos
- Tests a escribir
- Validation commands

**Tiempo:** ~3 minutos

---

### 🔨 I - IMPLEMENT (4 minutos)

**Prompt para Claude Code:**

```
Implementa el plan que acabas de crear.

Ejecuta TODOS los steps, escribe el código Y los tests.
NO dejes TODOs.
```

**Output esperado:**
- Código del endpoint implementado
- Tests escritos
- Ready para validation

**Tiempo:** ~4 minutos

---

### ✅ V - VALIDATE (3 minutos)

**Prompt para Claude Code:**

```
Ejecuta validation:

1. Type checking: mypy app/ (o tsc para TypeScript)
2. Tests: pytest -v
3. Reporta resultados
```

**Output esperado:**
- ✅ Type checking passed
- ✅ Tests passed (X tests en Y seconds)
- ✅ Ready for merge

**Tiempo:** ~3 minutos

---

### 🔁 → ITERATE (si algo falla)

**Si validation falla:**

```
La validation falló en: [describe el error]

1. Fixea el issue
2. Identifica qué del CLAUDE.md agregar para prevenir esto en futuro
3. Re-ejecuta validation
```

---

## 🎉 ¡Completaste tu Primer PIV Loop!

### Lo Que Acabas de Experimentar

**Sin sistema (método tradicional):**
1. Pides código al AI
2. Copias/pegas
3. Pruebas manualmente
4. Debuggeas errores
5. Repites 3-4 veces
⏱️ **Tiempo:** 20-30 minutos

**Con sistema (PIV Loop):**
1. Plan estructurado (AI conoce tus reglas automáticamente)
2. Implementation directa (sin improvisación)
3. Validation automática (no pruebas manuales)
4. Done ✅
⏱️ **Tiempo:** 10 minutos

**🚀 2-3x más rápido. Y eso es solo el INICIO.**

---

## 📊 Qué Acabas de Aprender

### 1. CLAUDE.md = Contexto Automático

**Antes:**
```
Prompt: "Crea un endpoint"
AI: *código genérico*
Tú: "No, usa FastAPI"
AI: *ajusta*
Tú: "No, sigue nuestro pattern de..."
AI: *más ajustes*
```

**Ahora:**
```
Prompt: "Crea un endpoint"
AI: *lee CLAUDE.md automáticamente*
    *genera código siguiendo TUS reglas*
    ✅ Primera iteración perfecta
```

---

### 2. PIV Loop = Proceso Repetible

No más "vibe-based coding". Ahora tienes un PROCESO:

- **P**: Siempre planifica antes de código
- **I**: Siempre ejecuta el plan completo
- **V**: Siempre valida automáticamente
- **→**: Siempre mejora el sistema si falla

**Resultado:** Misma calidad cada vez, sin depender de "estar inspirado".

---

### 3. Validation Automática = Confianza

No más "espero que funcione".

Ahora tienes CERTEZA:
- ✅ Types correctos (mypy/tsc)
- ✅ Tests passing (pytest/vitest)
- ✅ Code quality (linting)

**Si pasa validation → puedes hacer commit con confianza.**

---

## 🎯 Próximos Pasos

### Nivel 1: Básico (Ya lo Completaste ✅)
- [x] Crear CLAUDE.md
- [x] Ejecutar primer PIV Loop
- [x] Validation básica

**¿Qué sigue?**

---

### Nivel 2: Intermedio (1-2 horas)

**Expande tu CLAUDE.md:**

Lee: `02-planning/claude-md-creation.md`

Agrega a tu CLAUDE.md:
- Architecture patterns detallados
- Code style específico de tu stack
- Testing patterns
- Common patterns de tu proyecto

**Crea tus primeros slash commands:**

Lee: `03-roadmap/slash-commands.md`

Comandos esenciales:
- `/plan` - Planning automático
- `/validate` - Validation completa
- `/code-review` - Review automático

**Tiempo:** ~2 horas
**ROI:** Los usarás MILES de veces

---

### Nivel 3: Avanzado (4-6 horas)

**Configura validation pyramid completa:**

Lee: `04-implementation/validation-pyramid.md`

Implementa los 5 niveles:
1. Syntax & Style (ruff/black/prettier)
2. Type Safety (mypy/pyright/tsc)
3. Unit Tests (pytest/vitest)
4. Integration Tests (API tests)
5. Human Review (strategic alignment)

**Crea reference guides:**

Lee: `02-planning/reference-guides.md`

Documenta:
- API patterns de tu proyecto
- Frontend component patterns
- Database patterns
- Common workflows

**Tiempo:** ~4-6 horas
**ROI:** Velocidad 5-10x en proyectos complejos

---

### Nivel 4: Expert (Proyecto Real)

**Aplica en un proyecto completo:**

Lee: `01-discovery/prd-creation.md`

1. Crea PRD de tu proyecto
2. Configura architecture completa
3. Ejecuta múltiples PIV Loops
4. Itera y mejora tu sistema

**Lee los ejemplos reales:**
- `examples/veterinaria-saas/` - Sistema multi-tenant
- `examples/agencia-empleados/` - Sistema que escala a millones

**Tiempo:** Proyecto completo
**ROI:** Sistema reutilizable para TODOS tus futuros proyectos

---

## 💡 Tips para Maximizar Resultados

### 1. Empieza Simple, Itera

❌ **No hagas:**
- CLAUDE.md de 500 líneas en primer intento
- 20 slash commands el primer día
- Validation pyramid completa inmediatamente

✅ **Mejor:**
- CLAUDE.md básico (50-100 líneas) → expande según necesites
- 2-3 slash commands esenciales → agrega más según uses
- Validation nivel 1-2 → agrega niveles gradualmente

---

### 2. Documenta Patterns que Repites

**Cada vez que haces algo 2+ veces:**

- ¿Es un pattern repetible? → Agrégalo a CLAUDE.md
- ¿Es un prompt repetido? → Créalo como slash command
- ¿Es un workflow multi-step? → Documéntalo en reference guide

**Resultado:** Tu sistema se vuelve más poderoso con el tiempo.

---

### 3. "Fix the System" > "Fix the Bug"

**Cuando algo falla, pregunta:**

- ❌ "¿Cómo fixeo este bug?"
- ✅ "¿Qué del sistema mejorar para prevenir esto?"

**Ejemplos:**

| Bug | System Fix |
|-----|------------|
| Type error | Agregar "Type checking is non-negotiable" a CLAUDE.md |
| API sin tests | Agregar test template a reference guide |
| Código duplicado | Agregar DRY principle a CLAUDE.md con examples |

---

### 4. Usa los Templates

No reinventes la rueda:

```
templates/
├── CLAUDE.md.template          ← Usa esto
├── prd-template.md             ← Y esto
├── plan-template.md            ← Y esto
├── validate-command.md         ← Y esto
└── docker-compose.yml          ← Y esto
```

**Customiza según necesites, pero empieza con los templates.**

---

## 🚨 Errores Comunes a Evitar

### 1. Saltar Directo a Código

❌ **"Solo necesito este pequeño fix, no necesito planificar"**

**Por qué es malo:**
- "Pequeño fix" se vuelve refactor de 3 archivos
- No consideraste edge cases
- Rompes algo que ya funcionaba

✅ **Siempre planifica, incluso "pequeños" fixes.**

---

### 2. Validation Manual

❌ **"Voy a probar manualmente en el browser"**

**Por qué es malo:**
- Lento (5-10 min cada vez)
- Inconsistente (olvidas casos)
- No repetible (otros no pueden replicar)

✅ **Automatiza validation, ejecuta con un comando.**

---

### 3. No Iterar el Sistema

❌ **"Ya fixeé el bug, siguiente task"**

**Por qué es malo:**
- Mismo bug aparecerá en futuro
- No aprendes del error
- Sistema no mejora

✅ **Cada bug → pregunta "¿qué del sistema mejorar?"**

---

## 📚 Recursos de Apoyo

### Para Seguir Aprendiendo

**Si tienes 30 minutos:**
- Lee: `00-overview/philosophy.md` - Entiende el "por qué"

**Si tienes 1 hora:**
- Lee: `04-implementation/piv-loop-workflow.md` - PIV Loop completo

**Si tienes 2 horas:**
- Lee: `02-planning/claude-md-creation.md` - CLAUDE.md avanzado
- Lee: `04-implementation/validation-pyramid.md` - Validation completa

**Si tienes un día:**
- Lee TODO el playbook de inicio a fin
- Implementa sistema completo en un proyecto real

---

### Templates Útiles

```bash
# Copia templates a tu proyecto
cp templates/CLAUDE.md.template ./CLAUDE.md
cp templates/prd-template.md ./PRD.md
cp templates/docker-compose.yml ./docker-compose.yml

# Crea estructura de slash commands
mkdir -p .claude/commands
cp templates/validate-command.md .claude/commands/validate.md
```

---

## ✅ Checklist de Progreso

Marca lo que ya completaste:

### Quick Start Básico
- [ ] CLAUDE.md creado con al menos 3 secciones
- [ ] Primer PIV Loop ejecutado (cualquier feature)
- [ ] Validation automática funcionando (al menos type checking + tests)

### Siguiente Nivel
- [ ] CLAUDE.md con 6 secciones completas
- [ ] 3+ slash commands creados
- [ ] Validation pyramid con 4+ niveles
- [ ] Reference guide creado (al menos 1)

### Expert
- [ ] Sistema usado en proyecto real completo
- [ ] 10+ PIV Loops ejecutados
- [ ] Code acceptance >70%
- [ ] Sistema documentado para reutilizar

---

## 🎬 Acción Inmediata

**Ahora mismo, abre Claude Code y ejecuta:**

```
Crea un CLAUDE.md básico para mi proyecto.

Proyecto: [describe en 1-2 líneas]

Tech Stack:
- [lista tus tecnologías]

Usa las 6 secciones esenciales. Hazlo conciso (<150 líneas).
```

**Luego ejecuta tu primer PIV Loop con una feature simple.**

---

## 💬 Próximos Pasos

Después de completar este Quick Start:

1. **Lee la filosofía completa:** `00-overview/philosophy.md`
2. **Profundiza en PIV Loop:** `04-implementation/piv-loop-workflow.md`
3. **Expande tu CLAUDE.md:** `02-planning/claude-md-creation.md`

---

**🚀 Welcome to systematic AI coding. Nunca volverás al "vibe-based coding".**

**START NOW → Crea tu CLAUDE.md y ejecuta tu primer PIV Loop.**
