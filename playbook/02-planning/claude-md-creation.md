# 📝 CLAUDE.md Creation - Guía Completa

**El archivo más importante de tu proyecto**

## ¿Qué es CLAUDE.md?

El "manual de instrucciones" que la IA lee AUTOMÁTICAMENTE en cada prompt.

**Sin CLAUDE.md:** Repetir reglas en cada prompt
**Con CLAUDE.md:** AI conoce tus reglas desde el inicio

## Las 6 Secciones Esenciales

### 1. Core Principles
Valores fundamentales non-negotiable.

Ejemplo:
```markdown
## Core Principles
- TYPE SAFETY: Todo tiene tipos explícitos
- KISS: Keep It Simple
- YAGNI: You Ain't Gonna Need It
- Tests BEFORE merge
```

### 2. Tech Stack
Framework, lenguaje, versiones, herramientas.

Ejemplo:
```markdown
## Tech Stack

**Backend:**
- Python 3.13
- FastAPI 0.104+
- PostgreSQL 16
- SQLAlchemy 2.0
- Pydantic 2.0

**Frontend:**
- React 18
- TypeScript 5
- Vite 5
- Tailwind CSS

**Tools:**
- Package manager: UV
- Formatter: Black + Prettier
- Linter: Ruff + ESLint
```

### 3. Architecture
Patrón arquitectónico del proyecto.

Ejemplo:
```markdown
## Architecture

Pattern: Vertical Slice Architecture

app/
├── api/          # HTTP layer
├── models/       # Data models
├── services/     # Business logic
└── repositories/ # Data access

Cada feature es un "slice" vertical que toca todas las capas.
```

### 4. Code Style
Convenciones de naming, estructura, documentación.

Ejemplo:
```markdown
## Code Style

**Python:**
- Functions: snake_case
- Classes: PascalCase
- Constants: UPPER_SNAKE_CASE
- Line length: 88 chars (Black default)
- Docstrings: Google style

**TypeScript:**
- Functions: camelCase
- Components: PascalCase
- Files: kebab-case.tsx
- Max line: 100 chars
```

### 5. Testing
Frameworks, estructura, patterns.

Ejemplo:
```markdown
## Testing

**Backend:**
- Framework: pytest
- Structure: tests/ mirrors app/
- Coverage target: 80%+
- Run: `pytest tests/ -v --cov=app`

**Patterns:**
- Use fixtures for common setup
- One test file per module
- Test naming: test_[function]_[scenario]
```

### 6. Common Patterns
Cómo hacer tareas frecuentes en ESTE proyecto.

Ejemplo:
```markdown
## Common Patterns

### New API Endpoint
1. Create model in app/models/
2. Create service in app/services/
3. Create endpoint in app/api/
4. Write tests in tests/
5. Run validation

### Error Handling
```python
from app.models.error import ErrorResponse

@app.get("/users/{id}")
def get_user(id: int):
    try:
        user = user_service.get(id)
        if not user:
            raise HTTPException(404, "User not found")
        return user
    except ValueError as e:
        raise HTTPException(400, str(e))
```
```

## Templates por Tech Stack

### FastAPI + React Template
Ver: `templates/CLAUDE.md.template`

### Django + Vue Template
Adaptación de template base con Django-specific patterns

## Siguiente Paso

Después de crear CLAUDE.md → Primer PIV Loop

Ver: `00-overview/quick-start.md`
