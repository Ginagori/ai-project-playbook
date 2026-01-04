# Meta-Reasoning - Detectar Scope Creep

**Cómo detectar y prevenir scope creep en AI-generated plans**

---

## 🎯 Concepto

**Meta-reasoning = Razonar sobre el razonamiento**

La AI puede generar plans muy largos sin darse cuenta de scope creep. Tú necesitas detectarlo ANTES de implementar.

---

## 🚨 Warning Signals

### Signal #1: Plan Length

**Regla de oro:**
- **200-400 líneas:** Feature bien scoped ✅
- **400-800 líneas:** Feature complejo pero manejable ⚠️
- **800-1,500 líneas:** Scope creep probable 🚨
- **1,500+ líneas:** STOP - Scope creep confirmed 🛑

**Ejemplo del curso (Módulo 5):**
- Plan inicial: 1,700 líneas 🚨
- Después de meta-reasoning: Dividir en 3 features

### Signal #2: Número de Files

**Healthy feature:**
- 3-8 archivos modificados ✅

**Scope creep:**
- 15+ archivos modificados 🚨
- Tocando 3+ carpetas diferentes 🚨

### Signal #3: Dependencias No Planeadas

**Red flag:**
Plan dice "Also need to refactor X, update Y, migrate Z"

**Solución:**
Separate features:
- Feature A: Original request
- Feature B: Refactor X (separate PR)
- Feature C: Migrate Z (separate PR)

---

## 🔍 Meta-Reasoning Process

### Step 1: Generate Initial Plan

```
Prompt: "Create plan to add email notifications"

Claude generates 1,200 line plan including:
- Email service setup
- Template system
- Queue system
- Analytics tracking
- Admin dashboard for emails
```

### Step 2: Meta-Reasoning Check

**Prompt:**
```
Before implementing, analyze this plan:

1. How many files will be modified?
2. How many new dependencies?
3. Does this touch multiple domains? (auth, billing, etc.)
4. Can this be split into smaller features?
5. What's the MINIMUM implementation?

Be brutally honest. If scope is too large, suggest split.
```

**Claude output:**
```
Analysis:
- Files: 23 (🚨 Too many)
- Dependencies: 4 new packages
- Domains: Email, Queue, Analytics, Admin UI
- **Recommendation: SPLIT**

Suggested approach:
1. Phase 1: Basic email sending (SendGrid integration only)
   - 4 files, 1 dependency, 200 lines
   - Delivers core value

2. Phase 2: Template system (separate PR)
   - 6 files, 300 lines

3. Phase 3: Analytics (separate PR)
   - 8 files, 400 lines
```

### Step 3: Approve Minimal Scope

```
Prompt: "Implement Phase 1 only. Create plan for basic email sending."

Claude generates 250-line focused plan ✅
```

---

## 🛠️ Research-First Approach

**Anti-pattern:**
```
User: "Add AI chat"
Claude: Immediately generates massive plan
```

**Better pattern:**
```
User: "Add AI chat"

Claude: "Before planning, let me research:
1. What chat libraries do we already use?
2. What AI provider do you prefer?
3. Do you have existing message storage?
4. What's the MVP feature set?"

[Research phase: 10 minutes]

Claude: "Based on research, I recommend:
- Use existing WebSocket setup
- OpenAI API (you already have key)
- Store in current messages table
- MVP: Text chat only (no files/images yet)

This is 300-line implementation. Want me to proceed?"
```

**Key:** Research reduces unknowns → Better scoped plans

---

## 📊 Plan Quality Metrics

**High-quality plan indicators:**
- **Focused:** Single responsibility
- **Testable:** Clear validation steps
- **Incremental:** Can be deployed independently
- **Reversible:** Easy to rollback

**Low-quality plan (scope creep):**
- **Sprawling:** Touches unrelated systems
- **Vague:** "Also improve performance"
- **All-or-nothing:** Can't deploy partially
- **Risky:** Massive changes without safety net

---

## 🎯 Ejemplo Real (Curso Módulo 5)

### Paddy Obsidian Agent

**Initial scope:** AI agent for Obsidian notes

**Plan length:** 1,700 lines 🚨

**Meta-reasoning question:**
"Is this plan too large? Should we split it?"

**Answer:**
YES. Split into:
1. Core agent (query vault) - 500 lines
2. Advanced features (note creation) - 600 lines
3. UI improvements - 400 lines

**Result:**
3 separate PRs instead of 1 massive change ✅

---

## 🔄 Meta-Reasoning Prompts

### Prompt 1: Scope Check
```
Analyze this plan. Is scope appropriate for single PR?

Count:
- Files modified
- New dependencies
- Domains touched

If >10 files or >800 lines, suggest split.
```

### Prompt 2: MVP Definition
```
What's the MINIMUM implementation that delivers value?

Exclude:
- "Nice to have" features
- Future optimizations
- Polish/UX improvements

Focus on core functionality only.
```

### Prompt 3: Research Gaps
```
Before implementing, what do we need to research?

List unknowns:
- Existing code we should leverage
- Libraries/patterns already in use
- Database schema constraints
- API limitations

Let's research these BEFORE planning.
```

---

## 🎓 Key Takeaways

1. **Plan length = Scope indicator** - >800 lines = probable creep
2. **Meta-reasoning BEFORE implementing** - Saves weeks of work
3. **Research-first approach** - Reduces unknowns, better plans
4. **Split large features** - Multiple small PRs > 1 massive PR
5. **MVP mindset** - What's MINIMUM to deliver value?

---

**Rule of thumb:** If plan feels overwhelming, it probably is. Meta-reason before coding.
