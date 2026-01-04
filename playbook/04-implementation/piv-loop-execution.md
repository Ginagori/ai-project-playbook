# 🔄 PIV Loop Execution - Paso a Paso

Cómo ejecutar un ciclo completo de PIV.

## El Loop Completo

```
PLAN → IMPLEMENT → VALIDATE → (Pass? Merge : Iterate)
```

## Fase P: Planning

### Inputs
- Feature request
- CLAUDE.md
- Existing codebase

### Process
1. Read CLAUDE.md
2. Explore related code
3. Create structured plan

### Output
- Plan document (CONTEXT → PLAN → TASKS → VALIDATION)

## Fase I: Implementation

### Process
1. Follow plan step-by-step
2. Implement ALL components (no TODOs)
3. Write tests as you go

### Red Flags
- Skipping steps in plan
- Leaving TODOs
- Not running tests

## Fase V: Validation

### Process
1. Run Level 1-5 validation
2. Document results
3. If FAIL → Fix and revalidate

### Output
- Validation report (PASS/FAIL per level)

## Iteration

If validation fails:
- Analyze root cause
- Update code OR plan
- Revalidate

## Example Full Loop

Ver: `00-overview/quick-start.md` para primer PIV Loop

## Tools

- `/plan` - Create plan
- `/execute` - Implement
- `/validate` - Run validation pyramid

Ver: `03-roadmap/slash-commands.md`
