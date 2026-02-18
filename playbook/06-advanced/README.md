# Advanced Topics - AI Project Playbook

**Técnicas avanzadas para casos especiales y optimización**

---

## 📋 Overview

Esta sección cubre temas avanzados que NO todos los proyectos necesitan, pero son críticos en casos específicos.

### Cuándo Usar Esta Sección

- ✅ Migración desde no-code tools (Lovable, v0, Bolt)
- ✅ Separar monolito en frontend/backend
- ✅ Optimizar RAG para producción
- ✅ Setup persistent memory (Archon)
- ✅ Meta-reasoning para detectar scope creep

❌ **NO leas esto primero** - Empieza con 00-overview, 01-discovery, etc.

---

## 📂 Contenido

### 1. **[lovable-to-production.md](./lovable-to-production.md)**
**Migrar proyectos desde Lovable/v0 a producción**

- Exportar código desde Lovable
- Audit y cleanup de código generado
- Extraer design system
- Deployment a infraestructura real

**Cuándo usar:** Construiste MVP en Lovable, ahora necesitas control total.

---

### 2. **[design-system-creation.md](./design-system-creation.md)**
**Crear design system desde código existente**

- Component library setup
- Theming y design tokens
- Storybook integration
- Testing de componentes

**Cuándo usar:** Tienes 50+ componentes sin consistencia, necesitas design system.

---

### 3. **[frontend-backend-split.md](./frontend-backend-split.md)**
**Separar monolito en frontend + backend**

- API design (REST vs GraphQL)
- Authentication flow
- State management
- Migration strategy

**Cuándo usar:** Tienes fullstack monolito, necesitas escalar frontend y backend independientemente.

---

### 4. **[context-engineering.md](./context-engineering.md)**
**Advanced RAG patterns para producción**

- Semantic caching
- Context compression techniques
- Vector DB optimization
- Production RAG architecture

**Cuándo usar:** Aplicación con AI/RAG, necesitas optimizar costos y latencia.

---

### 5. **[archon-architecture.md](./archon-architecture.md)**
**MCP Knowledge Management con Archon**

- Qué es Archon (Command Center MCP)
- Knowledge + Task Management setup
- Persistent memory entre sesiones
- Cuándo usar vs simple CLAUDE.md

**Cuándo usar:** Proyecto complejo con múltiples agentes, necesitas memoria persistente.

---

### 6. **[meta-reasoning.md](./meta-reasoning.md)**
**Detectar y prevenir scope creep**

- Plan length como warning signal
- Research-first approach
- Ajustar approach antes de implementar
- Ejemplos del curso (Paddy agent)

**Cuándo usar:** Plans salen muy largos (>1,000 líneas), sospechas scope creep.

---

### 7. **[autonomous-agent-architecture.md](./autonomous-agent-architecture.md)**
**Arquitectura completa para agentes autónomos de producción**

- Triple-Layer Soul (Core + Identity + Learned Preferences)
- 4 Engines (Soul, Memory, Router, Heartbeat)
- Modelo de seguridad (hash verification, prompt injection defense)
- Patrón de adaptación por dominio

**Cuándo usar:** Construyes un agente AI que necesita identidad persistente, memoria, routing inteligente y comportamiento proactivo.

---

## 🎯 Cómo Usar Esta Sección

### Approach 1: Problem-Driven
**Tienes problema específico → Busca guía correspondiente**

```
Problema: "Construí en Lovable, necesito deployment real"
→ Lee: lovable-to-production.md

Problema: "Componentes inconsistentes, no hay design system"
→ Lee: design-system-creation.md

Problema: "RAG muy lento, embeddings costosos"
→ Lee: context-engineering.md
```

### Approach 2: Learning-Driven
**Leer todas las guías para expandir conocimiento**

Orden recomendado:
1. lovable-to-production.md (común)
2. frontend-backend-split.md (arquitectura)
3. design-system-creation.md (frontend)
4. context-engineering.md (AI/RAG)
5. meta-reasoning.md (planning)
6. archon-architecture.md (avanzado)

---

## ⚠️ Advertencias

### No Sobre-Optimices Prematuramente

**Escenario común:**
- Usuario: "Voy a implementar semantic caching desde día 1"
- Realidad: Tienes 0 usuarios, caching no importa aún

**Mejor approach:**
1. Construye MVP simple
2. Mide performance con usuarios reales
3. Identifica bottlenecks
4. ENTONCES lee guía avanzada correspondiente

### No Uses Todo al Mismo Tiempo

**❌ Mal:**
- Leer las 6 guías
- Implementar TODO al mismo tiempo
- Over-engineered desde día 1

**✅ Bien:**
- Implementar una técnica cuando la NECESITES
- Medir impacto
- Iterar

---

## 💡 Casos de Uso Comunes

### Caso 1: Startup con MVP en Lovable

**Situación:**
- App funcional en Lovable
- 50 usuarios, feedback positivo
- Necesitas features que Lovable no soporta
- Quieres deployment real (no Lovable hosting)

**Guías recomendadas:**
1. lovable-to-production.md (export código)
2. design-system-creation.md (extraer components)
3. 05-deployment/mvp-deployment.md (deploy)

**Tiempo:** 1-2 semanas

---

### Caso 2: SaaS con RAG Lento

**Situación:**
- Aplicación con RAG funcionando
- >500 usuarios
- Costos de embeddings muy altos
- Latencia p95 >3 segundos

**Guías recomendadas:**
1. context-engineering.md (optimize RAG)
2. 05-deployment/growth-deployment.md (scale infra)

**Tiempo:** 3-5 días

---

### Caso 3: Monolito que Necesita Escalar

**Situación:**
- Fullstack app en un solo repo
- Frontend y backend deployados juntos
- Necesitas escalar backend independientemente
- Team creciendo (frontend vs backend devs)

**Guías recomendadas:**
1. frontend-backend-split.md (separar)
2. 05-deployment/growth-deployment.md (deploy separado)

**Tiempo:** 1-2 semanas

---

### Caso 4: Proyecto Complejo con Múltiples Agentes

**Situación:**
- Aplicación con 5+ AI agents
- Necesitas memoria persistente entre sesiones
- Quieres task management automático
- Team de 3+ developers

**Guías recomendadas:**
1. archon-architecture.md (MCP setup)
2. context-engineering.md (optimize agents)
3. meta-reasoning.md (prevent scope creep)

**Tiempo:** 2-3 semanas

---

## 🎓 Key Takeaways

1. **Advanced ≠ Mejor** - Solo usa técnicas avanzadas cuando las NECESITES
2. **Problem-driven** - Identifica problema primero, luego busca solución
3. **Measure first** - Mide performance antes de optimizar
4. **One at a time** - Implementa una técnica, mide impacto, itera
5. **ROI clear** - Asegura que tiempo invertido justifica beneficio

---

## 🔗 Secciones Relacionadas

- **[00-overview/](../00-overview/)** - Empieza aquí si eres nuevo
- **[04-implementation/](../04-implementation/)** - PIV Loop basics
- **[05-deployment/](../05-deployment/)** - Deployment guides
- **[examples/](../examples/)** - Proyectos ejemplo completos

---

**Recuerda:** Lo avanzado solo importa cuando lo simple ya no es suficiente. Empieza simple, evoluciona cuando sea necesario.
