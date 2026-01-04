# Slash Commands - Atajos de Productividad para AI Coding

**Tu biblioteca de comandos reutilizables que transforman el AI coding de caótico a sistemático**

---

## 🎯 ¿Qué son los Slash Commands?

Los slash commands son **atajos de productividad** - como "Ctrl+C" para la IA.

**Sin slash commands:**
```
Tú: "Claude, necesito que leas el CLAUDE.md, luego explores el código
     relacionado a autenticación, analices los patterns existentes,
     identifiques qué archivos modificar, crees un plan estructurado
     con context references, implementation steps, y validation commands..."

[50 líneas de prompt cada vez que planeas una feature]
```

**Con slash commands:**
```
Tú: /plan auth-feature

Claude: [Ejecuta automáticamente el prompt completo de 50 líneas]
        [Genera plan estructurado listo para /execute]
```

**Diferencia:** 1 comando vs. reescribir 50 líneas cada vez.

---

## 📂 Estructura de Slash Commands

Los slash commands son **archivos markdown** en `.claude/commands/`:

```
.claude/
└── commands/
    ├── prime.md            # Cargar contexto del proyecto
    ├── plan.md             # Crear plan de feature
    ├── execute.md          # Implementar según plan
    ├── validate.md         # Ejecutar validation pyramid
    ├── code-review.md      # Review automático
    └── commit.md           # Git commits automáticos
```

**Invocación:** `/nombre-del-archivo` (sin `.md`)

---

## 🏗️ Anatomía de un Slash Command

Todo slash command efectivo tiene **3 secciones:**

### 1. INPUT (Contexto)
**Qué información necesita la IA para ejecutar bien**

```markdown
## Context

Read these files before proceeding:
- CLAUDE.md
- existing code in src/auth/
- tests related to authentication
```

### 2. PROCESS (Pasos)
**Qué pasos seguir exactamente**

```markdown
## Steps

1. Research existing code
2. Identify patterns
3. Create structured plan
4. Include validation commands
```

### 3. OUTPUT (Formato)
**Qué formato de respuesta quieres**

```markdown
## Output Format

Generate a plan with:
- Context References (files to read)
- Implementation Steps (what to do)
- Validation Commands (how to verify)
```

**Sin esta estructura:** Respuestas genéricas, inconsistentes.
**Con esta estructura:** Output predecible, repetible, confiable.

---

## 🛠️ 4 Funcionalidades Clave

### 1. Argumentos ($1, $2, $ARGUMENTS)

**Permite comandos dinámicos:**

```markdown
# /plan-feature command

Create implementation plan for: $1

Feature description: $ARGUMENTS
```

**Uso:**
```
/plan-feature auth-system Add JWT authentication with refresh tokens
```

**Variables disponibles:**
- `$1`, `$2`, `$3`, ... - Argumentos individuales
- `$ARGUMENTS` - Todos los argumentos como string
- `$FILE` - Archivo actual (si existe)

---

### 2. Bash Execution (!)

**Ejecuta comandos y carga output al contexto:**

```markdown
# /prime command

Load project context:

!git status
!git log -5 --oneline
!find src/ -name "*.py" | head -20
```

**Qué hace:**
1. Ejecuta los 3 comandos bash
2. Carga el output al contexto de Claude
3. Claude puede ver los resultados para informar su respuesta

**Cuándo usarlo:**
- Cargar lista de archivos del proyecto
- Ver git status antes de commits
- Leer configuraciones (package.json, pyproject.toml)

---

### 3. File References (@)

**Carga contenido de archivos al contexto:**

```markdown
# /code-review command

Review these files:

@CLAUDE.md
@src/auth/login.py
@tests/test_auth.py
```

**Qué hace:**
- Lee el contenido completo de cada archivo
- Lo carga al contexto de Claude
- Claude puede analizar el código actual

**Diferencia vs. bash:**
- `!cat file.py` - Solo carga output del comando
- `@file.py` - Carga archivo optimizado para análisis de código

---

### 4. Frontmatter (YAML Metadata)

**Metadata del comando en la parte superior:**

```markdown
---
description: Create implementation plan for a feature
allowed-tools: [Read, Glob, Grep]
argument-hint: feature-name
---

# /plan command

[Rest of the command]
```

**Campos útiles:**
- `description` - Qué hace el comando (aparece en autocomplete)
- `allowed-tools` - Qué herramientas puede usar Claude
- `argument-hint` - Ayuda sobre argumentos esperados
- `model` - Qué modelo usar (haiku, sonnet, opus)

---

## 🎯 Los 4 Comandos Core

Estos 4 comandos forman el **workflow completo** del PIV Loop:

### 1. /prime - Context Loading

**Propósito:** Cargar TODO el contexto del proyecto antes de trabajar.

**Cuándo usarlo:**
- Al inicio de cada sesión
- Antes de planear features grandes
- Cuando necesitas "refrescar" el contexto de Claude

**Archivo:** `.claude/commands/prime.md`

```markdown
---
description: Load complete project context
allowed-tools: [Read, Glob, Bash]
---

# Context Loading

Load the following project context:

## 1. Project Rules
@CLAUDE.md

## 2. Project Structure
!find . -type f -name "*.py" -o -name "*.ts" | grep -v node_modules | grep -v __pycache__ | head -50

## 3. Git Status
!git status
!git log -5 --oneline

## 4. Dependencies
@pyproject.toml
@package.json

## Summary

Provide a brief summary of:
- Current project state
- Recent changes (from git log)
- Key files identified
```

**Output esperado:**
```
✅ Context loaded successfully

Project: [Name from CLAUDE.md]
Tech Stack: [From CLAUDE.md]
Recent changes: [From git log]
Key files: [List of main source files]

Ready to plan features.
```

---

### 2. /plan - Planning Phase

**Propósito:** Crear plan estructurado para una feature.

**Cuándo usarlo:**
- Antes de implementar cualquier feature
- Cuando necesitas research de código existente
- Para crear plans agent-to-agent (que /execute puede consumir)

**Archivo:** `.claude/commands/plan.md`

```markdown
---
description: Create implementation plan for feature
allowed-tools: [Read, Glob, Grep]
argument-hint: feature-name [description]
---

# Implementation Planning

Feature to plan: $1
Additional context: $ARGUMENTS

## Phase 1: Research

1. Read CLAUDE.md to understand:
   - Tech stack
   - Architecture patterns
   - Code style conventions
   - Common patterns

2. Explore existing code related to: $1
   - Use Glob to find relevant files
   - Use Grep to search for related code
   - Identify patterns to follow

3. Document findings:
   - What files exist
   - What patterns are used
   - What needs to change

## Phase 2: Vibe Planning

Brainstorm approaches:
- How should this integrate with existing code?
- What's the simplest solution? (KISS principle)
- What edge cases to consider?
- What could go wrong?

## Phase 3: Structured Plan

Create plan with this structure:

### CONTEXT REFERENCES
Files Claude MUST read before implementing:
- path/to/file.py:line_number (explain why)

### IMPLEMENTATION PLAN
High-level approach:
- Phase 1: [What]
- Phase 2: [What]

### STEP-BY-STEP TASKS

#### CREATE path/to/new_file.py
- Implement: [Specific details]
- Follow pattern from: existing_file.py:123
- Validate with: `command to run`

#### MODIFY path/to/existing_file.py
- Change: [Specific details]
- Location: Line 45-60
- Validate with: `command to run`

### VALIDATION COMMANDS
```bash
# Type checking
mypy src/

# Tests
pytest tests/test_feature.py -v

# Linting
ruff check src/
```

## Output

Save plan to: .agents/plans/$1-plan.md
```

**Output esperado:**
Plan guardado en `.agents/plans/feature-plan.md` que contiene:
- Context References (qué leer)
- Implementation Plan (qué hacer)
- Step-by-Step Tasks (cómo hacerlo)
- Validation Commands (cómo verificar)

---

### 3. /execute - Implementation Phase

**Propósito:** Implementar una feature siguiendo el plan.

**Cuándo usarlo:**
- Después de crear un plan con /plan
- Cuando ya tienes plan estructurado listo
- Para ejecución automática paso a paso

**Archivo:** `.claude/commands/execute.md`

```markdown
---
description: Execute implementation plan
allowed-tools: [Read, Write, Edit, Bash]
argument-hint: feature-name
---

# Execute Implementation Plan

Feature to implement: $1
Plan location: .agents/plans/$1-plan.md

## Phase 1: Read and Understand

1. Read the plan completely:
   @.agents/plans/$1-plan.md

2. Read all Context References listed in plan
   (The plan will specify which files to read)

3. Confirm understanding:
   - What is the goal?
   - What files will change?
   - What is the validation criteria?

## Phase 2: Execute Tasks in Order

For each task in the plan:

### a. Navigate to the task
Read current state of the file (if modifying existing file)

### b. Implement the task
- Follow the specific instructions in the plan
- Use patterns referenced in plan
- Write clean, documented code

### c. Verify as you go
Run the validation command for this task (if specified)

## Phase 3: Testing

Write tests WHILE implementing, not after:
- Unit tests for new functions
- Integration tests for new endpoints
- Follow testing patterns from CLAUDE.md

## Phase 4: Validation

Run ALL validation commands from the plan:
```bash
[Commands from plan's VALIDATION COMMANDS section]
```

## Phase 5: Final Verification

Confirm completion:
- [ ] All tasks from plan completed
- [ ] All validation commands passing
- [ ] No TODOs left in code
- [ ] Tests written and passing

## Output

Report results:
✅ Feature implemented successfully
✅ Validation commands passed
✅ Tests passing

OR

❌ Implementation incomplete
- Reason: [Why]
- Next steps: [What to do]
```

**Output esperado:**
- Código implementado
- Tests escritos
- Validation passing
- Reporte de completitud

---

### 4. /validate - Validation Phase

**Propósito:** Ejecutar validation pyramid completa.

**Cuándo usarlo:**
- Después de implementar código
- Antes de commits
- Para verificar estado del proyecto

**Archivo:** `.claude/commands/validate.md`

```markdown
---
description: Run complete validation pyramid
allowed-tools: [Bash]
---

# Validation Pyramid Execution

Run all 5 levels of validation:

## Level 1: Syntax & Style (<5s)

!ruff check .
!black --check .
!prettier --check frontend/src/

Expected: No errors

## Level 2: Type Safety (<30s)

!mypy src/ --strict
!tsc --noEmit

Expected: No type errors

## Level 3: Unit Tests (<1min)

!pytest -m unit --cov=src --cov-report=term-missing

Expected: All tests passing, coverage >80%

## Level 4: Integration Tests (1-5min)

!pytest -m integration -v

Expected: All integration tests passing

## Level 5: Human Review

Checklist:
- [ ] Strategic alignment (does this solve the right problem?)
- [ ] Security implications (any vulnerabilities?)
- [ ] Performance considerations (any bottlenecks?)
- [ ] Code quality (readable, maintainable?)

## Summary Report

Generate report:

```
🏛️ VALIDATION PYRAMID RESULTS

Level 1: Syntax & Style        [✅/❌]
Level 2: Type Safety           [✅/❌]
Level 3: Unit Tests            [✅/❌] (X/Y passing, Z% coverage)
Level 4: Integration Tests     [✅/❌] (X/Y passing)
Level 5: Human Review          [PENDING]

Overall Status: [PASS/FAIL]

[If FAIL, list specific issues found]
```

## Action Items

If validation fails:
1. Fix the failing level
2. Re-run validation from Level 1
3. Do NOT proceed until all levels pass

If validation passes:
- Ready for git commit
- Can proceed to next feature
```

**Output esperado:**
- Reporte de todos los niveles
- Status claro (PASS/FAIL)
- Action items si falla

---

## 🔗 Command Chaining

Los 4 comandos se pueden **encadenar** para workflow completo:

```bash
# Cargar contexto
/prime

# Planear feature
/plan auth-system Add JWT authentication

# Implementar plan
/execute auth-system

# Validar resultado
/validate

# Si todo pasa, commit
/commit "Add JWT authentication system"
```

**Flujo completo:** 5 comandos, workflow sistemático, cero ambigüedad.

---

## 📚 Otros Comandos Útiles

### /code-review - Code Review Automation

```markdown
---
description: Automated code review of recent changes
allowed-tools: [Bash, Read]
---

# Automated Code Review

## Analyze Recent Changes

!git status
!git diff HEAD

## Read Changed Files

[For each file in git diff, read it completely]

## Review Criteria

1. **Logic Errors**
   - Are there obvious bugs?
   - Are edge cases handled?

2. **Security Issues**
   - SQL injection risks?
   - XSS vulnerabilities?
   - Sensitive data exposure?

3. **Performance**
   - N+1 queries?
   - Inefficient algorithms?

4. **Code Quality**
   - Readable?
   - Well-documented?
   - Follows CLAUDE.md patterns?

5. **Adherence to Standards**
   - Follows code style from CLAUDE.md?
   - Tests included?
   - Type hints present?

## Output

Generate review report in `.agents/code-reviews/[date]-review.md`:

```markdown
# Code Review - [Date]

## Summary
[1-2 sentence summary]

## Issues Found

### 🔴 Critical
- [Issue]: [Description]
  - File: path/to/file.py:line
  - Fix: [Suggestion]

### 🟡 Warnings
- [Issue]: [Description]

### 🟢 Suggestions
- [Improvement]: [Description]

## Approval Status
[✅ APPROVED / ⚠️ APPROVED WITH COMMENTS / ❌ CHANGES REQUIRED]
```
```

---

### /commit - Git Commits Automation

```markdown
---
description: Create conventional commit with AI assistance
allowed-tools: [Bash]
---

# Git Commit Automation

## Analyze Changes

!git status
!git diff --staged

## Generate Commit Message

Based on changes, create conventional commit message:

Format:
```
type(scope): subject

body

footer
```

Types: feat, fix, docs, style, refactor, test, chore

Example:
```
feat(auth): add JWT authentication system

- Implement JWT token generation and validation
- Add refresh token support
- Include password hashing with bcrypt

Closes #123
```

## Execute Commit

!git commit -m "[Generated message]"

## Confirmation

✅ Committed: [hash] - [subject]
```

---

## 🎨 Best Practices

### 1. Nombres Descriptivos

❌ **Malo:** `/do.md`, `/thing.md`, `/work.md`
✅ **Bueno:** `/plan-feature.md`, `/validate-code.md`, `/review-pr.md`

**Por qué:** Autocomplete es más útil con nombres claros.

---

### 2. Documentación en Frontmatter

```markdown
---
description: Clear description of what this command does
argument-hint: Expected arguments format
---
```

**Por qué:** Aparece en autocomplete, ayuda a recordar cómo usar el comando.

---

### 3. Output Estructurado

❌ **Malo:**
```markdown
Respond with your analysis.
```

✅ **Bueno:**
```markdown
Generate report in this format:

## Summary
[1-2 lines]

## Details
- Item 1
- Item 2

## Status
[PASS/FAIL]
```

**Por qué:** Output predecible es reutilizable por otros comandos (agent-to-agent).

---

### 4. Validation Built-in

**Cada comando debe verificar su propio éxito:**

```markdown
## Validation

Confirm:
- [ ] Plan created at .agents/plans/[name]-plan.md
- [ ] All context references documented
- [ ] Validation commands specified
```

**Por qué:** Self-documenting, fácil de debug.

---

## 🚨 Errores Comunes

### 1. Comandos Muy Genéricos

❌ **Problema:**
```markdown
# /help command

Help me with whatever I need.
```

**Por qué falla:** Sin INPUT/PROCESS/OUTPUT específicos, respuestas inconsistentes.

✅ **Solución:** Comandos específicos para tareas específicas.

---

### 2. No Usar Agent-to-Agent

❌ **Problema:**
```markdown
# /plan command

Create a plan and explain it to the user.
```

**Por qué falla:** Output para humanos, no reutilizable por /execute.

✅ **Solución:**
```markdown
# /plan command

Create structured plan and save to .agents/plans/[name]-plan.md

Format:
- Context References (file paths)
- Implementation Steps (explicit commands)
- Validation Commands (bash commands)
```

**Por qué funciona:** /execute puede LEER el plan y ejecutarlo sin ver la conversación.

---

### 3. Olvidar Argumentos

❌ **Problema:**
```markdown
# /plan command

Plan the feature.
```

**Usuario:** `/plan auth-system`
**Claude:** "What feature do you want to plan?"

**Por qué falla:** No usa $1 o $ARGUMENTS.

✅ **Solución:**
```markdown
# /plan command

Feature to plan: $1
Description: $ARGUMENTS

[Rest of command uses $1 throughout]
```

---

## 📖 Cómo Crear Tu Primer Comando

**Paso a paso:**

### 1. Identifica Prompt Repetitivo

¿Qué prompt escribes 3+ veces?

Ejemplo: "Lee el CLAUDE.md, luego el código en src/auth/, y crea un plan para..."

### 2. Crea el Archivo

```bash
mkdir -p .claude/commands
touch .claude/commands/plan-auth.md
```

### 3. Estructura INPUT → PROCESS → OUTPUT

```markdown
---
description: Plan authentication features
---

# INPUT
Read these files:
@CLAUDE.md
@src/auth/

# PROCESS
1. Analyze existing auth code
2. Identify patterns
3. Create structured plan

# OUTPUT
Save plan to .agents/plans/auth-plan.md
```

### 4. Prueba

```
/plan-auth
```

### 5. Itera

Mejora basado en resultados:
- ¿Output correcto?
- ¿Faltó contexto?
- ¿Muy genérico?

---

## 🎯 Checklist de Comando Efectivo

Antes de considerar tu comando "done":

- [ ] Nombre descriptivo
- [ ] Frontmatter con description
- [ ] INPUT claro (qué contexto cargar)
- [ ] PROCESS específico (qué pasos)
- [ ] OUTPUT estructurado (formato exacto)
- [ ] Usa argumentos si aplica ($1, $ARGUMENTS)
- [ ] Validation built-in
- [ ] Tested con caso real

---

## 📚 Recursos

**Archivos relacionados del Playbook:**
- `plan-templates.md` - Estructura de planes
- `planning-prompts.md` - Prompts reutilizables
- `feature-breakdown.md` - Cómo descomponer features
- `../templates/validate-command.md` - Template de /validate
- `../templates/code-review.md` - Template de /code-review

**Ejemplos reales:**
- `.claude/commands/start-project.md` - PM conversacional
- Repositorio Context Engineering Hub (tiene 52+ comandos)

---

**🎯 Remember: Los slash commands transforman prompts repetitivos en workflows sistemáticos.**

**Empieza con los 4 core (/prime, /plan, /execute, /validate) y expande según necesites.**

**Cada comando es una inversión: 1 hora crear, miles de horas ahorradas. 🚀**
