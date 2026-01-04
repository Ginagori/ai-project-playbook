# 🎯 Planning Prompts - Biblioteca de Prompts Reutilizables

**Prompts copy-paste optimizados para la fase de Planning del PIV Loop**

---

## 🎨 ¿Por Qué Necesitas Esta Biblioteca?

### El Problema

Cada vez que planeas una feature, escribes prompts desde cero:
- "Ayúdame a planificar un endpoint de..."
- "Necesito crear un componente que..."
- "Quiero agregar una funcionalidad de..."

**Resultado:**
- 10-15 minutos escribiendo el prompt
- Prompts inconsistentes entre features
- Olvidas pedir context loading
- Planes incompletos (sin tests, sin validation)

---

### La Solución

**Biblioteca de prompts reutilizables:**
- Copy-paste en 30 segundos
- Estructura consistente (CONTEXT → PLAN → TASKS → VALIDATION)
- Siempre incluye tests y validation
- Customizables con variables simples

**Impacto:**
- ⏱️ **Ahorro de tiempo:** 10 min → 30 seg por planning
- 📊 **Calidad consistente:** Todos los planes tienen la misma estructura
- ✅ **Completitud garantizada:** Nunca olvidas tests o validation

---

## 📚 Prompts por Categoría

### CATEGORÍA 1: Backend - API Endpoints

#### Prompt 1.1: New GET Endpoint

```markdown
Planifica un nuevo endpoint GET siguiendo el template de ai-project-playbook/03-roadmap/plan-templates.md

**CONTEXT TO LOAD:**
- Read: CLAUDE.md (project standards)
- Read: app/api/[similar_endpoint].py (existing pattern to follow)
- Read: app/models/[related_model].py (model structure)

**ENDPOINT DETAILS:**
- Path: GET /api/v1/[RESOURCE]/[ACTION]
- Query params: [PARAM1]: type, [PARAM2]: type
- Response: List[[RESPONSE_MODEL]] | [RESPONSE_MODEL]

**BUSINESS LOGIC:**
[Describe what this endpoint does - be specific]

**EDGE CASES TO HANDLE:**
- Empty results
- Invalid query params
- [Add specific edge cases]

**OUTPUT:**
Create structured plan with:
1. CONTEXT REFERENCES (files to read)
2. IMPLEMENTATION PLAN (what to build)
3. STEP-BY-STEP TASKS (models → service → endpoint → tests)
4. VALIDATION COMMANDS (mypy + pytest + curl)

Save plan to: plans/[feature-name].md
```

**Ejemplo de uso:**
```markdown
Planifica un nuevo endpoint GET siguiendo el template de ai-project-playbook/03-roadmap/plan-templates.md

**CONTEXT TO LOAD:**
- Read: CLAUDE.md
- Read: app/api/products.py (existing pattern to follow)
- Read: app/models/product.py (model structure)

**ENDPOINT DETAILS:**
- Path: GET /api/v1/products/search
- Query params: query: str, category: str | None, min_price: float | None
- Response: List[ProductResponse]

**BUSINESS LOGIC:**
Search products by name/description, optionally filter by category and minimum price.
Use case-insensitive search, return results sorted by relevance.

**EDGE CASES TO HANDLE:**
- Empty results (return empty list)
- Invalid category (return 400)
- Negative min_price (return 400)

**OUTPUT:**
Create structured plan with:
1. CONTEXT REFERENCES
2. IMPLEMENTATION PLAN
3. STEP-BY-STEP TASKS
4. VALIDATION COMMANDS

Save plan to: plans/product-search.md
```

---

#### Prompt 1.2: New POST Endpoint

```markdown
Planifica un nuevo endpoint POST siguiendo el template de ai-project-playbook/03-roadmap/plan-templates.md

**CONTEXT TO LOAD:**
- Read: CLAUDE.md (project standards)
- Read: app/api/[similar_endpoint].py (existing POST pattern)
- Read: app/models/[related_model].py (model structure)

**ENDPOINT DETAILS:**
- Path: POST /api/v1/[RESOURCE]
- Request body: [REQUEST_MODEL] (fields: [FIELD1]: type, [FIELD2]: type)
- Response: [RESPONSE_MODEL] (status 201)

**BUSINESS LOGIC:**
[Describe what happens when this endpoint is called]

**VALIDATION RULES:**
- [FIELD1]: [validation rules]
- [FIELD2]: [validation rules]

**SIDE EFFECTS:**
- Database: [what gets created/updated]
- External APIs: [if any]
- Events: [if any events triggered]

**OUTPUT:**
Create structured plan with:
1. CONTEXT REFERENCES
2. IMPLEMENTATION PLAN (include request/response models)
3. STEP-BY-STEP TASKS (models → validation → service → endpoint → tests)
4. VALIDATION COMMANDS (mypy + pytest + curl POST)

Save plan to: plans/[feature-name].md
```

---

#### Prompt 1.3: New PUT/PATCH Endpoint

```markdown
Planifica un endpoint PUT/PATCH siguiendo el template de ai-project-playbook/03-roadmap/plan-templates.md

**CONTEXT TO LOAD:**
- Read: CLAUDE.md
- Read: app/api/[similar_endpoint].py (existing update pattern)
- Read: app/models/[model].py (current model)

**ENDPOINT DETAILS:**
- Path: [PUT/PATCH] /api/v1/[RESOURCE]/{id}
- Request body: [UPDATE_MODEL] (fields that can be updated)
- Response: [RESPONSE_MODEL] (status 200)

**UPDATE RULES:**
- Fields that CAN be updated: [FIELD1, FIELD2, ...]
- Fields that CANNOT be updated: [FIELD3, FIELD4, ...] (immutable)
- Partial updates allowed: [Yes/No]

**BUSINESS LOGIC:**
[What happens on update]

**EDGE CASES:**
- Resource not found (404)
- Concurrent updates (optimistic locking?)
- Validation failures (400)

**OUTPUT:**
Create structured plan with CONTEXT → PLAN → TASKS → VALIDATION
Save to: plans/[feature-name].md
```

---

#### Prompt 1.4: New DELETE Endpoint

```markdown
Planifica un endpoint DELETE siguiendo el template de ai-project-playbook/03-roadmap/plan-templates.md

**CONTEXT TO LOAD:**
- Read: CLAUDE.md
- Read: app/api/[similar_endpoint].py (existing delete pattern)

**ENDPOINT DETAILS:**
- Path: DELETE /api/v1/[RESOURCE]/{id}
- Response: 204 No Content (success) | 404 (not found)

**DELETE STRATEGY:**
- [Hard delete / Soft delete (set deleted_at)]
- Cascade deletes: [What related data gets deleted?]
- Restore possible: [Yes/No]

**SIDE EFFECTS:**
- Database: [what gets deleted]
- Cleanup: [files, cache, etc.]

**EDGE CASES:**
- Resource not found (404)
- Resource in use (409 conflict?)
- Insufficient permissions (403)

**OUTPUT:**
Create structured plan with CONTEXT → PLAN → TASKS → VALIDATION
Save to: plans/[feature-name].md
```

---

### CATEGORÍA 2: Frontend - React Components

#### Prompt 2.1: New UI Component

```markdown
Planifica un nuevo componente React siguiendo el template de ai-project-playbook/03-roadmap/plan-templates.md

**CONTEXT TO LOAD:**
- Read: CLAUDE.md (component patterns)
- Read: src/components/[SimilarComponent].tsx (existing component pattern)
- Read: src/lib/api-client.ts (API calling pattern)

**COMPONENT DETAILS:**
- Name: [ComponentName]
- Purpose: [What it displays/does]
- Props:
  - [prop1]: type (description)
  - [prop2]: type (description)
- State:
  - [state1]: type (description)

**API INTEGRATION:**
- Endpoint(s) used: [GET/POST /api/v1/...]
- Data fetching: [On mount / On user action / Real-time]
- Error handling: [How to display errors]
- Loading states: [Skeleton / Spinner / etc.]

**UI STRUCTURE:**
[Brief description or ASCII mockup]

**OUTPUT:**
Create structured plan with:
1. CONTEXT REFERENCES
2. IMPLEMENTATION PLAN
3. STEP-BY-STEP TASKS (component → tests → integration)
4. VALIDATION COMMANDS (typecheck + test + build)

Save to: plans/[component-name].md
```

**Ejemplo:**
```markdown
Planifica un nuevo componente React siguiendo el template

**CONTEXT TO LOAD:**
- Read: CLAUDE.md
- Read: src/components/ProductCard.tsx (existing card pattern)
- Read: src/lib/api-client.ts

**COMPONENT DETAILS:**
- Name: UserProfileCard
- Purpose: Display user profile with avatar, name, email, edit button
- Props:
  - userId: string
  - onEdit?: () => void
- State:
  - user: User | null
  - loading: boolean
  - error: string | null

**API INTEGRATION:**
- Endpoint: GET /api/v1/users/{userId}
- Data fetching: On mount
- Error handling: Display error message in card
- Loading states: Skeleton loader

**UI STRUCTURE:**
- Avatar (circular, 64x64)
- Name (h2)
- Email (p, muted)
- Edit button (if onEdit provided)

**OUTPUT:**
Create plan and save to: plans/user-profile-card.md
```

---

#### Prompt 2.2: New Page/Route

```markdown
Planifica una nueva página/ruta siguiendo el template de ai-project-playbook/03-roadmap/plan-templates.md

**CONTEXT TO LOAD:**
- Read: CLAUDE.md
- Read: src/App.tsx (routing setup)
- Read: src/pages/[SimilarPage].tsx (page structure pattern)

**PAGE DETAILS:**
- Route: /[route-path]
- Purpose: [What this page does]
- Components used: [List of components to compose]
- Data sources: [APIs, local state, URL params]

**LAYOUT:**
[Description of page sections]

**ROUTING:**
- Protected route: [Yes/No - requires auth]
- URL params: [param1, param2] (if any)
- Query params: [param1, param2] (if any)

**SEO:**
- Page title: [Title]
- Meta description: [Description]

**OUTPUT:**
Create structured plan with CONTEXT → PLAN → TASKS → VALIDATION
Save to: plans/[page-name].md
```

---

### CATEGORÍA 3: Database & Models

#### Prompt 3.1: New Database Model

```markdown
Planifica un nuevo modelo de base de datos siguiendo el template de ai-project-playbook/03-roadmap/plan-templates.md

**CONTEXT TO LOAD:**
- Read: CLAUDE.md (model patterns)
- Read: app/models/[existing_model].py (model structure)
- Read: migrations/[latest].py (migration pattern)

**MODEL DETAILS:**
- Name: [ModelName]
- Purpose: [What data it represents]
- Fields:
  - [field1]: type (constraints, default)
  - [field2]: type (constraints, default)
- Relationships:
  - [Model1]: [one-to-many/many-to-many] (description)
- Indexes: [Which fields need indexes]

**VALIDATION RULES:**
- [field1]: [validation rules]
- [field2]: [validation rules]

**MIGRATION STRATEGY:**
- New table or alter existing?
- Data migration needed: [Yes/No - describe]

**OUTPUT:**
Create structured plan with:
1. CONTEXT REFERENCES
2. IMPLEMENTATION PLAN
3. STEP-BY-STEP TASKS (model → migration → tests)
4. VALIDATION COMMANDS (alembic + pytest)

Save to: plans/[model-name].md
```

---

#### Prompt 3.2: Database Migration

```markdown
Planifica una migración de base de datos siguiendo el template de ai-project-playbook/03-roadmap/plan-templates.md

**CONTEXT TO LOAD:**
- Read: app/models/[affected_model].py (current model)
- Read: migrations/[latest].py (migration pattern)

**MIGRATION DETAILS:**
- Type: [ADD column / MODIFY column / DROP column / ADD table / etc.]
- Affected table(s): [table1, table2]
- Changes:
  - [Change 1]
  - [Change 2]

**DATA MIGRATION:**
- Existing data: [How to handle - transform, delete, default values]
- Backwards compatible: [Yes/No]

**ROLLBACK STRATEGY:**
- downgrade() implementation: [How to undo this migration]
- Data loss on rollback: [Yes/No - what gets lost]

**OUTPUT:**
Create structured plan with:
1. CONTEXT REFERENCES
2. IMPLEMENTATION PLAN
3. STEP-BY-STEP TASKS (migration → model update → tests → apply → rollback test)
4. VALIDATION COMMANDS (alembic check + history + up/down)

Save to: plans/migration-[description].md
```

---

### CATEGORÍA 4: Features Complejas

#### Prompt 4.1: Multi-Component Feature

```markdown
Planifica una feature completa (backend + frontend) siguiendo el template de ai-project-playbook/03-roadmap/plan-templates.md

**CONTEXT TO LOAD:**
- Read: CLAUDE.md
- Read: [relevant backend files]
- Read: [relevant frontend files]

**FEATURE OVERVIEW:**
- Name: [Feature name]
- User story: As a [user], I want to [action], so that [benefit]
- Acceptance criteria:
  1. [Criterion 1]
  2. [Criterion 2]
  3. [Criterion 3]

**COMPONENTS:**

**Backend:**
- Models: [Model1, Model2]
- Services: [Service functions needed]
- Endpoints: [List endpoints - GET/POST/etc. with paths]

**Frontend:**
- Components: [Component1, Component2]
- Pages: [Page updates/new pages]
- State management: [How data flows]

**INTEGRATION FLOW:**
1. [Step 1 - user action]
2. [Step 2 - API call]
3. [Step 3 - backend processing]
4. [Step 4 - response handling]
5. [Step 5 - UI update]

**OUTPUT:**
Create structured plan with:
1. CONTEXT REFERENCES (all relevant files)
2. IMPLEMENTATION PLAN (architecture overview)
3. STEP-BY-STEP TASKS (backend first, then frontend, then integration)
4. VALIDATION COMMANDS (backend tests + frontend tests + E2E test)

Save to: plans/[feature-name].md
```

---

#### Prompt 4.2: Authentication/Authorization

```markdown
Planifica implementación de autenticación/autorización siguiendo el template de ai-project-playbook/03-roadmap/plan-templates.md

**CONTEXT TO LOAD:**
- Read: CLAUDE.md (security patterns)
- Read: app/core/config.py (environment variables)
- Docs: [JWT / OAuth2 / etc. documentation]

**AUTH STRATEGY:**
- Type: [JWT / Session / OAuth2 / etc.]
- Token storage: [Where - localStorage, httpOnly cookie, etc.]
- Token expiry: [Duration]
- Refresh tokens: [Yes/No]

**COMPONENTS:**

**Backend:**
- Models: User, Token (if needed)
- Endpoints:
  - POST /auth/register
  - POST /auth/login
  - POST /auth/logout
  - POST /auth/refresh (if using refresh tokens)
- Middleware: verify_token() dependency
- Password hashing: [bcrypt / argon2 / etc.]

**Frontend:**
- Auth context (React Context API / Zustand / etc.)
- Protected routes
- Login/Register pages
- Token management (storage, refresh, clear)

**SECURITY CONSIDERATIONS:**
- [CSRF protection]
- [XSS prevention]
- [SQL injection prevention]
- [Rate limiting on login endpoint]

**OUTPUT:**
Create structured plan with CONTEXT → PLAN → TASKS → VALIDATION
Include security testing in validation commands.
Save to: plans/auth-implementation.md
```

---

### CATEGORÍA 5: Refactoring & Bug Fixes

#### Prompt 5.1: Bug Fix

```markdown
Planifica un bug fix siguiendo el template de ai-project-playbook/03-roadmap/plan-templates.md

**CONTEXT TO LOAD:**
- Read: [file_with_bug].py (current implementation)
- Read: tests/test_[file].py (existing tests)
- Issue: [Link to GitHub issue / bug report]

**BUG DESCRIPTION:**
- What's broken: [Describe the bug]
- How to reproduce:
  1. [Step 1]
  2. [Step 2]
  3. [Step 3]
- Expected behavior: [What should happen]
- Actual behavior: [What actually happens]

**ROOT CAUSE ANALYSIS:**
[Hypothesize what's causing the bug - will be verified in planning phase]

**AFFECTED AREAS:**
- Files likely affected: [file1, file2]
- Side effects possible: [Yes/No - what might break]

**FIX STRATEGY:**
- Regression test first: [Yes - write test that fails]
- Fix approach: [High-level fix strategy]
- Backwards compatible: [Yes/No]

**OUTPUT:**
Create structured plan with:
1. CONTEXT REFERENCES (bug location + related code)
2. IMPLEMENTATION PLAN (root cause + fix)
3. STEP-BY-STEP TASKS (regression test → fix → verify → full test suite)
4. VALIDATION COMMANDS (regression test + full tests + manual verification)

Save to: plans/bugfix-[issue-number].md
```

---

#### Prompt 5.2: Refactoring

```markdown
Planifica un refactoring siguiendo el template de ai-project-playbook/03-roadmap/plan-templates.md

**CONTEXT TO LOAD:**
- Read: [file_to_refactor].py (current implementation)
- Read: CLAUDE.md (code style standards)
- Read: tests/test_[file].py (existing tests)

**REFACTOR GOAL:**
- What to refactor: [Function/Class/Module]
- Why: [Tech debt / Performance / Readability / Maintainability]
- Success metric: [How to measure improvement]

**CURRENT STATE:**
- Issues with current implementation:
  1. [Issue 1]
  2. [Issue 2]
- Test coverage: [%]

**TARGET STATE:**
- Desired structure: [High-level description]
- Improvements:
  1. [Improvement 1]
  2. [Improvement 2]

**CONSTRAINTS:**
- Backwards compatibility: [Must maintain / Breaking change OK]
- Performance: [Must not regress / Can sacrifice for clarity]
- API changes: [Yes/No - what changes]

**OUTPUT:**
Create structured plan with:
1. CONTEXT REFERENCES
2. IMPLEMENTATION PLAN
3. STEP-BY-STEP TASKS (ensure 100% test coverage first → refactor → verify tests pass → update tests if API changed)
4. VALIDATION COMMANDS (all tests pass + no performance regression)

Save to: plans/refactor-[description].md
```

---

### CATEGORÍA 6: Testing & Validation

#### Prompt 6.1: Add Test Coverage

```markdown
Planifica agregar tests a código existente sin tests.

**CONTEXT TO LOAD:**
- Read: [file_to_test].py (implementation)
- Read: CLAUDE.md (testing patterns)
- Read: tests/test_[similar].py (existing test structure)

**TARGET:**
- File to test: [file path]
- Current coverage: [% - run pytest --cov first]
- Target coverage: [% - typically 80-100%]

**FUNCTIONS TO TEST:**
1. [function1()] - [what it does]
2. [function2()] - [what it does]
3. [function3()] - [what it does]

**TEST SCENARIOS:**
For each function:
- Happy path (valid inputs)
- Edge cases (empty, null, boundary values)
- Error cases (invalid inputs, exceptions)
- Integration (if function calls other functions/APIs)

**OUTPUT:**
Create structured plan with:
1. CONTEXT REFERENCES
2. IMPLEMENTATION PLAN (test strategy)
3. STEP-BY-STEP TASKS (one test file per module, group by function)
4. VALIDATION COMMANDS (pytest with coverage report)

Save to: plans/add-tests-[module].md
```

---

#### Prompt 6.2: Integration Testing

```markdown
Planifica tests de integración para feature completa.

**CONTEXT TO LOAD:**
- Read: CLAUDE.md (testing patterns)
- Read: tests/conftest.py (fixtures)
- Read: [backend endpoint files]
- Read: [frontend component files]

**FEATURE TO TEST:**
- Feature: [Feature name]
- User flow:
  1. [Step 1]
  2. [Step 2]
  3. [Step 3]

**TEST SCENARIOS:**
1. Happy path (everything works)
2. Error handling (API errors, network failures)
3. Edge cases (empty data, concurrent requests)
4. Permissions (unauthorized access attempts)

**INTEGRATION POINTS:**
- Backend endpoints: [List]
- Frontend components: [List]
- External services: [If any]

**OUTPUT:**
Create structured plan with:
1. CONTEXT REFERENCES
2. IMPLEMENTATION PLAN (test strategy, fixtures needed)
3. STEP-BY-STEP TASKS (setup → tests → teardown)
4. VALIDATION COMMANDS (pytest -m integration)

Save to: plans/integration-test-[feature].md
```

---

### CATEGORÍA 7: Data & Analytics

#### Prompt 7.1: Data Pipeline

```markdown
Planifica un pipeline de datos siguiendo el template de ai-project-playbook/03-roadmap/plan-templates.md

**CONTEXT TO LOAD:**
- Read: CLAUDE.md (data patterns)
- Read: [existing pipeline example if any]

**PIPELINE DETAILS:**
- Name: [Pipeline name]
- Source: [Where data comes from - API, CSV, DB, etc.]
- Destination: [Where data goes - DB, file, another API]
- Frequency: [One-time / Hourly / Daily / Real-time]

**TRANSFORMATIONS:**
1. [Transformation 1 - describe]
2. [Transformation 2 - describe]
3. [Transformation 3 - describe]

**DATA VALIDATION:**
- Schema validation: [Expected columns/types]
- Quality checks: [Nulls, duplicates, ranges]
- Error handling: [What to do with bad data]

**TOOLS:**
- [Pandas / Polars / DuckDB / etc.]
- Orchestration: [Airflow / Prefect / Cron / etc.]

**OUTPUT:**
Create structured plan with:
1. CONTEXT REFERENCES
2. IMPLEMENTATION PLAN (pipeline architecture)
3. STEP-BY-STEP TASKS (extract → transform → validate → load → schedule)
4. VALIDATION COMMANDS (test with sample data + data quality tests)

Save to: plans/pipeline-[name].md
```

---

#### Prompt 7.2: Analytics Dashboard

```markdown
Planifica un dashboard de analítica siguiendo el template.

**CONTEXT TO LOAD:**
- Read: CLAUDE.md (data viz patterns)
- Read: [existing dashboard example if any]

**DASHBOARD DETAILS:**
- Name: [Dashboard name]
- Purpose: [What insights it provides]
- Users: [Who will use it]
- Data source: [Database / API / CSV]

**METRICS/KPIs:**
1. [Metric 1]: [Description, calculation]
2. [Metric 2]: [Description, calculation]
3. [Metric 3]: [Description, calculation]

**VISUALIZATIONS:**
1. [Chart type]: [What it shows]
2. [Chart type]: [What it shows]
3. [Chart type]: [What it shows]

**FILTERS/INTERACTIVITY:**
- Date range selector
- [Filter 2]
- [Filter 3]

**TECH STACK:**
- [Streamlit / Plotly Dash / React + Recharts / etc.]

**OUTPUT:**
Create structured plan with:
1. CONTEXT REFERENCES
2. IMPLEMENTATION PLAN (dashboard layout, data fetching strategy)
3. STEP-BY-STEP TASKS (data layer → calculations → visualizations → interactivity)
4. VALIDATION COMMANDS (run dashboard + manual testing)

Save to: plans/dashboard-[name].md
```

---

## 🎯 Prompts Meta (Planning de Planning)

### Meta Prompt 1: Vibe Planning Session

```markdown
Ayúdame a explorar soluciones para [FEATURE] antes de crear el plan estructurado.

**Context:**
- Read: CLAUDE.md
- Explore: [relevant directories]

**Feature to explore:**
[Brief description of feature]

**Questions to explore:**
1. What's the best architecture for this?
2. What existing patterns can I follow?
3. What are the edge cases?
4. What could go wrong?

**Output:**
Brainstorm 2-3 different approaches.
For each approach, list:
- Pros
- Cons
- Complexity (Low/Medium/High)
- Risks

Then recommend the best approach with rationale.

After this vibe session, we'll create the structured plan.
```

**Cuándo usar:**
- Feature compleja donde no está claro el approach
- Múltiples formas de implementar algo
- Necesitas explorar trade-offs antes de decidir

---

### Meta Prompt 2: Plan Review

```markdown
Revisa el plan en plans/[feature].md y mejóralo.

**Review checklist:**

**1. CONTEXT REFERENCES:**
- [ ] Incluye CLAUDE.md
- [ ] Incluye archivos relevantes existentes
- [ ] Menciona patterns a seguir
- [ ] Tiene suficiente contexto (no demasiado, no muy poco)

**2. IMPLEMENTATION PLAN:**
- [ ] Describe el problema claramente
- [ ] Explica la solución en alto nivel
- [ ] Lista todos los componentes
- [ ] Incluye decisiones técnicas con rationale

**3. STEP-BY-STEP TASKS:**
- [ ] Pasos numerados en orden lógico
- [ ] Cada paso es específico (no vago)
- [ ] Incluye nombres de archivos exactos
- [ ] Agrupa en phases lógicas
- [ ] Incluye tests (no los olvida)

**4. VALIDATION COMMANDS:**
- [ ] Type checking (mypy)
- [ ] Unit tests (pytest)
- [ ] Manual testing (curl / UI check)
- [ ] Expected outputs documentados

**Output:**
- List issues found
- Suggest improvements
- Output improved plan
```

---

### Meta Prompt 3: Generate Custom Prompt Template

```markdown
Crea un prompt template reutilizable para [TYPE OF TASK].

**Task type:** [Describe el tipo de tarea - ej: "crear workers de background jobs", "agregar webhooks", etc.]

**Common variables:**
[List variables que cambiarían entre usos - ej: worker_name, event_type, etc.]

**Context typically needed:**
[What files/docs are usually relevant for this task type]

**Steps that are usually the same:**
[Common steps for this task type]

**Output format:**
Create a prompt template following the structure of prompts in ai-project-playbook/03-roadmap/planning-prompts.md

The template should have:
- CONTEXT TO LOAD section
- [TASK-SPECIFIC] DETAILS section with variables in [BRACKETS]
- OUTPUT section

Save to: my_workspace/custom-prompts/[task-type].md
```

**Cuándo usar:**
- Tienes una tarea que se repite (no está en esta biblioteca)
- Quieres crear tu propia biblioteca de prompts custom
- Proyecto con patterns únicos que quieres codificar

---

## 🛠️ Cómo Usar Esta Biblioteca

### Opción 1: Copy-Paste Directo

1. Encuentra el prompt apropiado arriba
2. Copia el prompt completo
3. Reemplaza las variables en [BRACKETS]
4. Pega en Claude Code
5. Claude genera el plan estructurado

**Tiempo:** 30 segundos

---

### Opción 2: Con /plan Command

```markdown
# .claude/commands/plan.md

Feature to plan: $1
Feature type: $2  # backend-api | frontend-component | database | feature | bugfix | refactor

## Step 1: Load Prompt Template
Based on $2, load prompt from ai-project-playbook/03-roadmap/planning-prompts.md:
- backend-api → Prompt 1.1/1.2/1.3/1.4 (based on HTTP method in $1)
- frontend-component → Prompt 2.1
- database → Prompt 3.1 or 3.2
- feature → Prompt 4.1
- bugfix → Prompt 5.1
- refactor → Prompt 5.2

## Step 2: Customize Template
Fill template with specifics from $1 and conversation context.

## Step 3: Execute Template
Generate structured plan following template.

## Step 4: Save Plan
Save to: plans/[feature-name].md
```

**Uso:**
```
/plan "GET endpoint for product search" backend-api
```

---

### Opción 3: Chatear con Claude Para Customizar

```
Usuario: Necesito planear un endpoint de búsqueda de productos.

Claude: ¡Perfecto! Voy a usar el prompt template para GET endpoints.

Déjame hacerte algunas preguntas para customizar el plan:

1. ¿Qué parámetros de búsqueda necesitas? (query, filtros, etc.)
2. ¿Hay un endpoint similar que deba seguir como patrón?
3. ¿Qué edge cases esperas? (resultados vacíos, parámetros inválidos, etc.)

[Usuario responde]

Claude: Perfecto. Generando plan estructurado usando el template...

[Genera plan customizado]
```

---

## 📊 Comparación: Prompt Ad-Hoc vs. Template

### ❌ Prompt Ad-Hoc (Sin Template)

```
Ayúdame a crear un endpoint de búsqueda de productos.
```

**Resultado:**
- Claude improvisa el plan
- Puede olvidar leer CLAUDE.md
- Puede no incluir tests
- Puede no definir validation
- Estructura inconsistente con otros planes

**Tiempo para prompt:** 30 segundos
**Tiempo para corregir plan incompleto:** 10 minutos
**Total:** 10.5 minutos

---

### ✅ Usando Template

```
[Copy-paste Prompt 1.1: New GET Endpoint]

[Fill variables in 30 seconds]
```

**Resultado:**
- Plan estructurado consistente
- Siempre incluye CLAUDE.md
- Siempre incluye tests
- Validation completa definida
- Sigue estructura estándar

**Tiempo para prompt:** 30 segundos
**Tiempo para corregir:** 0 minutos
**Total:** 30 segundos

**Ahorro:** 10 minutos por feature × 10 features/semana = **100 minutos/semana ahorrados**

---

## 🎨 Customización de Templates

### Agregar Variables Custom

Si tu proyecto tiene patterns únicos, agrega secciones custom:

**Ejemplo: Proyecto con Event Sourcing**

```markdown
## Prompt 1.1 Custom: New GET Endpoint (Event Sourced)

[... secciones estándar ...]

**EVENT SOURCING CONSIDERATIONS:**
- Events to query: [Event1, Event2]
- Projection needed: [Yes/No - describe]
- Event store: [Which event store to query]
- Consistency: [Eventual / Strong - explain trade-off]

[... resto del template ...]
```

---

### Crear Template para Domain Específico

**Ejemplo: E-commerce**

```markdown
## E-commerce Prompt: New Product Feature

**CONTEXT TO LOAD:**
- Read: CLAUDE.md
- Read: app/models/product.py
- Read: app/models/inventory.py
- Read: app/services/pricing_service.py (pricing rules)

**FEATURE DETAILS:**
[Feature description]

**INVENTORY IMPACT:**
- Does this affect stock levels? [Yes/No]
- Reservation needed? [Yes/No]

**PRICING IMPACT:**
- Pricing rules affected? [Yes/No]
- Discounts applicable? [Yes/No]

**CHECKOUT IMPACT:**
- Affects checkout flow? [Yes/No]

[... resto del template ...]
```

---

## 🚨 Errores Comunes al Usar Templates

### Error 1: No Reemplazar TODAS las Variables

**❌ Malo:**
```markdown
Path: GET /api/v1/[RESOURCE]/[ACTION]  # Olvidó reemplazar
```

**✅ Bueno:**
```markdown
Path: GET /api/v1/products/search  # Variables reemplazadas
```

---

### Error 2: No Agregar Context Específico

**❌ Malo:**
```markdown
**CONTEXT TO LOAD:**
- Read: CLAUDE.md  # Solo esto
```

**✅ Bueno:**
```markdown
**CONTEXT TO LOAD:**
- Read: CLAUDE.md
- Read: app/api/products.py (existing GET pattern to follow)
- Read: app/models/product.py (ProductResponse model)
```

---

### Error 3: No Customizar Edge Cases

**❌ Malo:**
```markdown
**EDGE CASES TO HANDLE:**
- [Add specific edge cases]  # Dejó el placeholder
```

**✅ Bueno:**
```markdown
**EDGE CASES TO HANDLE:**
- Empty search results (return empty list)
- Invalid category filter (return 400 with error message)
- Query too short (< 3 chars - return 400)
- Too many results (limit to 100, add pagination)
```

---

## 🎯 Best Practices

### 1. Mantén Tu Propia Biblioteca

```
my_workspace/
├── custom-prompts/
│   ├── new-background-job.md
│   ├── new-webhook.md
│   ├── new-cron-task.md
│   └── add-cache-layer.md
```

**Cada vez que repites una tarea:**
1. Crea template para esa tarea
2. Guárdalo en `custom-prompts/`
3. Reutiliza en próximas ocasiones

---

### 2. Versiona Tus Templates

```markdown
# new-api-endpoint-v2.md

**Changelog:**
- v2: Added rate limiting section
- v1: Initial version

[... template ...]
```

**Por qué:** Templates mejoran con el tiempo. Versionar ayuda a trackear mejoras.

---

### 3. Comparte Templates con el Team

Si trabajas en equipo:

```
.claude/
├── commands/
│   └── plan.md
├── team-prompts/
│   ├── backend/
│   │   ├── new-endpoint.md
│   │   └── new-service.md
│   ├── frontend/
│   │   ├── new-component.md
│   │   └── new-page.md
│   └── README.md  # Cómo usar estos templates
```

**Beneficio:** Todo el equipo genera planes consistentes.

---

## 📚 Referencias

**Files relacionados:**
- `plan-templates.md` - Estructura de los planes que estos prompts generan
- `slash-commands.md` - Cómo ejecutar estos planes con /plan command
- `feature-breakdown.md` - Cómo descomponer features complejas

**Templates en blanco:**
- `templates/plan-template.md` - Template vacío listo para copiar

---

## 🎓 Ejercicio: Crea Tu Primer Prompt Custom

**Tarea:**
Piensa en una tarea que repites frecuentemente en tu proyecto (que no esté en esta biblioteca).

**Pasos:**
1. Usa "Meta Prompt 3: Generate Custom Prompt Template"
2. Describe tu tarea repetitiva
3. Claude generará un template custom para ti
4. Guárdalo en `my_workspace/custom-prompts/[task].md`
5. Úsalo la próxima vez que hagas esa tarea

**Resultado:**
Tendrás tu propia biblioteca de prompts adaptada a TU proyecto. 🎯

---

**🎯 Remember: Cada minuto invertido en crear un buen prompt template ahorra 10 minutos en cada feature subsecuente.**

**La biblioteca de prompts crece con tu proyecto. Build it incrementally. 🚀**
