# 🔄 El PIV Loop Workflow Completo

**El framework que diferencia al top 5% (88% code acceptance) del 90% (30% acceptance)**

---

## 🎯 ¿Qué es el PIV Loop?

**PIV Loop** es tu proceso sistemático para trabajar con AI coding assistants:

```
┌────────────────────────────────────────┐
│  P - PLAN                              │
│  Research + Vibe Planning + Structure  │
│  ↓                                     │
│  I - IMPLEMENT                         │
│  Execute step-by-step (no improvise)   │
│  ↓                                     │
│  V - VALIDATE                          │
│  5-level pyramid (automated checks)    │
│  ↓                                     │
│  → ITERATE                             │
│  Fix the SYSTEM, not just the bug      │
└────────────────────────────────────────┘
```

**Cambio de mentalidad:**
- ❌ OLD: "Pido código → reviso → debuggeo → repito"
- ✅ NEW: "Planifico → AI ejecuta → validation auto → mejoro sistema"

---

## 📋 P - PLAN

**Objetivo:** Crear un plan estructurado ANTES de escribir código

**Duración:** 15-30 min para features medianas, 60+ min para features complejas

---

### Las 3 Sub-Fases del Planning

#### 1. Research (5-15 min)

**Qué hacer:**
- Lee código existente relacionado
- Lee CLAUDE.md completo
- Lee reference guides relevantes
- Investiga documentación de librerías si necesitas nuevas

**Prompt para Claude Code:**
```
Voy a implementar: [feature description]

Primero ayúdame a hacer research:
1. ¿Qué archivos del codebase son relevantes?
2. ¿Qué patterns existentes debo seguir?
3. ¿Qué de nuestro CLAUDE.md aplica aquí?
4. [Si usa librería nueva] Research de [nombre librería]

NO implementes aún. Solo research.
```

**Output:** Contexto completo de lo que existe y cómo se hace

**Tiempo:** 5-15 min

---

#### 2. Vibe Planning (5-10 min)

**Qué hacer:**
- Brainstorm de arquitectura
- Considera diferentes approaches
- Identifica trade-offs
- Decide approach general

**Prompt para Claude Code:**
```
Basado en el research, ayúdame a planear approach:

Feature: [descripción]

Opciones que veo:
A. [Approach 1 - descripción]
B. [Approach 2 - descripción]

¿Cuál recomiendas y por qué?
Considera: simplicidad, maintainability, performance

NO implementes. Solo discusión de arquitectura.
```

**Output:** Decisión de approach con rationale

**Tiempo:** 5-10 min

---

#### 3. Structured Plan (10-15 min)

**Qué hacer:**
- Crear plan formal ejecutable
- Especificar archivos a modificar/crear
- Desglosar en steps específicos
- Incluir tests y validation

**Prompt para Claude Code:**
```
Crea un plan estructurado para:

Feature: [descripción]

Approach: [del vibe planning]

Usa este template:
---
# Plan: [Feature Name]

## Context References
IMPORTANT: AI MUST READ THESE BEFORE IMPLEMENTING
- File: path/to/file.py:line-range - Reason: [why relevant]
- Reference: guides/api-patterns.md - Reason: [why relevant]

## Implementation Steps

### 1. [Action] path/to/file.py
- IMPLEMENT: [specific detail]
- PATTERN: [Reference existing file:line if following pattern]
- VALIDATE: `command to run`

### 2. [Action] path/to/another_file.py
...

## Tests to Write
- Test: [description]
- Test: [description]

## Validation Commands
1. Type checking: `mypy app/`
2. Tests: `pytest -v`
3. Linting: `ruff check .`
---

Hazlo specific, no genérico.
```

**Output:** Plan markdown de ~100-300 líneas (más largo = probablemente scope creep)

**Tiempo:** 10-15 min

---

### Red Flags en Planning

🚨 **Plan sin file references**
- Malo: "Create user authentication"
- Bueno: "CREATE app/features/auth/routes.py following pattern from app/features/products/routes.py:15-40"

🚨 **Plan sin tests mencionados**
- Si plan no menciona tests → no está completo

🚨 **Plan muy largo (>500 líneas)**
- Indica scope creep o feature muy compleja
- Considera dividir en múltiples PIV Loops

🚨 **Plan sin validation commands**
- Plan debe especificar CÓMO validar cada paso

---

## 🔨 I - IMPLEMENT

**Objetivo:** Ejecutar el plan step-by-step sin improvisación

**Duración:** 20-60 min dependiendo de complejidad

---

### Proceso de Implementation

#### Paso 1: Lee el Plan Completo

**Prompt para Claude Code:**
```
Lee el plan completo en [path-to-plan.md]

Confirma que entiendes:
1. Todos los context references que debo leer
2. Todos los steps a ejecutar
3. Todos los tests a escribir
4. Todos los validation commands

NO implementes aún. Solo confirmación.
```

**Output:** AI confirma entendimiento completo

---

#### Paso 2: Lee TODO el Contexto

**Antes de escribir código:**
```
Ahora LEE todos los context references del plan:
- [Lista los archivos del plan]

Confirma que entiendes los patterns a seguir.
```

**Output:** AI lee y confirma patterns

**CRÍTICO:** No saltar este paso. Sin contexto completo, AI improvisa.

---

#### Paso 3: Ejecuta Step-by-Step

**Prompt para Claude Code:**
```
Ejecuta el plan step-by-step.

Para CADA step:
1. Implementa exactamente lo especificado
2. Sigue los patterns de los context references
3. NO dejes TODOs ni comentarios "implement this later"
4. Escribe el código + tests simultáneamente

Si encuentras algo que el plan no cubrió, DETENTE y pregunta.
NO improvises.
```

**Output:** Código completo, tests escritos, sin TODOs

---

#### Paso 4: Validation Preliminar

**Después de implementar CADA step:**
```
Ejecuta el validation command para este step:
[El comando del plan]

Reporta resultado.
```

**Output:** Validation passing o errores específicos

---

### Red Flags en Implementation

🚨 **AI sugiere en vez de implementar**
- "You could add a function here..." → ❌ NO
- Debería implementar directamente → ✅ SÍ

🚨 **AI deja TODOs**
```python
def process_data(data):
    # TODO: Add validation
    # TODO: Handle edge cases
    pass
```
→ ❌ Inaceptable. Implementation completa o no está done.

🚨 **AI no escribe tests**
- "Here's the code, you can add tests later" → ❌ NO
- Tests son PARTE de la implementation → ✅ SÍ

🚨 **AI se desvía del plan**
- Agrega features no especificadas
- Usa approaches diferentes
- "Mejoré el plan con..." → ❌ NO (a menos que sea bug del plan)

---

## ✅ V - VALIDATE

**Objetivo:** Verificar automáticamente que el código funciona

**Duración:** 3-10 min (automático)

---

### La Validation Pyramid de 5 Niveles

Cada nivel es un GATE. Si falla, NO avanzas.

```
        Level 5: Human Review
              (Alignment)
                  |
        Level 4: Integration Tests
              (System behavior)
                  |
        Level 3: Unit Tests
              (Logic correctness)
                  |
        Level 2: Type Safety
              (Type errors)
                  |
        Level 1: Syntax & Style
              (Format, linting)
```

---

#### Level 1: Syntax & Style (< 5 segundos)

**Tools:** ruff, black, prettier, eslint

**Qué detecta:**
- Format errors
- Style violations (PEP8, etc.)
- Import ordering
- Unused variables

**Commands:**
```bash
# Python
ruff check .
black --check .

# TypeScript
npm run lint
npm run format:check
```

**Si falla:** Fix automáticamente con formatters, re-run

---

#### Level 2: Type Safety (< 30 segundos)

**Tools:** mypy, pyright, tsc

**Qué detecta:**
- Type mismatches
- Null/undefined errors
- Missing type hints
- Invalid type usage

**Commands:**
```bash
# Python
mypy app/
pyright app/

# TypeScript
tsc --noEmit
```

**Si falla:** Agrega type hints, corrige types, re-run

---

#### Level 3: Unit Tests (< 1 minuto)

**Tools:** pytest, vitest, jest

**Qué detecta:**
- Logic errors
- Edge cases mal manejados
- Incorrect function behavior
- Missing error handling

**Commands:**
```bash
# Python
pytest tests/unit/ -v

# TypeScript
npm test -- --run
```

**Si falla:** Fix logic, agrega missing cases, re-run

**Common Pitfall:** AI que mockea tests para pasar
- ❌ `mock.return_value = "success"` → test siempre pasa
- ✅ Tests reales que verifican lógica

---

#### Level 4: Integration Tests (1-5 minutos)

**Tools:** pytest (integration), curl, playwright

**Qué detecta:**
- Component interaction issues
- API contract violations
- Database integration problems
- External service issues

**Commands:**
```bash
# API integration
pytest tests/integration/ -v

# Manual API test
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User"}'

# E2E tests
npm run test:e2e
```

**Si falla:** Fix integration issues, update API contracts, re-run

---

#### Level 5: Human Review (5-15 minutos)

**Tool:** TU

**Qué revisar:**
- ❓ ¿El código resuelve el problema original?
- ❓ ¿Sigue la arquitectura planeada?
- ❓ ¿Usa los patterns correctos del codebase?
- ❓ ¿Es maintainable (alguien más lo entiende)?
- ❓ ¿Hay algo que cambiarías?

**NO revisar:**
- ❌ Style (Level 1 ya cubrió)
- ❌ Types (Level 2 ya cubrió)
- ❌ Logic bugs (Level 3-4 ya cubrieron)

**Focus en:** Strategic alignment, architecture, maintainability

---

### Prompt para Validation Completa

```
Ejecuta la validation pyramid completa:

## Level 1: Syntax & Style
ruff check .
black --check .

## Level 2: Type Safety
mypy app/
pyright app/

## Level 3: Unit Tests
pytest tests/unit/ -v

## Level 4: Integration Tests
pytest tests/integration/ -v

Reporta resultados en formato:
✅/❌ Level 1: [resultado]
✅/❌ Level 2: [resultado]
✅/❌ Level 3: [resultado]
✅/❌ Level 4: [resultado]

Si ALGUNO falla, detente y reporta el error específico.
```

**Output:** Report de validation con status de cada nivel

---

### Red Flags en Validation

🚨 **Saltar levels**
- "Type checking dio error pero tests pasan, así que está bien" → ❌ NO
- CADA level debe pasar → ✅ SÍ

🚨 **Validation manual**
- "Probé en el browser y funciona" → ❌ NO como única validation
- Automated tests primero, manual después → ✅ SÍ

🚨 **Ignorar warnings**
- "Solo son warnings, no errores" → ❌ Peligroso
- Fix warnings también → ✅ SÍ

---

## 🔁 → ITERATE

**Objetivo:** Cuando falla, mejorar el SISTEMA para prevenir en futuro

**Duración:** Variable (5-30 min)

---

### El Loop de Mejora Continua

```
Validation falla
      ↓
Identifica la CAUSA ROOT
      ↓
Pregunta: ¿Qué del SISTEMA mejorar?
      ↓
Actualiza: CLAUDE.md | Command | Guide | Template
      ↓
Re-ejecuta PIV Loop
      ↓
Sistema ahora previene ese error
```

---

### Framework de Iteration

#### Paso 1: Analiza el Failure

**Preguntas:**
- ¿QUÉ falló exactamente?
- ¿En qué LEVEL de validation falló?
- ¿POR QUÉ falló (causa root)?

**Ejemplo:**
```
Failure: mypy error "missing type hint for parameter"
Level: 2 (Type Safety)
Causa: AI no agregó type hints en nueva función
```

---

#### Paso 2: Identifica el System Fix

**Pregunta: "¿Qué del sistema mejorar para prevenir esto?"**

**Opciones:**

| Failure Type | System Fix |
|--------------|------------|
| Type error | Agregar a CLAUDE.md: "ALL functions MUST have type hints" + example |
| Test no escrito | Agregar a plan-template: "Tests required before step marked complete" |
| Pattern no seguido | Crear reference guide: "API Endpoint Patterns" con examples |
| Validation no ejecutada | Agregar a /validate command: nuevo check |

---

#### Paso 3: Implementa el System Fix

**Prompt para Claude Code:**
```
El validation falló con: [error description]

Ayúdame a mejorar el SISTEMA:

1. ¿Qué agregar a CLAUDE.md para prevenir esto?
2. ¿Qué slash command necesitamos crear/mejorar?
3. ¿Qué reference guide crear?

Implementa el fix al sistema, NO solo al código.
```

**Output:** Sistema actualizado (CLAUDE.md, command, o guide)

---

#### Paso 4: Re-ejecuta PIV Loop

```
Sistema mejorado → Re-ejecuta desde PLAN (si es major) o desde VALIDATE (si es minor fix)

Verifica que ahora pasa validation.
```

---

### Ejemplos Reales de System Fixes

#### Ejemplo 1: Type Errors Frecuentes

**Failure:**
```
mypy error: missing type hint for 'process_data' parameter 'data'
```

**System Fix - Actualizar CLAUDE.md:**
```markdown
## Code Style

### Type Hints (NON-NEGOTIABLE)
ALL functions MUST have complete type hints:

❌ BAD:
```python
def process_data(data):
    return data.transform()
```

✅ GOOD:
```python
def process_data(data: pd.DataFrame) -> pd.DataFrame:
    return data.transform()
```

**Validation:** `mypy app/` must pass with zero errors.
```

**Resultado:** AI siempre agrega type hints en futuro.

---

#### Ejemplo 2: Tests Faltantes

**Failure:**
```
No tests found for new endpoint /api/v1/users
```

**System Fix - Actualizar plan-template.md:**
```markdown
### [ACTION] [file_path]
- IMPLEMENT: [detail]
- PATTERN: [reference]
- TESTS: [specific test cases to write]  ← AGREGADO
- VALIDATE: `pytest tests/test_[feature].py -v`  ← ESPECÍFICO
```

**Resultado:** Plans siempre incluyen tests específicos.

---

#### Ejemplo 3: Pattern Inconsistente

**Failure:**
```
New API endpoint doesn't follow logging pattern from other endpoints
```

**System Fix - Crear reference guide:**

`reference/api-endpoint-pattern.md`:
```markdown
# API Endpoint Pattern

ALL API endpoints MUST follow this pattern:

```python
from app.core.logging import get_logger

logger = get_logger(__name__)

@router.post("/api/v1/resource")
async def create_resource(data: ResourceCreate) -> ResourceResponse:
    logger.info("creating_resource", resource_type=data.type)
    try:
        result = await service.create(data)
        logger.info("resource_created", resource_id=result.id)
        return result
    except Exception as e:
        logger.error("resource_creation_failed", error=str(e))
        raise
```

See: app/features/products/routes.py:15-40
```

**System Fix - Actualizar CLAUDE.md:**
```markdown
## Common Patterns

When creating API endpoints:
→ See: reference/api-endpoint-pattern.md
→ Example: app/features/products/routes.py:15-40
```

**Resultado:** AI siempre sigue logging pattern.

---

### Red Flags en Iteration

🚨 **Solo fixear el bug**
- "Corregí el type hint en esa función" → ❌ Incompleto
- "Corregí + actualicé CLAUDE.md" → ✅ Completo

🚨 **No documentar la solución**
- Fix el código pero no agregar nada al sistema
- Mismo error aparecerá en próximo feature

🚨 **Scope creep en iteration**
- Usar el failure como excusa para refactor masivo
- Iteration debe ser focused: fix + system update

---

## 🎯 PIV Loop en Acción: Ejemplo Completo

### Feature: "Add user authentication endpoint"

---

#### 🔵 PLAN (20 min)

**1. Research (7 min):**
```
Prompt: "Voy a implementar user authentication endpoint.
Research: ¿Qué patterns de auth usamos? ¿Qué de CLAUDE.md aplica?"

Output: AI lee existing auth code, CLAUDE.md security section
```

**2. Vibe Planning (5 min):**
```
Prompt: "Opciones: JWT vs sessions vs API keys. ¿Qué recomiendas?"

Output: Decision - JWT porque proyecto es API-only
```

**3. Structured Plan (8 min):**
```
Prompt: "Crea plan estructurado para JWT authentication siguiendo template"

Output: Plan con steps, files, tests, validation
```

---

#### 🟢 IMPLEMENT (35 min)

**1. Lee Contexto (5 min):**
```
AI lee: app/core/security.py, app/models/user.py, CLAUDE.md
```

**2. Ejecuta Steps (25 min):**
- CREATE app/features/auth/routes.py
- CREATE app/features/auth/models.py
- UPDATE app/core/dependencies.py
- WRITE tests/test_auth.py

**3. Preliminary Validation (5 min):**
```
mypy app/features/auth/ → ✅
pytest tests/test_auth.py → ✅
```

---

#### 🟡 VALIDATE (8 min)

**Level 1: Syntax (30s):**
```bash
ruff check . → ✅
black --check . → ✅
```

**Level 2: Types (1 min):**
```bash
mypy app/ → ✅
pyright app/ → ✅
```

**Level 3: Unit Tests (2 min):**
```bash
pytest tests/test_auth.py -v → ✅ 8 tests passed
```

**Level 4: Integration (3 min):**
```bash
pytest tests/integration/test_auth_flow.py → ✅
curl POST /api/v1/auth/login → ✅ returns JWT
```

**Level 5: Human Review (2 min):**
- ✅ Sigue architecture
- ✅ Security best practices
- ✅ Matches plan

---

#### 🔴 ITERATE (0 min en este caso)

**Validation pasó completamente → No iteration needed.**

**Si hubiera fallado:**
```
Ejemplo: Type error → Update CLAUDE.md
Ejemplo: Test faltante → Update plan-template
```

---

**Total Time: 63 min para feature completa, tested, validated. ✅**

**Sin PIV Loop:** 2-3 horas con debugging manual, revisión, re-work.

**🚀 2-3x más rápido + higher quality.**

---

## 🎓 Best Practices del PIV Loop

### 1. SIEMPRE Planifica (incluso "quick fixes")

❌ **"Solo es un pequeño fix, no necesito plan"**

**Realidad:** "Pequeño fix" se convierte en:
- 3 archivos modificados
- 2 edge cases no considerados
- 1 feature rota
- 4 horas de debugging

✅ **SIEMPRE planifica. Takes 5-10 min, saves hours.**

---

### 2. Plans Específicos > Plans Genéricos

❌ **Plan genérico:**
```
1. Add authentication
2. Update database
3. Test
```

✅ **Plan específico:**
```
1. CREATE app/features/auth/routes.py
   - IMPLEMENT: POST /api/v1/auth/login endpoint
   - PATTERN: Follow app/features/products/routes.py:15-40 for logging
   - VALIDATE: `curl -X POST http://localhost:8000/api/v1/auth/login`

2. CREATE app/features/auth/models.py
   - IMPLEMENT: LoginRequest, LoginResponse, TokenPayload
   - PATTERN: Pydantic models like app/models/product.py:8-25
   - VALIDATE: `mypy app/features/auth/`
```

---

### 3. Implementation SIN Improvisación

**Reglas:**
- ✅ Si está en plan → implementa
- ❌ Si NO está en plan → DETENTE y pregunta
- ✅ Si encuentras issue en plan → reporta y ajusta plan
- ❌ NUNCA improvises "mejoras" no planeadas

**Por qué:** Improvisation = scope creep = features medio implementadas

---

### 4. Validation es GATE, no "Nice to Have"

**Cada level es un gate:**
- ❌ "Level 2 falló pero Level 3 pasó, entonces OK" → NO
- ✅ "Level 2 falló, fixeo y re-run" → SÍ

**No avanzas hasta que TODOS los levels pasen.**

---

### 5. Iterate en el Sistema, no Solo el Código

**Cada failure pregunta:**
- "¿Qué actualizar en CLAUDE.md?"
- "¿Qué command crear/mejorar?"
- "¿Qué reference guide agregar?"

**Resultado:** Sistema se fortalece con cada proyecto.

---

## 🚨 Errores Comunes

### 1. Saltar Directo a Código

**Error:** "Solo necesito agregar un campo a la DB"

**Realidad:**
- Campo requiere migration
- Migration rompe otros features
- Tests fallan
- 3 horas de rollback

**Fix:** SIEMPRE plan (toma 5 min, evita 3 horas).

---

### 2. Plans Vagos

**Error:**
```
Plan:
1. Add authentication
2. Test it
```

**Por qué es malo:**
- AI no sabe QUÉ tipo de auth
- AI no sabe QUÉ files modificar
- AI improvisa

**Fix:** Specific files, steps, patterns.

---

### 3. Implementation Parcial

**Error:** AI deja TODOs o comentarios "implement later"

**Por qué es malo:**
- "Implement later" nunca pasa
- Tests no cubren TODOs
- Validation da falso positivo

**Fix:** NO marcar step como done hasta que esté 100% completo.

---

### 4. Validation Manual Únicamente

**Error:** "Probé en el browser, funciona"

**Por qué es malo:**
- Lento
- Inconsistente
- No reproducible
- Olvidas edge cases

**Fix:** Automated validation pyramid primero, manual después.

---

### 5. Solo Fixear Bug, no el Sistema

**Error:** Corriges el type error pero no actualizas CLAUDE.md

**Por qué es malo:**
- Mismo error en próximo feature
- Sistema no mejora
- Knowledge no se captura

**Fix:** Cada bug → update sistema.

---

## 📊 Métricas de Éxito

**Cómo saber que tu PIV Loop funciona:**

### Week 1-2:
- [ ] Code acceptance 50-60%
- [ ] Planning toma 20-30 min
- [ ] Validation mostly manual
- [ ] 1-2 iterations por feature

### Month 1:
- [ ] Code acceptance 70-75%
- [ ] Planning toma 10-15 min (practice)
- [ ] Validation 80% automated
- [ ] 0-1 iterations por feature

### Month 3:
- [ ] Code acceptance 85%+
- [ ] Planning instintivo (<10 min)
- [ ] Validation 100% automated
- [ ] Rare iterations (sistema robusto)

### Month 6:
- [ ] Code acceptance 88%+ (top 5%)
- [ ] PIV Loop es segunda naturaleza
- [ ] Sistema reutilizable en nuevos proyectos
- [ ] Enseñando a otros

---

## 🎯 Next Steps

**Has aprendido el PIV Loop completo. Ahora:**

1. **Practica:** Ejecuta 3-5 PIV Loops en features reales
2. **Itera:** Mejora tu sistema con cada loop
3. **Documenta:** Captura patterns en CLAUDE.md y guides

**Recursos Relacionados:**
- `planning-phase.md` - Deep dive en Planning
- `implementation-phase.md` - Deep dive en Implementation
- `validation-pyramid.md` - Deep dive en Validation
- `iteration-strategies.md` - Deep dive en Iteration

---

**🚀 El PIV Loop es el diferenciador #1 entre developers promedio y top 5%.**

**Dominarlo = 88% code acceptance + velocidad 10x.**

**START NOW: Ejecuta tu próximo feature con PIV Loop.**
