# Patrones de Arquitectura para AI Coding

> **Fuente:** Artículo de Rasmus Widing, adaptado para el AI Project Playbook
> **Aplicable a:** Todos los proyectos (MVP → Enterprise)

---

## 💡 La Idea Central

**El patrón de arquitectura que elijas tiene MÁS impacto en la productividad con AI que los prompts que escribes.**

Equipos con el mismo AI coding assistant producen resultados dramáticamente diferentes. La diferencia: la arquitectura.

---

## El Costo Oculto de la Arquitectura Tradicional

> "La arquitectura layered quema tokens como loco - es como correr un generador diesel para cargar tu Tesla."

Cuando un agente AI necesita entender cómo agregar un producto al catálogo en arquitectura layered tradicional:

```
controllers/product_controller.py     # 1. Entry point
services/product_service.py           # 2. Business logic
repositories/product_repository.py    # 3. Data access
models/product.py                     # 4. Data model
validators/product_validator.py       # 5. Validation rules
dto/product_dto.py                    # 6. Data transfer objects
```

**6 archivos** en **6 directorios diferentes** para entender UNA feature. Cada context switch cuesta tokens. El agente gasta 60-70% de su tiempo navegando tu arquitectura.

---

## Matriz Comparativa de Patrones

| Patrón | AI-Friendliness | Token Efficiency | Maintainability | Complexity |
|--------|-----------------|------------------|-----------------|------------|
| **Vertical Slice Architecture** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **Feature Folders** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **Modular Monolith** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Clean/Layered Architecture** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Microservices** | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Single File / Monolith** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐ |

### Definiciones

- **AI-Friendliness:** ¿Qué tan fácil puede un agente entender y modificar código?
- **Token Efficiency:** ¿Cuántos tokens se consumen para operaciones típicas?
- **Maintainability:** ¿Qué tan fácil es mantener a largo plazo para humanos?
- **Complexity:** ¿Cuánto overhead para implementar y operar? (Menos estrellas = menos complejo)

---

## Patrón 1: Vertical Slice Architecture (El Ganador)

**Qué es:** Organizar código por feature (slices verticales) en vez de por layer técnico (capas horizontales). Cada slice contiene TODO lo necesario para esa feature.

### Estructura

```
app/
├── products/
│   ├── routes.py           # FastAPI endpoints
│   ├── service.py          # Business logic
│   ├── repository.py       # Database access
│   ├── types.py            # Models, DTOs, schemas
│   ├── validators.py       # Input validation
│   ├── test_routes.py      # Endpoint tests
│   ├── test_service.py     # Business logic tests
│   └── README.md           # Feature documentation
├── inventory/
│   ├── routes.py
│   ├── service.py
│   ├── types.py
│   └── ...
└── categories/
    └── ...
```

### Por Qué Gana para AI Coding

| Beneficio | Descripción |
|-----------|-------------|
| **Context isolation** | Agente solo necesita entender un directorio de feature |
| **Token efficiency** | Todo el código relacionado está co-localizado |
| **High cohesion** | Todo para productos vive en `products/` |
| **Grep-ability** | Buscar "product" encuentra todo en un lugar |
| **Parallel development** | Diferentes agentes trabajan en diferentes features sin conflictos |

### Caso Real

> Un equipo cambió de layered a VSA. Su productividad con AI aumentó 3×. No porque el agente se hizo más inteligente - porque dejó de gastar tokens navegando entre layers.

### Trade-offs

- Algo de duplicación de código entre slices (pero duplicación es más barata que coupling)
- Requiere disciplina para mantener boundaries
- Infraestructura compartida (auth, logging, database) vive en `common/` o `shared/`

### Cuándo Usar

- ✅ Nuevas aplicaciones
- ✅ Refactoring de apps medianas a grandes
- ✅ Trabajo extensivo con AI agents

---

## Patrón 2: Feature Folders / Package by Feature

**Qué es:** Similar a VSA, pero típicamente menos estricto. Organiza por feature pero puede compartir más código de infraestructura.

### Estructura

```
app/
├── features/
│   ├── product_catalog/
│   │   ├── api.py
│   │   ├── models.py
│   │   ├── business_logic.py
│   │   └── tests.py
│   └── inventory_management/
│       └── ...
├── shared/
│   ├── database.py
│   ├── auth.py
│   └── ...
```

### Por Qué Funciona

- Alta cohesión dentro de features
- Navegación reducida
- Boundaries naturales
- Fácil de extraer a microservices después

### Trade-offs

- Menos prescriptivo que VSA
- Puede llevar a "junk drawer" shared folders
- Boundaries a veces poco claros

### Cuándo Usar

- ✅ Equipos transicionando desde layered
- ✅ Proyectos con mucha infraestructura compartida
- ✅ Equipos nuevos en AI coding

---

## Patrón 3: Modular Monolith

**Qué es:** Unidad deployable única organizada en módulos loosely coupled con interfaces explícitas.

### Estructura

```
app/
├── modules/
│   ├── products/
│   │   ├── domain/         # Business logic
│   │   ├── application/    # Use cases
│   │   ├── infrastructure/ # DB, external APIs
│   │   └── interface/      # HTTP, CLI
│   ├── inventory/
│   └── ...
```

### Por Qué Funciona

- Boundaries de módulo claros
- Interfaces explícitas entre módulos
- Bueno para codebases grandes
- Single deployment (más simple que microservices)

### Trade-offs

- Más complejo que VSA o feature folders
- Todavía requiere navegación dentro de módulos
- Más difícil para AI entender dependencias entre módulos

### Cuándo Usar

- ✅ Aplicaciones grandes (>50K líneas)
- ✅ Equipos con fuerte disciplina arquitectónica
- ✅ Necesidad de boundaries estrictos

---

## Patrón 4: Clean/Layered Architecture

**Qué es:** Layers horizontales tradicionales - controllers, services, repositories, models. El enfoque MVC/N-tier.

### Estructura

```
app/
├── controllers/     # HTTP handlers
├── services/        # Business logic
├── repositories/    # Data access
├── models/          # Data models
└── dto/             # Data transfer objects
```

### Por Qué Lucha con AI Coding

| Problema | Impacto |
|----------|---------|
| **Low cohesion** | Código de producto esparcido en 5 directorios |
| **High navigation cost** | AI debe atravesar layers para entender una feature |
| **Token inefficiency** | Cargar 6 archivos para entender agregar un producto |
| **Context switching** | AI pierde track del propósito mientras navega |

### La Verdad Dura

> "Clean Architecture fue diseñada para maintainability humana a escala. Pero los agentes AI no piensan en layers - piensan en features. En 2025, construir arquitectura layered es como optimizar para caballos cuando todos manejan autos."

### Cuándo Todavía Tiene Sentido

- Apps pequeñas (<5K líneas)
- Código legacy que funciona
- Cumplimiento regulatorio que requiere separación específica

---

## Patrón 5: Microservices

**Qué es:** Múltiples servicios independientes, cada uno deployado separadamente, comunicándose por red.

### Por Qué es Challenging para AI Coding

| Desafío | Descripción |
|---------|-------------|
| **Context fragmentation** | Agente necesita entender múltiples repos |
| **Coordination overhead** | Cambios a menudo abarcan múltiples servicios |
| **State management** | Contexto de conversación dividido entre servicios |
| **Testing complexity** | Integration tests requieren múltiples servicios corriendo |
| **Network boundaries** | AI no puede atravesar fácilmente service calls |

### La Paradoja de Microservices

> "Microservices dividen concerns bien para equipos humanos, pero son notablemente hostiles para agentes AI."

### Solución Pragmática

Si ya tienes microservices:
- **NO reescribas** - es mucho esfuerzo
- **Organiza cada servicio internamente con VSA**
- "Microservices para scaling, monorepos para sanidad"

### Cuándo Usar

- Ya tienes microservices (no reescribir)
- Bounded contexts distintos con equipos separados
- Requisitos de scaling genuinamente necesitan servicios independientes

---

## Patrón 6: Single File / Monolith

**Qué es:** Todo en un archivo (o muy pocos). El enfoque "script".

### Por Qué Algunos Equipos lo Intentan

- Ultimate token efficiency (AI ve todo de una vez)
- Sin navegación
- Iteración rápida

### Por Qué Colapsa

| Problema | Resultado |
|----------|-----------|
| **Context window explosion** | La mayoría de archivos llegan a 1000+ líneas rápido |
| **No modularity** | No se puede trabajar en múltiples features en paralelo |
| **Human maintainability nightmare** | Imposible de navegar para humanos |
| **Git conflicts** | Cada cambio toca el mismo archivo |

### Cuándo Funciona

- ✅ Prototipos verdaderos (<500 líneas total)
- ✅ Proyectos de fin de semana que tirarás
- ✅ Proof-of-concepts donde maintainability no importa

---

## El Problema del Context Window

Los LLMs tienen context windows limitados. Tu arquitectura determina cuánto se gasta en navegación vs trabajo real.

### Capacidades Actuales

| Tipo de Modelo | Capacidad |
|----------------|-----------|
| **Modelos rápidos** | ~6,000 caracteres por interacción |
| **Modelos avanzados** | ~200,000 tokens (~150K caracteres) |
| **Modelos frontier** | ~1M tokens (~750K caracteres) |

Pero un codebase empresarial típico tiene **millones de tokens** en **miles de archivos**.

### Las Matemáticas de Token Efficiency

**Layered Architecture:**
```
Add product to catalog flow:
- Load controller       (150 tokens)
- Load service         (200 tokens)
- Load repository      (180 tokens)
- Load model          (120 tokens)
- Load validator      (160 tokens)
- Load DTO            (90 tokens)
Total: ~900 tokens solo para ver el código
```

**Vertical Slice Architecture:**
```
Add product to catalog flow:
- Load products/routes.py    (400 tokens - incluye todo)
Total: ~400 tokens
```

**Ahorro: 55% menos tokens** para el mismo entendimiento. En cientos de interacciones por día, esto se acumula masivamente.

---

## El Factor del Tamaño de Archivo

AI coding assistants luchan con archivos de más de 400-500 líneas.

### Best Practices

| Regla | Razón |
|-------|-------|
| **Target: <300 líneas por archivo** | Context window manejable |
| **Romper archivos grandes** | En módulos enfocados |
| **Una responsabilidad por archivo** | Single Responsibility Principle |
| **Tests junto a implementación** | Co-localización |

### Ejemplo de Breakdown

```
# ❌ Malo: Un archivo masivo de 1200 líneas
products/service.py       # Todo aquí

# ✅ Bueno: Archivos enfocados
products/
├── service.py            # 200 líneas - core business logic
├── validation.py         # 150 líneas - input validation
├── pricing.py            # 100 líneas - price calculation logic
├── inventory_sync.py     # 120 líneas - inventory integration
└── serializers.py        # 180 líneas - data transformation
```

---

## Arquitectura de Documentación

Tu arquitectura de código es solo la mitad. La **arquitectura de documentación** es igual de crítica.

### Modelo de Documentación de 3 Tiers

**Tier 1: README.md** (Single source of truth)
- Overview del proyecto y propósito
- Quick start guide (instalación, tests, dev server)
- Overview de arquitectura high-level
- Comandos comunes y workflows
- Links a documentación más profunda

**Tier 2: Feature-level READMEs**
```
products/README.md
inventory/README.md
categories/README.md
```

Cada directorio de feature tiene su README explicando:
- Propósito de la feature
- Flows clave y use cases
- Edge cases importantes
- Puntos de integración con otras features

**Tier 3: Architecture Decision Records (ADRs)**
```
docs/architecture/adr/
├── 001-use-vertical-slice-architecture.md
├── 002-database-per-feature-schema.md
└── 003-authentication-strategy.md
```

Los ADRs documentan **POR QUÉ** se tomaron decisiones. Crítico para agentes AI, porque sin contexto, sugerirán revertir decisiones que ven como subóptimas.

### ¿AGENTS.md?

Algunos equipos usan `AGENTS.md` - un "README para máquinas".

**Mi opinión:** Si escribes un README comprehensivo, no necesitas AGENTS.md. El contenido debería ser idéntico.

Si usas AGENTS.md:
- Mantenlo ≤150 líneas
- Incluye solo notas operacionales específicas para AI
- Mantén como código - actualiza en el mismo commit cuando cambien convenciones

---

## Caso de Estudio Real: El Journey de Refactoring

Un startup con 40K líneas de Python en arquitectura layered. 5 developers, usando GitHub Copilot, constantemente frustrados.

### Antes (Layered Architecture)

| Métrica | Valor |
|---------|-------|
| Archivos para cargar por cambio | 6-8 |
| Tokens promedio por cambio | 12,000 |
| Satisfacción del developer con AI | 4/10 |
| Tiempo ahorrado por AI | ~20% |

### Después (Vertical Slice Architecture)

| Métrica | Valor |
|---------|-------|
| Archivos para cargar por cambio | 1-2 |
| Tokens promedio por cambio | 4,500 |
| Satisfacción del developer con AI | 8/10 |
| Tiempo ahorrado por AI | ~60% |

**El refactoring tomó 2 semanas. Los gains de productividad se pagaron en 3 semanas.**

### Cómo Lo Hicieron

1. Empezaron con features nuevas - construidas en VSA desde día 1
2. Al tocar código viejo, lo movían a feature slices
3. Crearon guía de migración (ADR) explicando la nueva estructura
4. Después de 6 meses, 80% del codebase estaba en nueva estructura
5. Dejaron código estable y no tocado en estructura vieja (pragmatismo sobre pureza)

---

## Estrategias de Migración Prácticas

### Estrategia 1: Features Nuevas Primero

- Todas las features nuevas usan nueva arquitectura
- Código viejo se queda en estructura vieja hasta que se toque
- Crear boundary claro entre viejo y nuevo
- En 6-12 meses, la mayoría del código activo migra naturalmente

### Estrategia 2: Extracción de Features

1. Elegir una feature (ej: product catalog)
2. Extraer todo el código relacionado a nuevo directorio
3. Escribir feature README
4. Actualizar imports y tests
5. Deploy y validar
6. Repetir con siguiente feature

### Estrategia 3: Enfoque Híbrido

- Mantener código estable y no tocado en estructura vieja
- Mover código frecuentemente modificado a nueva estructura
- Crear `docs/MIGRATION.md` explicando los dos patterns
- Set timeline para eventual migración completa (o no - pragmatismo gana)

### Estrategia 4: Colapso Gradual de Layers

1. Empezar moviendo controllers + services a feature folders
2. Después agregar repositories a feature folders
3. Finalmente agregar models y DTOs
4. Cada paso es un cambio pequeño y seguro

**Pro tip:** Deja que tu agente AI ayude con el refactoring. Dale el plan de migración y que mueva archivos, actualice imports, y arregle tests. Es excelente en este tipo de trabajo mecánico.

---

## Conexión con Multi-Agent Architecture

Si construyes sistemas con **múltiples agentes AI** (orchestrator + workers), tu arquitectura de código se vuelve aún más crítica.

### Por Qué

Cada agente opera en su propio context window. Necesitan:
- Encontrar código relevante rápido
- Entender boundaries claros
- Pasar información eficientemente
- Evitar pisarse los pies unos a otros

### Por Qué VSA es Perfecto para Multi-Agent

- Cada agente puede "ser dueño" de un feature slice
- Puntos de handoff claros entre slices
- Overlap de contexto mínimo
- Distribución de trabajo natural

### Ejemplo de Flow Multi-Agent

```
Orchestrator Agent: "Necesitamos agregar pricing tiers a bulk products"
  ↓
Worker Agent 1: "Actualizaré products/service.py con tier pricing logic"
Worker Agent 2: "Actualizaré products/pricing.py con calculation engine"
Worker Agent 3: "Actualizaré products/test_service.py con pricing tests"
  ↓
Orchestrator Agent: "Correr tests, merge cambios"
```

Cada worker opera en un contexto enfocado (un directorio de feature), sin conflictos, uso eficiente de tokens.

---

## Checklist de Token Efficiency

Antes de comprometerte con una arquitectura, audítala contra estos criterios:

### ✅ Arquitectura AI-Friendly

- [ ] Código relacionado vive junto (high cohesion)
- [ ] Archivos son <300 líneas cada uno
- [ ] Nombres claros y descriptivos de archivos y funciones
- [ ] Dependencias explícitas (sin globals ocultos)
- [ ] Documentación a nivel de feature (READMEs)
- [ ] Tests co-localizados con implementación
- [ ] Straightforward, mínima "magia"
- [ ] ADRs para decisiones clave

### ❌ Arquitectura AI-Hostile

- [ ] Código esparcido en muchos directorios
- [ ] Archivos grandes (>500 líneas)
- [ ] Nombres genéricos (handler.py, utils.py, helpers.py)
- [ ] Dependencias ocultas y estado global
- [ ] Documentación esparcida o faltante
- [ ] Tests en árbol separado lejos del código
- [ ] Heavy metaprogramming o behaviors implícitos
- [ ] Sin explicación de decisiones arquitectónicas

---

## Roadmap de Implementación

### Semana 1: Auditoría

- [ ] Mapear tu arquitectura actual
- [ ] Identificar pain points (¿dónde lucha más la AI?)
- [ ] Medir uso de tokens para operaciones comunes
- [ ] Encuestar al equipo sobre productividad con AI

### Semana 2: Experimentar

- [ ] Elegir una feature nueva
- [ ] Implementar en Vertical Slice Architecture
- [ ] Medir token efficiency vs enfoque viejo
- [ ] Recoger feedback del equipo

### Semana 3: Expandir

- [ ] Aplicar a 2-3 features nuevas más
- [ ] Crear guía de migración (ADR)
- [ ] Actualizar documentación
- [ ] Compartir learnings con equipo

### Semana 4+: Escalar

- [ ] Todas las features nuevas usan nueva arquitectura
- [ ] Migrar gradualmente código de alto tráfico
- [ ] Setup monitoring de productividad con AI
- [ ] Iterar basándose en datos

**Lo más importante:** Logra buy-in del equipo. Cambios de arquitectura fallan cuando se imponen top-down. Corre experimentos, comparte datos, deja que los resultados hablen.

---

## Matriz de Decisión Final

| Patrón | AI-Friendliness | Token Efficiency | Maintainability | Complexity | Mejor Para |
|--------|-----------------|------------------|-----------------|------------|------------|
| **Vertical Slice** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | Apps nuevas, equipos AI-heavy |
| **Feature Folders** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | Transición desde layered |
| **Modular Monolith** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | Apps grandes, boundaries estrictos |
| **Layered** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Apps pequeñas, legacy |
| **Microservices** | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Ya usando, scaling needs |
| **Single File** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐ | Solo prototipos |

---

## Recomendación

**Empieza con Vertical Slice Architecture.** Es el sweet spot:
- Alta productividad con AI
- Complejidad razonable
- Buena maintainability

Puedes ajustar después basándote en tus necesidades específicas.

---

## Conclusión

> "Architecture Is Infrastructure" — Rasmus Widing

No correrías una aplicación de producción sin infraestructura apropiada. **La arquitectura para AI coding es infraestructura para tu proceso de desarrollo.**

Los patrones de arquitectura que elijas crean el ambiente donde tanto AI como humanos trabajan. Elige mal, y pelearás con tu codebase todos los días. Elige bien, y tus agentes AI se vuelven 3-5× más productivos.

**Los ganadores en desarrollo AI-augmented no son los equipos con mejores prompts o herramientas AI más fancy. Son los equipos con MEJOR ARQUITECTURA.**
