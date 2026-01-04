# 📋 Plan Templates - Estructura de Planes Agent-to-Agent

**Guía completa para crear planes estructurados que maximizan la efectividad de la IA**

---

## 🎯 ¿Por Qué Importa la Estructura de los Planes?

### El Problema Sin Estructura

**❌ Plan vago (90% de developers):**
```
"Agrega un endpoint de login"
```

**Resultado:**
- La IA improvisa
- Ignora context existente
- No escribe tests
- Código inconsistente con el resto del proyecto
- ~30% code acceptance rate

---

**✅ Plan estructurado (top 5%):**
```markdown
## CONTEXT REFERENCES
- Read: app/api/users.py (existing user model)
- Read: CLAUDE.md (project standards)
- Pattern: Follow POST /products pattern from app/api/products.py:15-40

## IMPLEMENTATION PLAN
Create POST /auth/login endpoint with:
- Email + password validation
- JWT token generation
- Rate limiting (5 attempts/minute)

## STEP-BY-STEP TASKS
1. Create app/models/auth.py (LoginRequest, LoginResponse)
2. Create app/api/auth.py (POST /auth/login endpoint)
3. Create tests/test_auth.py (test_login_success, test_login_invalid)
4. Run validation: pytest tests/test_auth.py

## VALIDATION COMMANDS
!pytest tests/test_auth.py -v
!mypy app/api/auth.py
!curl -X POST http://localhost:8000/auth/login -d '{"email":"test@example.com","password":"pass123"}'
```

**Resultado:**
- La IA sigue el plan exactamente
- Lee context necesario primero
- Escribe tests automáticamente
- Código consistente con CLAUDE.md
- ~88% code acceptance rate

---

## 📐 La Anatomía de un Plan Estructurado

Todo plan debe tener **4 secciones obligatorias:**

### 1. CONTEXT REFERENCES

**Qué es:**
Lista explícita de archivos que la IA DEBE leer antes de implementar.

**Por qué importa:**
Sin context references, la IA inventa estructuras nuevas en vez de seguir las existentes.

**Formato:**
```markdown
## CONTEXT REFERENCES
- Read: path/to/file.py (explicación de por qué)
- Read: CLAUDE.md (project standards)
- Pattern: Follow [pattern description] from path/to/example.py:line-range
- Explore: src/components/ (understand component structure)
```

**Tipos de references:**

**a) Read (archivos específicos):**
```markdown
- Read: app/models/product.py (existing Pydantic models)
- Read: app/core/config.py (environment variables)
- Read: tests/conftest.py (pytest fixtures)
```

**b) Pattern (seguir ejemplo existente):**
```markdown
- Pattern: Follow error handling from app/api/products.py:25-30
- Pattern: Use same logging pattern from app/services/product_service.py:15
```

**c) Explore (explorar estructura):**
```markdown
- Explore: app/api/ (understand existing API structure)
- Explore: tests/ (see testing patterns)
```

**d) External (documentación externa):**
```markdown
- Docs: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
- Reference: OpenAPI spec at docs/api-spec.yaml
```

---

### 2. IMPLEMENTATION PLAN

**Qué es:**
Descripción en alto nivel de QUÉ se va a construir (no cómo).

**Por qué importa:**
Da contexto del problema antes de entrar en detalles técnicos.

**Formato:**
```markdown
## IMPLEMENTATION PLAN

**Feature:** [Nombre de la feature]

**Problem:** [Qué problema resuelve]

**Solution:** [Approach en alto nivel]

**Components:**
- [Componente 1]: [Descripción]
- [Componente 2]: [Descripción]

**Technical Decisions:**
- [Decisión técnica importante con rationale]
```

**Ejemplo completo:**
```markdown
## IMPLEMENTATION PLAN

**Feature:** User Authentication with JWT

**Problem:**
Users need secure login to access protected endpoints. Currently no authentication exists.

**Solution:**
Implement JWT-based authentication with:
- Login endpoint (email + password)
- Token generation with 24h expiry
- Token validation middleware

**Components:**
- Auth models: LoginRequest, LoginResponse, TokenPayload
- Auth endpoint: POST /auth/login
- Auth middleware: verify_token() dependency
- Auth service: hash_password(), verify_password(), create_token()

**Technical Decisions:**
- Use bcrypt for password hashing (industry standard)
- JWT tokens with HS256 (sufficient for MVP, can upgrade to RS256 later)
- Store secret in environment variable (never in code)
- Rate limit login endpoint (prevent brute force)
```

---

### 3. STEP-BY-STEP TASKS

**Qué es:**
Lista ordenada de pasos técnicos específicos para implementar el plan.

**Por qué importa:**
Sin esto, la IA puede hacer cosas en orden incorrecto o saltarse pasos críticos.

**Formato:**
```markdown
## STEP-BY-STEP TASKS

**Phase 1: Models**
1. Create app/models/auth.py
   - LoginRequest (email: EmailStr, password: str)
   - LoginResponse (access_token: str, token_type: str)
   - TokenPayload (sub: str, exp: datetime)

**Phase 2: Service Layer**
2. Create app/services/auth_service.py
   - hash_password(password: str) -> str
   - verify_password(plain: str, hashed: str) -> bool
   - create_token(user_id: str) -> str
   - verify_token(token: str) -> TokenPayload

**Phase 3: API Endpoint**
3. Create app/api/auth.py
   - POST /auth/login endpoint
   - Return LoginResponse
   - Handle invalid credentials (401)

**Phase 4: Tests**
4. Create tests/test_auth.py
   - test_login_success()
   - test_login_invalid_email()
   - test_login_invalid_password()
   - test_token_validation()

**Phase 5: Validation**
5. Run validation commands (see section 4)
```

**Best practices:**

**✅ DO:**
- Numerar cada paso
- Agrupar en phases lógicas
- Especificar nombres exactos de archivos
- Incluir firmas de funciones (params + return types)
- Mencionar edge cases a manejar

**❌ DON'T:**
- Dejar pasos vagos ("implementar auth")
- Omitir tests
- Asumir que la IA "sabrá" el orden correcto
- Dejar TODOs para "implementar después"

---

### 4. VALIDATION COMMANDS

**Qué es:**
Comandos bash específicos para verificar que la implementación funciona.

**Por qué importa:**
Sin validation clara, la IA puede marcar como "done" código que no funciona.

**Formato:**
```markdown
## VALIDATION COMMANDS

**Syntax & Types:**
!mypy app/api/auth.py
!mypy app/services/auth_service.py

**Tests:**
!pytest tests/test_auth.py -v
!pytest tests/test_auth.py::test_login_success -v

**Manual Testing:**
# Start server
!uvicorn app.main:app --reload

# Test login endpoint
!curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Expected: {"access_token":"eyJ...", "token_type":"bearer"}

**Integration:**
!pytest tests/ -v  # All tests must pass
```

**Niveles de validation:**

**Level 1 - Syntax:**
```markdown
!python -m py_compile app/api/auth.py
```

**Level 2 - Type Safety:**
```markdown
!mypy app/ --strict
```

**Level 3 - Unit Tests:**
```markdown
!pytest tests/test_auth.py -v --cov=app/services/auth_service
```

**Level 4 - Integration Tests:**
```markdown
!pytest tests/ -v -m integration
```

**Level 5 - Manual Verification:**
```markdown
# Expected behavior documented
!curl [command]  # Expected: [exact output]
```

---

## 🎨 Templates Reutilizables

### Template 1: New API Endpoint

```markdown
## CONTEXT REFERENCES
- Read: CLAUDE.md (API patterns)
- Read: app/models/[existing_model].py (model structure)
- Pattern: Follow POST /[existing_endpoint] from app/api/[file].py:line-range

## IMPLEMENTATION PLAN

**Feature:** [Endpoint name]

**HTTP Method:** [GET/POST/PUT/DELETE]

**Path:** /api/v1/[resource]/[action]

**Request:**
- Body: [RequestModel fields]
- Query params: [if applicable]
- Headers: [if applicable]

**Response:**
- Success (200/201): [ResponseModel fields]
- Error (400/404/500): ErrorResponse

**Business Logic:**
[Describe what happens]

## STEP-BY-STEP TASKS

1. Create app/models/[resource].py
   - [RequestModel] (fields)
   - [ResponseModel] (fields)

2. Create app/services/[resource]_service.py
   - [business_logic_function](params) -> return_type

3. Create app/api/[resource].py
   - [HTTP_METHOD] /api/v1/[resource]/[action]
   - Use service layer
   - Return [ResponseModel]

4. Create tests/test_[resource].py
   - test_[endpoint]_success()
   - test_[endpoint]_validation_error()
   - test_[endpoint]_not_found()

## VALIDATION COMMANDS
!mypy app/api/[resource].py
!pytest tests/test_[resource].py -v
!curl -X [METHOD] http://localhost:8000/api/v1/[resource]/[action] -d '[json]'
```

---

### Template 2: New Frontend Component

```markdown
## CONTEXT REFERENCES
- Read: CLAUDE.md (component patterns)
- Read: src/components/[ExistingComponent].tsx (component structure)
- Read: src/lib/api-client.ts (API calling pattern)

## IMPLEMENTATION PLAN

**Component:** [ComponentName]

**Purpose:** [What it does]

**Props:**
- [prop1]: type (description)
- [prop2]: type (description)

**State:**
- [state1]: type (description)

**API Calls:**
- [endpoint] (when, why)

**UI Structure:**
[Brief description]

## STEP-BY-STEP TASKS

1. Create src/components/[ComponentName].tsx
   - Define Props interface
   - Implement component with hooks
   - Add error handling
   - Add loading states

2. Create src/components/[ComponentName].test.tsx
   - test_renders_correctly()
   - test_handles_loading()
   - test_handles_error()
   - test_user_interaction()

3. Export from src/components/index.ts

4. Import in parent component (src/[Parent].tsx)

## VALIDATION COMMANDS
!npm run typecheck
!npm run test -- [ComponentName].test.tsx
!npm run build  # Must succeed
```

---

### Template 3: Database Migration

```markdown
## CONTEXT REFERENCES
- Read: app/models/[existing].py (current schema)
- Read: migrations/[latest].py (migration pattern)
- Docs: Alembic documentation for [operation_type]

## IMPLEMENTATION PLAN

**Migration:** [Description]

**Changes:**
- [Table]: [ADD/MODIFY/DROP] [column/constraint]

**Data Migration:**
[If existing data needs transformation]

**Rollback Strategy:**
[How to undo this migration]

## STEP-BY-STEP TASKS

1. Create migration
   !alembic revision -m "[description]"

2. Edit migrations/versions/[hash]_[description].py
   - Implement upgrade()
   - Implement downgrade()
   - Add data migration if needed

3. Update app/models/[model].py
   - Reflect schema changes

4. Test migration
   !alembic upgrade head  # Apply
   !alembic downgrade -1  # Rollback
   !alembic upgrade head  # Re-apply

## VALIDATION COMMANDS
!alembic check  # No pending migrations
!pytest tests/test_models.py -v  # Models match DB
!alembic history  # Migration in history
```

---

### Template 4: Bug Fix

```markdown
## CONTEXT REFERENCES
- Read: [file_with_bug].py (current implementation)
- Read: tests/test_[file].py (existing tests)
- Issue: [GitHub issue / bug report link]

## IMPLEMENTATION PLAN

**Bug:** [Brief description]

**Root Cause:** [What's causing it]

**Fix:** [How to fix it]

**Affected Areas:**
- [File 1]: [What needs to change]
- [File 2]: [What needs to change]

**Risk Assessment:**
- Breaking changes? [Yes/No + explanation]
- Affects existing behavior? [Yes/No + explanation]

## STEP-BY-STEP TASKS

1. Add regression test to tests/test_[file].py
   - test_[bug_scenario]() that FAILS currently

2. Fix bug in [file].py
   - [Specific change]

3. Verify regression test now PASSES
   !pytest tests/test_[file].py::test_[bug_scenario] -v

4. Run full test suite
   !pytest tests/ -v

## VALIDATION COMMANDS
!pytest tests/test_[file].py::test_[bug_scenario] -v  # Must pass
!pytest tests/ -v  # All tests must pass
!mypy [file].py  # No new type errors
```

---

### Template 5: Refactoring

```markdown
## CONTEXT REFERENCES
- Read: [file_to_refactor].py (current implementation)
- Read: CLAUDE.md (code style standards)
- Read: tests/test_[file].py (existing tests)

## IMPLEMENTATION PLAN

**Refactor:** [What to refactor]

**Reason:** [Why - tech debt, performance, readability]

**Approach:**
[High-level strategy]

**Backwards Compatibility:**
[Yes/No + migration strategy if needed]

## STEP-BY-STEP TASKS

1. Ensure 100% test coverage BEFORE refactoring
   !pytest tests/test_[file].py --cov=[file] --cov-report=term-missing
   - Add missing tests if coverage < 100%

2. Refactor [file].py
   - [Specific change 1]
   - [Specific change 2]
   - DO NOT change test files yet

3. Verify all existing tests still pass
   !pytest tests/test_[file].py -v

4. Update tests if API changed (only if necessary)

5. Verify no performance regression
   !pytest tests/test_[file].py --benchmark

## VALIDATION COMMANDS
!pytest tests/ -v  # All tests pass
!mypy [file].py  # No new type errors
!pytest tests/test_[file].py --cov=[file] --cov-report=term-missing  # Coverage maintained
```

---

## 📊 Comparación: Plan Malo vs. Plan Bueno

### ❌ Plan Malo

```markdown
Implementa autenticación JWT en el backend.

Tareas:
- Crear modelos
- Crear endpoint de login
- Agregar middleware
- Escribir tests
```

**Problemas:**
- ❌ No especifica archivos a leer
- ❌ No define estructura de modelos
- ❌ No dice QUÉ tests escribir
- ❌ No incluye validation commands
- ❌ Orden de tareas ambiguo

**Resultado esperado:**
- IA inventa estructura de modelos
- Endpoint inconsistente con resto del código
- Tests genéricos sin coverage completo
- No valida que funcione
- **Code acceptance: ~30%**

---

### ✅ Plan Bueno

```markdown
## CONTEXT REFERENCES
- Read: CLAUDE.md (security patterns)
- Read: app/core/config.py (get JWT_SECRET)
- Read: app/models/user.py (User model)
- Pattern: Follow error handling from app/api/products.py:25-30
- Docs: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/

## IMPLEMENTATION PLAN

**Feature:** JWT Authentication

**Problem:**
No authentication exists. Need secure login for protected endpoints.

**Solution:**
- Login endpoint: POST /auth/login (email + password → JWT token)
- Token validation middleware: verify_token() dependency
- Password hashing: bcrypt

**Components:**
- Models: LoginRequest, LoginResponse, TokenPayload
- Service: AuthService (hash, verify, create_token, verify_token)
- Endpoint: POST /auth/login
- Middleware: get_current_user() dependency

## STEP-BY-STEP TASKS

**Phase 1: Models (app/models/auth.py)**
1. Create LoginRequest
   - email: EmailStr
   - password: str (min_length=8)

2. Create LoginResponse
   - access_token: str
   - token_type: Literal["bearer"]

3. Create TokenPayload
   - sub: str (user_id)
   - exp: datetime

**Phase 2: Service (app/services/auth_service.py)**
4. Create AuthService class
   - hash_password(password: str) -> str
   - verify_password(plain: str, hashed: str) -> bool
   - create_token(user_id: str, expires_delta: timedelta) -> str
   - verify_token(token: str) -> TokenPayload

**Phase 3: Endpoint (app/api/auth.py)**
5. Create POST /auth/login
   - Accept LoginRequest
   - Query user by email from DB
   - Verify password with AuthService
   - Return LoginResponse with token
   - Raise 401 if invalid credentials

**Phase 4: Middleware (app/core/security.py)**
6. Create get_current_user() dependency
   - Extract token from Authorization header
   - Verify token with AuthService
   - Return User object
   - Raise 401 if invalid token

**Phase 5: Tests (tests/test_auth.py)**
7. Create tests
   - test_login_success()
   - test_login_invalid_email()
   - test_login_invalid_password()
   - test_login_user_not_found()
   - test_token_validation()
   - test_token_expired()
   - test_get_current_user()

## VALIDATION COMMANDS

**Type Checking:**
!mypy app/models/auth.py
!mypy app/services/auth_service.py
!mypy app/api/auth.py
!mypy app/core/security.py

**Unit Tests:**
!pytest tests/test_auth.py -v --cov=app/services/auth_service --cov=app/api/auth

**Integration Test:**
# Start server
!uvicorn app.main:app --reload &

# Valid login
!curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
# Expected: {"access_token":"eyJ...","token_type":"bearer"}

# Invalid password
!curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"wrong"}'
# Expected: 401 Unauthorized

# Use token to access protected endpoint
!curl http://localhost:8000/users/me \
  -H "Authorization: Bearer eyJ..."
# Expected: User data

**Full Test Suite:**
!pytest tests/ -v  # All tests must pass
```

**Ventajas:**
- ✅ Context claro (qué archivos leer)
- ✅ Modelos especificados (campos + tipos)
- ✅ Tests exhaustivos (6 escenarios)
- ✅ Validation completa (types + tests + manual)
- ✅ Orden claro (models → service → endpoint → middleware → tests)

**Resultado esperado:**
- IA sigue el plan exactamente
- Código consistente con CLAUDE.md
- Tests con cobertura completa
- Validación exhaustiva
- **Code acceptance: ~88%**

---

## 🛠️ Cómo Usar Estos Templates

### En /plan Command

```markdown
# .claude/commands/plan.md

Feature to plan: $1

## Step 1: Choose Template
Based on feature type:
- API endpoint → Use Template 1
- Frontend component → Use Template 2
- Database change → Use Template 3
- Bug fix → Use Template 4
- Refactoring → Use Template 5

## Step 2: Fill Template
Copy template from ai-project-playbook/03-roadmap/plan-templates.md

Fill in:
- CONTEXT REFERENCES (read existing files first)
- IMPLEMENTATION PLAN (customize to feature)
- STEP-BY-STEP TASKS (specific to this feature)
- VALIDATION COMMANDS (specific tests)

## Step 3: Output Plan
Save plan to: plans/[feature-name].md
```

---

### En Prompts Directos

```
Planifica la implementación de [feature].

Usa el template de "New API Endpoint" de ai-project-playbook/03-roadmap/plan-templates.md

Requisitos específicos:
- [Detalle 1]
- [Detalle 2]

Guarda el plan en: plans/[feature].md
```

---

## 🎯 Best Practices

### 1. Siempre Empieza con CONTEXT REFERENCES

**❌ Malo:**
```markdown
## STEP-BY-STEP TASKS
1. Create app/api/users.py
```

**✅ Bueno:**
```markdown
## CONTEXT REFERENCES
- Read: CLAUDE.md
- Read: app/models/user.py
- Pattern: Follow app/api/products.py:15-40

## STEP-BY-STEP TASKS
1. Create app/api/users.py (following products.py pattern)
```

**Por qué:** Sin context, la IA inventa estructuras inconsistentes.

---

### 2. Especifica Tests ANTES de Validation Commands

**❌ Malo:**
```markdown
## STEP-BY-STEP TASKS
1. Create endpoint
2. Run tests

## VALIDATION COMMANDS
!pytest tests/
```

**✅ Bueno:**
```markdown
## STEP-BY-STEP TASKS
1. Create endpoint
2. Create tests/test_endpoint.py
   - test_success()
   - test_validation_error()
   - test_not_found()

## VALIDATION COMMANDS
!pytest tests/test_endpoint.py -v
```

**Por qué:** La IA necesita saber QUÉ tests escribir, no solo "escribir tests".

---

### 3. Incluye Expected Output en Validation

**❌ Malo:**
```markdown
!curl http://localhost:8000/users
```

**✅ Bueno:**
```markdown
!curl http://localhost:8000/users
# Expected: [{"id":1,"name":"John"},{"id":2,"name":"Jane"}]
```

**Por qué:** Sin expected output, la IA no puede validar si el resultado es correcto.

---

### 4. Agrupa Tasks en Phases Lógicas

**❌ Malo:**
```markdown
1. Create model
2. Create test
3. Create service
4. Create endpoint
5. Create another test
```

**✅ Bueno:**
```markdown
**Phase 1: Data Layer**
1. Create model
2. Create service

**Phase 2: API Layer**
3. Create endpoint

**Phase 3: Tests**
4. Create model tests
5. Create service tests
6. Create endpoint tests
```

**Por qué:** Phases muestran dependencias y facilitan debugging.

---

## 🚨 Errores Comunes

### Error 1: Plan Demasiado Vago

**Síntoma:**
```markdown
1. Implementar autenticación
2. Agregar tests
```

**Fix:**
```markdown
1. Create app/models/auth.py
   - LoginRequest (email: EmailStr, password: str)
   - LoginResponse (access_token: str, token_type: str)

2. Create app/services/auth_service.py
   - hash_password(password: str) -> str
   - verify_password(plain: str, hashed: str) -> bool

3. Create tests/test_auth.py
   - test_login_success()
   - test_login_invalid_credentials()
```

---

### Error 2: Olvidar Context References

**Síntoma:**
La IA crea código inconsistente con el resto del proyecto.

**Fix:**
Siempre incluir:
```markdown
## CONTEXT REFERENCES
- Read: CLAUDE.md
- Read: [archivo relevante existente]
- Pattern: Follow [patrón del proyecto]
```

---

### Error 3: Validation Incompleta

**Síntoma:**
```markdown
## VALIDATION COMMANDS
!pytest tests/
```

**Fix:**
```markdown
## VALIDATION COMMANDS
!mypy app/ --strict
!pytest tests/test_[feature].py -v --cov=app/[module]
!curl [manual test] # Expected: [output]
!pytest tests/ -v  # Full suite
```

---

## 📚 Referencias

**Files relacionados:**
- `slash-commands.md` - Cómo ejecutar estos planes con /plan y /execute
- `planning-prompts.md` - Prompts reutilizables para generar planes
- `templates/plan-template.md` - Template en blanco listo para copiar

**External:**
- PIV Loop framework (00-overview/quick-start.md)
- CLAUDE.md creation guide (02-planning/claude-md-creation.md)

---

**🎯 Remember: Un plan estructurado es la diferencia entre 30% y 88% code acceptance.**

**El tiempo invertido en planning se recupera 10x en implementation. 🚀**
