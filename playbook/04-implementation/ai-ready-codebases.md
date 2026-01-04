# Los 7 Pilares de Codebases AI-Ready

> **Fuente:** Artículo de Rasmus Widing, adaptado para el AI Project Playbook
> **Aplicable a:** Todos los proyectos (MVP → Enterprise)

---

## 💡 La Idea Central

**El éxito con AI coding NO depende de los prompts que escribes, sino de la INFRAESTRUCTURA que construyes.**

El principio fundamental:

> **"El agente NO termina hasta que TODOS los checks estén verdes."**

Esto transforma linting y type checking de "gates pasivos" a un **sistema de feedback activo**. El agente escribe código, corre checks, ve qué falla, lo arregla, y repite - sin intervención humana.

---

## Los 7 Pilares

| # | Pilar | Qué Resuelve |
|---|-------|--------------|
| 1 | **Grep-ability** | Código buscable para que el agente encuentre en vez de inventar |
| 2 | **Glob-ability** | Estructura predecible para navegación eficiente |
| 3 | **Architectural Boundaries** | Límites explícitos que el agente no puede cruzar |
| 4 | **Security & Privacy** | Safety nets automáticos (el agente no piensa en seguridad) |
| 5 | **Testability** | Tests como requisito, no como opción |
| 6 | **Observability** | Logging estructurado y consistente |
| 7 | **Documentation** | Contexto rico para que el agente tome mejores decisiones |

---

## Pilar 1: Grep-ability (Código Buscable)

**Problema:** Los agentes navegan codebases mediante búsqueda. Si tus patrones no son buscables, el agente **inventará** implementaciones en vez de encontrar las reales.

### Reglas Core

| Regla | Por qué |
|-------|---------|
| **Prohibir default exports, usar named exports** | El agente puede buscar `export function createUser` y encontrar exactamente una definición |
| **Usar DTOs tipados explícitos** | En vez de tipos inline, crear definiciones buscables |
| **Tipos de error consistentes** | No esparcir `new Error()`, crear `UserNotFoundError`, `ValidationError`, etc. |
| **Evitar magic strings** | Usar enums o constantes que se puedan buscar |

### Ejemplos

**TypeScript:**
```typescript
// ❌ AI-hostile: Default exports son invisibles a búsqueda
export default function handler(req, res) { ... }

// ✅ AI-friendly: Named exports son grep-ables
export function handleUserRegistration(req: Request, res: Response) { ... }
```

**Python:**
```python
# ❌ AI-hostile: Nombres genéricos, magic strings
def handler(request):
    if request.type == "user":  # Magic string
        return {"status": "ok"}

# ✅ AI-friendly: Nombres explícitos, constantes buscables
from app.constants import RequestType, ResponseStatus

def handle_user_registration(request: Request) -> UserResponse:
    if request.type == RequestType.USER_REGISTRATION:
        return UserResponse(status=ResponseStatus.SUCCESS)
```

---

## Pilar 2: Glob-ability (Estructura Predecible)

**Problema:** Los agentes usan patrones de archivos para navegar. Si tu estructura es caótica, el agente gasta tokens preguntando "¿dónde va esto?"

### Reglas Core

| Regla | Ejemplo |
|-------|---------|
| **Colocalizar por feature, no por tipo** | `users/routes.py`, `users/types.py`, `users/service.py` juntos |
| **Naming estandarizado** | Siempre `types.py`, `enums.py`, `helpers.py`, `service.py`, `test_*.py` |
| **Tests junto al código** | `test_user_service.py` vive junto a `user_service.py` |
| **Imports absolutos** | `from app.users.service import UserService` (no `from ...users.service`) |

### Por Qué Importa

Cuando el agente necesita agregar lógica de autenticación, debería saber **instantáneamente** que debe buscar `auth/service.py` y `auth/types.py` - sin gastar tokens explorando todo el codebase.

---

## Pilar 3: Architectural Boundaries (Límites Explícitos)

**Problema:** Los agentes son TERRIBLES respetando límites implícitos. Felizmente importarán tu database layer en tus API responses si no los detienes.

### Reglas Core

| Regla | Implementación |
|-------|----------------|
| **Prevenir imports cross-layer** | Database layer no puede importar de HTTP layer |
| **Usar allowlists/denylists** | Configurar linter para bloquear `src/database` de importar `src/api` |
| **Dependency injection explícita** | No dejar que agentes creen dependencias ocultas |

### Configuración Ruff (Python/FastAPI)

```toml
[tool.ruff.lint]
select = ["I"]  # Import sorting and organization

[tool.ruff.lint.isort]
sections = ["FUTURE", "STDLIB", "THIRDPARTY", "FIRSTPARTY", "LOCALFOLDER"]
force-single-line = false
force-sort-within-sections = true
```

---

## Pilar 4: Security & Privacy (Safety Nets Automáticos)

**Problema:** Los agentes NO piensan en seguridad. Debes codificarla en sus constraints.

### Reglas Core

| Regla | Ruff Rule |
|-------|-----------|
| **Bloquear secrets hardcodeados** | `S105`, `S106` (flake8-bandit) |
| **Requerir input validation** | Nunca dejar input crudo llegar a business logic |
| **Prohibir funciones peligrosas** | Bloquear `eval()`, `exec()`, y similares |
| **Forzar patterns seguros** | Requerir queries parametrizadas, no concatenación de strings |

### Configuración Ruff

```toml
[tool.ruff.lint]
select = [
    "S",    # flake8-bandit (security)
    "B",    # flake8-bugbear (common pitfalls)
]
ignore = [
    "S311",  # Standard pseudo-random generators (OK for non-crypto)
]
```

---

## Pilar 5: Testability (Tests NO Negociables)

> "Tests are non-negotiable, and AI removes all excuses to not write them." — Simon Willison

### Reglas Core

| Regla | Por qué |
|-------|---------|
| **Tests colocalizados** | `test_user_service.py` vive junto a `user_service.py` |
| **Sin network calls en unit tests** | Usar mocks/fixtures |
| **Assert en comportamiento, no implementación** | Aquí es donde la AI suele fallar |

### ⚠️ El Problema de los Assertions: Los Tests de AI Mienten

**El secreto sucio:** Los tests generados por AI pasan, se ven hermosos, y hacen assertions de completas tonterías.

```python
# ❌ AI-generated assertion (incorrecto pero se ve bien)
def test_calculate_discount():
    result = calculate_discount(price=100, code="SAVE20")
    assert result == 80  # AI adivinó 20% off

# ✅ Human-validated assertion (correcto)
def test_calculate_discount():
    result = calculate_discount(price=100, code="SAVE20")
    assert result == 85  # En realidad es 15% off en nuestro sistema
```

**Por qué pasa:** Los LLMs no conocen tu business logic. Adivinan basándose en naming (`SAVE20` → probablemente 20% off). Se equivocan justo lo suficiente para quemarte en producción.

### Dos Estrategias que Funcionan

1. **Diseña assertions upfront:** Incluye casos de prueba explícitos en tu prompt. "Test que SAVE20 da 15% off, no 20%. Test que descuento no excede precio del producto."

2. **Verifica assertions después:** Deja que AI genere estructura y mocks, pero trata cada assertion como **culpable hasta probar inocencia**. Este es el único lugar donde DEBES permanecer en el loop.

### Configuración Ruff para Tests

```toml
[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = [
    "S101",   # Allow assert in tests
    "ANN",    # Skip type annotations in tests
    "ARG",    # Allow unused arguments in test fixtures
]
```

---

## Pilar 6: Observability (Logging Estructurado)

**Problema:** Los agentes necesitan agregar logging, pero logs no estructurados son ruido.

### Reglas Core

| Regla | Implementación |
|-------|----------------|
| **Solo logging estructurado** | JSON logging con field names consistentes |
| **Log levels estandarizados** | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| **Patrón de namespace híbrido** | Formato `domain.component.action_state` |
| **Incluir contexto** | Siempre loggear `user_id`, `request_id`, `correlation_id` |

### Patrón de Naming de Eventos

**Formato:** `{domain}.{component}.{action}_{state}`

| Evento | Significado |
|--------|-------------|
| `user.registration_started` | Registro de usuario iniciado |
| `product.create_completed` | Producto creado exitosamente |
| `agent.tool.execution_failed` | Ejecución de tool del agente falló |
| `database.connection_initialized` | Conexión a DB establecida |

### Por Qué Este Patrón

- **OpenTelemetry compliant** - Sigue convenciones semánticas 2024-2025
- **AI/LLM parseable** - Estructura jerárquica para pattern recognition
- **Grep-friendly** - Fácil de buscar: `grep "user\."` o `grep "_failed"`
- **Escalable** - Soporta features de agentes: `agent.tool.execution_started`

### Ejemplo de Implementación

```python
import structlog

logger = structlog.get_logger()

def create_user(email: str) -> User:
    logger.info(
        "user.registration_started",
        email=email,
        source="api"
    )

    try:
        user = User.create(email=email)
        logger.info(
            "user.registration_completed",
            user_id=user.id,
            email=email
        )
        return user
    except Exception as e:
        logger.error(
            "user.registration_failed",
            email=email,
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True
        )
        raise
```

---

## Pilar 7: Documentation (Contexto es Rey)

> "Context is King. I'll Say It Again: Context is King." — Rasmus Widing

### Reglas Core

| Regla | Implementación |
|-------|----------------|
| **APIs públicas requieren docstrings** | Usar reglas `D` en Ruff para enforcar |
| **Link a ADRs** | Cuando ignoras una lint rule, explica por qué |
| **README en cada directorio mayor** | Contexto breve sobre el propósito del módulo |
| **Type annotations everywhere** | Usar reglas `ANN` para enforcar |

### Docstrings para Tools vs Funciones

| Tipo | Audiencia | Propósito |
|------|-----------|-----------|
| **Tool docstrings** | AI agent DENTRO de tu app | Instrucciones de cómo usar el tool |
| **Function/API docstrings** | AI agent ESCRIBIENDO tu app | Documentación de la función |

### Configuración Ruff

```toml
[tool.ruff.lint]
select = [
    "D",      # pydocstyle (docstrings)
    "ANN",    # flake8-annotations
]
ignore = [
    "D100",   # Missing docstring in public module (too noisy)
    "D104",   # Missing docstring in public package
]
```

---

## Configuración Completa: Ruff + MyPy + Pyright

Esta es la configuración battle-tested para proyectos FastAPI con typing estricto:

### pyproject.toml

```toml
[tool.ruff]
target-version = "py312"
line-length = 100
exclude = [
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".mypy_cache",
    "alembic",  # Migration files don't need strict linting
]

[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # pyflakes
    "I",      # isort (import sorting)
    "B",      # flake8-bugbear (catch mutable defaults, etc.)
    "C4",     # flake8-comprehensions
    "UP",     # pyupgrade (modernize syntax)
    "ANN",    # flake8-annotations (enforce type hints)
    "S",      # flake8-bandit (security)
    "DTZ",    # flake8-datetimez (timezone-aware datetimes)
    "RUF",    # Ruff-specific rules
    "ARG",    # flake8-unused-arguments
    "PTH",    # flake8-use-pathlib (prefer Path over os.path)
]

ignore = [
    "B008",   # FastAPI uses Depends() in function defaults
    "S311",   # Standard random is fine for non-crypto use
    "E501",   # Line too long (formatter handles this)
]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101", "ANN", "ARG001", "D"]
"__init__.py" = ["F401"]  # Allow unused imports in package init
"scripts/**/*.py" = ["T201"]  # Allow print in scripts

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
line-ending = "auto"

[tool.ruff.lint.isort]
known-first-party = ["app"]

# ========== MYPY ==========
[tool.mypy]
python_version = "3.12"
strict = true
show_error_codes = true
warn_unused_ignores = true

# FastAPI compatibility
plugins = ["pydantic.mypy"]

# Practical strictness (not dogmatic)
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = false  # FastAPI decorators aren't typed

[tool.pydantic-mypy]
init_forbid_extra = true
init_typed = true
warn_required_dynamic_aliases = true

# ========== PYRIGHT ==========
[tool.pyright]
include = ["app"]
exclude = [
    "**/__pycache__",
    ".venv",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache"
]

pythonVersion = "3.12"
typeCheckingMode = "strict"

# Report all issues - no escape hatches
reportMissingImports = true
reportMissingTypeStubs = true
reportUnusedImport = true
reportUnusedVariable = true
reportDuplicateImport = true
reportOptionalMemberAccess = true
reportOptionalSubscript = true
reportOptionalCall = true
```

---

## MyPy vs Pyright: Cuándo Usar Cada Uno

| Aspecto | MyPy | Pyright |
|---------|------|---------|
| **Filosofía** | Leniente, pragmático | Estricto, tipo-correcto |
| **Velocidad** | Más lento | Más rápido |
| **Third-party libs** | Más tolerante | Más estricto |
| **Edge cases** | Deja pasar algunos | Los atrapa |

### Cuándo Agregar Pyright

| Escenario | Recomendación |
|-----------|---------------|
| **Sistemas de producción** | ✅ Sí - tipos incorrectos causan runtime failures |
| **Library code** | ✅ Sí - tu código será consumido por otros |
| **Prototipos early-stage** | ❌ No - velocidad importa más |
| **Tools internas** | ❌ No - pragmatismo sobre pedantería |

### Lo que Pyright Atrapa que MyPy No

```python
# Example: Processor type variance
def add_metadata(
    logger: Any,
    method_name: str,
    event_dict: dict[str, Any]  # MyPy: ✅  Pyright: ❌
) -> dict[str, Any]:
    return event_dict

# Pyright error: "dict[str, Any]" is incompatible with "MutableMapping[str, Any]"
```

**Key insight:** Pyright enforza **structural subtyping** más estrictamente. Un `dict` es un `MutableMapping`, pero `MutableMapping` no siempre es un `dict`.

### Workflow Práctico

1. **Durante desarrollo:** Usa MyPy para iteración rápida
2. **Antes de merge:** Agrega Pyright
3. **En CI/CD:** Corre ambos para atrapar issues antes de producción

---

## Pre-commit: Automatización Local

### .pre-commit-config.yaml

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.4
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.13.0
    hooks:
      - id: mypy
        additional_dependencies: [pydantic, structlog]

  - repo: https://github.com/RobertCraigie/pyright-python
    rev: v1.1.365
    hooks:
      - id: pyright
        additional_dependencies: [structlog]
```

### Instalación

```bash
# Con uv
uv tool install pre-commit
pre-commit install

# Correr manualmente
pre-commit run --all-files
```

---

## El Workflow de Desarrollo con AI

### 1. PRPs Ricos en Contexto

Empieza con un PRP (Product Requirements Prompt) que incluya:
- **Goal:** Qué estás construyendo y por qué
- **Technical Context:** Patrones existentes, decisiones de arquitectura
- **Constraints:** Requisitos de seguridad, targets de performance
- **Examples:** Código existente a seguir como patrón

### 2. Deja que el Agente Genere

No esperes perfección en el primer intento. Espera un **buen primer draft** que necesita iteración.

### 3. Loop de Feedback Automatizado

```bash
# El código del agente pasa por checks automáticos
uv run ruff check . --fix
uv run ruff format .
uv run mypy .
uv run pytest

# Opcional: Pyright para type checking más estricto
uv run pyright .
```

El agente ve errores de linting e itera. Tu configuración paga dividendos aquí - errores claros y accionables que el agente puede arreglar automáticamente.

### 4. Human Review: Focus en Lógica

Tu trabajo NO es arreglar formatting o atrapar type hints faltantes - el linter hace eso. Tu trabajo es:

- **Validar test assertions** - ¿Están testeando el comportamiento correcto?
- **Revisar implicaciones de seguridad** - ¿Esto expone datos sensibles?
- **Evaluar fit arquitectónico** - ¿Esto pertenece aquí?

### 5. Ship con Confianza

Cuando tests pasan y linters están verdes, tienes confianza. El trabajo tedioso está manejado; te enfocaste en decisiones de alto impacto.

---

## Presentación de Errores para AI

**Insight del equipo de Aider:** Los LLMs son TERRIBLES con números de línea. Cometen errores off-by-one constantemente.

### Solución: Contexto AST-aware

```
❌ Malo (solo número de línea):
./app/users.py:42: error: Missing type annotation

✅ Bueno (context-rich):
./app/users.py: In function 'create_user':
    def create_user(email, password):
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^
    error: Missing type annotation for parameters
```

Muestra el error dentro de su boundary semántico (función, clase, o módulo). Esto mejora dramáticamente la precisión del fix.

---

## Roadmap de Implementación

No necesitas implementar los 7 pilares en el día 1.

### Semana 1: Fundamentos

- [ ] Agregar Ruff con reglas `E`, `F`, `I` (errors, imports, sorting)
- [ ] Setup pre-commit hooks
- [ ] Instalar uv para dependency management

### Semanas 2-3: Seguridad y Tipos

- [ ] Habilitar reglas `B`, `S` (bugbear, security)
- [ ] Agregar MyPy con strict mode básico
- [ ] Estandarizar convenciones de naming de archivos

### Semana 4+: Documentación y Observability

- [ ] Habilitar reglas `ANN`, `D` (annotations, docstrings)
- [ ] Escribir primeros patrones de logging estructurado
- [ ] Crear ADRs para decisiones arquitectónicas

### Más Adelante: Refinamiento Continuo

- [ ] Agregar Pyright para dual-layer type checking (sistemas de producción)
- [ ] Agregar lint rules específicas del proyecto
- [ ] Construir tooling custom para presentar errores a AI
- [ ] Compartir configuración across team projects

---

## Principios Atemporales

Estos NO son solo "best practices para AI coding" - son principios atemporales que funcionan sin importar qué AI coding tool uses:

| # | Principio | Implementación |
|---|-----------|----------------|
| 1 | **Patrones buscables** | Named exports, explicit types, naming consistente |
| 2 | **Codifica constraints como lints** | No confíes en el juicio del agente para seguridad o arquitectura |
| 3 | **Automatiza feedback loops** | Deja que agentes se auto-corrijan sin intervención humana |
| 4 | **Estructura de tests vs assertions** | AI genera estructura; tú validas lógica |
| 5 | **Estructurado > no estructurado** | Logging, errors, types - estructura habilita automatización |
| 6 | **Contexto es moneda** | Documentación rica y type hints multiplican efectividad del agente |
| 7 | **Green checks = done** | Haz de esto tu definición de completitud |

---

## Conclusión

> "Infrastructure Scales, Vibes Don't" — Rasmus Widing

La promesa de AI coding NO es que dejamos de preocuparnos por calidad de código - es que podemos **systematically enforce quality at scale**.

Tus archivos de configuración - `pyproject.toml`, `.pre-commit-config.yaml` - son el scaffolding que permite a los agentes AI construir sistemas confiables en vez de prototipos frágiles.

**El objetivo no es constrainer a la AI, sino darle rieles claros para correr a máxima velocidad.**
