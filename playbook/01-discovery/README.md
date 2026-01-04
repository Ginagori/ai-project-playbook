# 🔍 Discovery - Fase de Descubrimiento del Proyecto

**La fase más importante que la mayoría de developers se salta.**

---

## 🎯 ¿Qué es Discovery?

Discovery es el proceso de **entender profundamente el problema ANTES de escribir código**.

**No es:**
- ❌ "Tengo una idea, voy a codear"
- ❌ "El PM me dio specs, empiezo ya"  
- ❌ "Copio este tutorial y lo adapto"

**Es:**
- ✅ Hacer las preguntas correctas sobre el problema
- ✅ Entender usuarios, contexto, y constraints
- ✅ Elegir el tech stack apropiado (no el de moda)
- ✅ Validar suposiciones antes de invertir semanas de desarrollo

---

## 📊 El Costo de Saltar Discovery

**30 minutos de Discovery ahorraron 2 semanas de desarrollo.**

Saltar Discovery → 8 semanas con 50% en refactors
Con Discovery → 6 semanas sin refactors arquitectónicos

---

## 🧠 El Framework de Discovery (30 minutos)

### Fase 1: PROBLEM DISCOVERY (15 min)
1. ¿Qué problema resuelve?
2. ¿Para quién es?
3. ¿Cómo lo resuelven hoy?
4. ¿Por qué lo existente no funciona?
5. ¿Cuál es el éxito?

### Fase 2: TECHNICAL DISCOVERY (10 min)
1. ¿Cuántos usuarios?
2. ¿Escala de datos?
3. ¿Multi-tenancy?
4. ¿Transacciones ACID?
5. ¿Integraciones externas?
6. ¿Budget?
7. ¿Team skills?

### Fase 3: TECH STACK SELECTION (5 min)
Basado en Fase 1+2, elegir stack apropiado.

**Ver:** `tech-stack-selector.md` en esta carpeta

---

## 📋 Discovery Checklist

**Antes de escribir código:**

- [ ] Problem statement de 1 párrafo
- [ ] Usuarios identificados
- [ ] Tech stack elegido con rationale
- [ ] 3 riesgos identificados
- [ ] MVP scope definido
- [ ] Métricas de éxito

---

## 🎨 Métodos de Discovery

### Método 1: Conversacional con AI (10-15 min)

```
Actúa como Product Manager.
Hazme preguntas de Discovery.
UNA pregunta a la vez.
Al final, propón tech stack.
```

### Método 2: Questionnaire (30-45 min)
Ver: `discovery-questions.md`

---

## 📊 Discovery Document Template

```markdown
# Discovery: [PROJECT]

## 1. PROBLEM
[1 párrafo]

## 2. USERS
- Primary: [quién]

## 3. TECH STACK
- Backend: [tech] - Rationale: [...]
- Frontend: [tech] - Rationale: [...]

## 4. RISKS
1. [Risk]: Mitigation: [...]

## 5. MVP
- [Feature 1]
- [Feature 2]
```

Guardar en: `my_workspace/projects/[name]/DISCOVERY.md`

---

## ✅ Definition of Done

- [ ] Discovery Document completo
- [ ] Tech stack con rationale
- [ ] Usuarios conocidos
- [ ] MVP scope definido

→ Avanzar a Planning (crear CLAUDE.md)

---

**🎯 30 minutos ahorra semanas de refactoring. 🚀**

**Ver también:**
- `discovery-questions.md` - Cuestionario completo
- `tech-stack-selector.md` - Decision tree
- `../02-planning/claude-md-creation.md` - Siguiente paso
