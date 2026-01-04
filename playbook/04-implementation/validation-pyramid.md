# 🔺 Validation Pyramid - 5 Niveles de Calidad

La diferencia entre 30% y 88% code acceptance.

## Los 5 Niveles

### Level 1: Syntax & Formatting
```bash
black app/
ruff check app/
```

**Debe pasar:** 0 errors

### Level 2: Type Safety
```bash
mypy app/ --strict
```

**Debe pasar:** 0 type errors

### Level 3: Unit Tests
```bash
pytest tests/ -v --cov=app
```

**Debe pasar:** All tests, 80%+ coverage

### Level 4: Integration Tests
```bash
pytest tests/ -m integration
```

**Debe pasar:** Full flows work

### Level 5: Manual Testing + Code Review
- Probar manualmente en browser/API
- Code review checklist
- Security checks

## Workflow

```
Code → L1 → L2 → L3 → L4 → L5 → Merge
        ↓
     FAIL → Fix → Revalidate
```

**NO skipes niveles**
**NO merges con validation failing**

## Automation

Ver: `templates/validate-command.md` para automatizar L1-L4

## Siguiente Paso

Ver: `piv-loop-execution.md`
