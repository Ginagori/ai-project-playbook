# 🎯 Tech Stack Selector - Decision Tree Interactivo

**Elige el tech stack apropiado basado en tus requirements (no en modas)**

---

## Cómo Usar Este Selector

Responde las preguntas en orden. Cada respuesta te lleva a la siguiente pregunta relevante.

Al final, obtendrás:
- Tech stack recomendado con rationale
- Alternativas consideradas
- Trade-offs de tu elección

---

## DECISION TREE

### Q1: ¿Qué tipo de proyecto es?

A) **Web Application (SaaS, Dashboard, CMS)**
→ Ir a Q2

B) **Mobile App (iOS/Android)**
→ Ir a Q10

C) **Data/Analytics Project (Dashboards, Reports, ML)**
→ Ir a Q15

D) **CLI Tool / Automation Script**
→ Ir a Q20

---

## BRANCH A: Web Application

### Q2: ¿Necesitas SEO (marketing site, blog, e-commerce)?

**A) SÍ - Necesito SEO**
→ Necesitas Server-Side Rendering (SSR)
→ Frontend: **Next.js** (React) o **SvelteKit** (Svelte)
→ Ir a Q3

**B) NO - Es un dashboard/app interna**
→ Single Page App (SPA) es suficiente
→ Frontend: **React + Vite** o **Vue + Vite**
→ Ir a Q3

---

### Q3: ¿Necesitas backend?

**A) SÍ - Necesito APIs, base de datos, lógica de negocio**
→ Ir a Q4

**B) NO - Solo frontend estático (JAMstack)**
→ Stack: Next.js/SvelteKit + Headless CMS (Contentful, Sanity)
→ Deployment: Vercel, Netlify
→ DONE

---

### Q4: ¿Qué lenguaje conoce tu equipo para backend?

**A) Python**
→ Backend: **FastAPI** (moderno, async) o **Django** (batteries-included)
→ Ir a Q5

**B) TypeScript/JavaScript**
→ Backend: **Express.js** (estándar) o **Fastify** (rápido)
→ Ir a Q5

**C) Go**
→ Backend: **Gin** o **Fiber**
→ Ir a Q5

**D) Otro / No sé**
→ Recomendación: **Python + FastAPI** (mejor balance velocidad/facilidad)
→ Ir a Q5

---

### Q5: ¿Necesitas transacciones ACID?

**Contexto:** E-commerce, finanzas, reservaciones = necesitas ACID

**A) SÍ**
→ Database: **PostgreSQL** (gold standard)
→ Ir a Q6

**B) NO / No estoy seguro**
→ Database: **PostgreSQL** (default seguro para 90% casos)
→ Alternativa: MongoDB solo si schema muy variable
→ Ir a Q6

---

### Q6: ¿Necesitas multi-tenancy?

**Contexto:** B2B SaaS donde cada empresa/customer es un "tenant"

**A) SÍ - B2B SaaS con múltiples customers**
→ CRÍTICO: Diseña multi-tenancy DESDE DÍA 1
→ Architecture: tenant_id en todas las tablas, row-level security
→ Ir a Q7

**B) NO - B2C o herramienta interna**
→ Architecture: más simple, sin tenant isolation
→ Ir a Q7

---

### Q7: ¿Cuántos usuarios concurrentes esperas?

**A) 1-100 usuarios**
→ Deployment: **Railway** (simple, $5-20/mes) o **Vercel + Supabase**
→ Ir a Q8

**B) 100-1,000 usuarios**
→ Deployment: **Cloud Run** (auto-scaling) o **Railway Pro**
→ Necesitas: Redis caching, CDN
→ Ir a Q8

**C) 1,000-10,000 usuarios**
→ Deployment: **Cloud Run** con load balancing
→ Necesitas: Redis, CDN, DB read replicas
→ Ir a Q8

**D) 10,000+ usuarios**
→ Deployment: **Kubernetes** (EKS, GKE)
→ Necesitas: Microservices, sharding, advanced caching
→ Ir a Q8

---

### Q8: ¿Necesitas background jobs?

**Ejemplos:** Email sending, report generation, data processing

**A) SÍ**
→ Queue: **Celery** (Python) o **BullMQ** (Node)
→ Message broker: **Redis**
→ Ir a Q9

**B) NO**
→ Ir a Q9

---

### Q9: ¿Necesitas búsqueda full-text avanzada?

**A) SÍ - Búsqueda compleja, fuzzy matching, typo tolerance**
→ Search: **MeiliSearch** (fácil) o **Elasticsearch** (enterprise)
→ DONE - Ve a Resumen

**B) NO - Búsqueda simple por nombre/email**
→ Search: PostgreSQL full-text search (pg_trgm)
→ DONE - Ve a Resumen

---

## BRANCH B: Mobile App

### Q10: ¿iOS, Android, o ambos?

**A) Ambos (cross-platform)**
→ Ir a Q11

**B) Solo iOS**
→ Stack: **Swift + SwiftUI**
→ Backend: usa Q4-Q9 de Web App
→ DONE

**C) Solo Android**
→ Stack: **Kotlin + Jetpack Compose**
→ Backend: usa Q4-Q9 de Web App
→ DONE

---

### Q11: ¿Necesitas features nativas?

**Ejemplos:** Cámara avanzada, GPS en background, Bluetooth, NFC

**A) SÍ - Muchas features nativas**
→ Stack: **React Native** (comunidad grande) o **Flutter** (performance)
→ Backend: usa Q4-Q9
→ DONE

**B) NO - App básica, UI/forms principalmente**
→ Considera: **PWA** (Progressive Web App)
→ Stack: Next.js/SvelteKit + manifest.json
→ Benefit: Un codebase para web + móvil
→ DONE

---

## BRANCH C: Data/Analytics

### Q15: ¿Qué tipo de data project?

**A) Dashboard interactivo (visualización de datos)**
→ Ir a Q16

**B) Data pipeline (ETL, processing)**
→ Ir a Q17

**C) Machine Learning / AI**
→ Ir a Q18

---

### Q16: Dashboard - ¿Cuántos datos?

**A) < 100K filas, data cabe en memoria**
→ Stack: **Streamlit** + **Pandas/Polars**
→ Database: PostgreSQL o CSV files
→ Deployment: Streamlit Cloud (free)
→ DONE

**B) 100K - 10M filas**
→ Stack: **Streamlit** + **DuckDB** (analytics DB, super rápido)
→ Database: DuckDB + PostgreSQL para app data
→ Deployment: Railway, Cloud Run
→ DONE

**C) 10M+ filas, analytics pesado**
→ Stack: **Plotly Dash** + **ClickHouse** (columnar DB)
→ Caching: Redis
→ Deployment: Cloud Run + ClickHouse Cloud
→ DONE

---

### Q17: Data Pipeline - ¿Batch o real-time?

**A) Batch (nightly, hourly)**
→ Stack: **Python** + **Pandas/Polars**
→ Orchestration: **Cron** (simple) o **Airflow** (complejo)
→ Storage: PostgreSQL o Parquet files (S3)
→ DONE

**B) Real-time streaming**
→ Stack: **Python** + **Kafka** o **Pulsar**
→ Processing: **Apache Flink** o **Spark Streaming**
→ Storage: ClickHouse, TimescaleDB
→ DONE (complejo, considera alternativas simples primero)

---

### Q18: ML/AI - ¿Inference o training?

**A) Solo inference (modelo pre-entrenado)**
→ Stack: **FastAPI** + **PyTorch/TensorFlow**
→ Model: Hugging Face models, OpenAI API
→ Deployment: Cloud Run (CPU) o Cloud Run GPU
→ DONE

**B) Training + inference**
→ Stack: **Python** + **PyTorch** / **TensorFlow**
→ Training: **Google Colab** (prototipos) o **AWS SageMaker** (producción)
→ Deployment: Separate inference API (FastAPI)
→ DONE

---

## BRANCH D: CLI Tool

### Q20: ¿Qué lenguaje?

**A) Python - para scripting, data processing**
→ Stack: **Python** + **Click** o **Typer**
→ Distribution: PyPI package
→ DONE

**B) Node.js - para tooling de desarrollo**
→ Stack: **TypeScript** + **Commander.js**
→ Distribution: NPM package
→ DONE

**C) Go - para performance, binarios standalone**
→ Stack: **Go** + **Cobra**
→ Distribution: Binarios compilados
→ DONE

---

## TECH STACK TEMPLATES

### Template 1: Simple SaaS (B2B)

```yaml
Frontend:
  Framework: Next.js (React + TypeScript)
  Styling: Tailwind CSS
  State: Zustand

Backend:
  Framework: FastAPI (Python 3.13)
  Database: PostgreSQL 16
  ORM: SQLAlchemy
  Auth: NextAuth.js

Infrastructure:
  Frontend Deploy: Vercel
  Backend Deploy: Railway
  Database: Railway PostgreSQL
  Storage: AWS S3 (for files)

Cost: ~$20-50/mes (< 1000 users)
```

**Rationale:**
- Next.js: SEO + great DX
- FastAPI: Rápido, async, type-safe
- PostgreSQL: ACID, multi-tenancy support
- Railway: Simple, auto-deploy, $5 start

---

### Template 2: Internal Dashboard (No SEO)

```yaml
Frontend:
  Framework: React + Vite (TypeScript)
  Styling: Tailwind + shadcn/ui
  State: React Query + Zustand

Backend:
  Framework: FastAPI
  Database: PostgreSQL
  Cache: Redis

Infrastructure:
  Frontend: Netlify/Vercel
  Backend: Cloud Run
  Database: Cloud SQL

Cost: ~$10-30/mes
```

**Rationale:**
- Vite: Fast dev, simple
- No SSR needed (internal tool)
- Cloud Run: Pay-per-use, scales to zero

---

### Template 3: Analytics Dashboard

```yaml
Stack:
  Framework: Streamlit (Python)
  Data: DuckDB + Polars
  Viz: Plotly
  Cache: DuckDB materialized views

Infrastructure:
  Deploy: Streamlit Cloud (free) or Railway
  Data source: PostgreSQL / CSV files

Cost: $0-10/mes
```

**Rationale:**
- Streamlit: Fastest way to build data apps
- DuckDB: In-process analytics, super fast
- No backend needed

---

### Template 4: Mobile + Web (Cross-platform)

```yaml
Frontend:
  Web: Next.js
  Mobile: PWA (from Next.js)
  Alternative: React Native

Backend:
  Framework: FastAPI
  Database: PostgreSQL
  Auth: Firebase Auth

Infrastructure:
  Web: Vercel
  Backend: Cloud Run
  Database: Supabase

Cost: ~$15-40/mes
```

**Rationale:**
- PWA: One codebase, works on web + mobile
- Falls back to React Native if native features needed

---

## ANTI-PATTERNS (Qué NO hacer)

### ❌ Anti-Pattern 1: "Elegir porque está de moda"

**Malo:**
"Voy a usar microservices + Kubernetes porque Netflix lo usa"

**Contexto:**
- Tu app: 100 usuarios
- Netflix: 100M usuarios

**Correcto:**
Monolito en Railway. Escala a microservices CUANDO lo necesites (> 10K users).

---

### ❌ Anti-Pattern 2: "Tech stack mismatch"

**Malo:**
- Proyecto: Dashboard de analytics con 10M filas
- Stack elegido: MongoDB + React

**Problema:**
- MongoDB malo para analytics (no columnar)
- Deberías usar: PostgreSQL + DuckDB o ClickHouse

**Correcto:**
Elegir stack basado en requirements, no en familiaridad.

---

### ❌ Anti-Pattern 3: "Aprender 5 techs nuevas a la vez"

**Malo:**
- Nunca usaste: Rust, Kubernetes, GraphQL, Cassandra
- Tu proyecto nuevo: Rust + K8s + GraphQL + Cassandra

**Problema:**
- Vas a batallar con infra en vez de construir features
- Learning curve = 6 meses

**Correcto:**
- Usa tech que conoces para 80% del stack
- Aprende MAX 1 tech nueva (la más crítica)

---

## DECISION FRAMEWORK

Cuando no estás seguro, usa esta jerarquía:

**1. Requirements > Moda**
"¿Necesito ACID?" > "¿MongoDB está de moda?"

**2. Team Skills > Optimal Tech**
"Mi team sabe Python" > "Go es más rápido"

**3. Simplicidad > Poder**
Monolito > Microservices (hasta que lo necesites)

**4. Probado > Nuevo**
PostgreSQL (1996) > CockroachDB (2015)

**5. Managed > Self-hosted**
Railway > EC2 (para MVP)

---

## VALIDACIÓN DEL TECH STACK

**Antes de empezar a codear, verifica:**

### Checklist de Validación

- [ ] **Alignment:** ¿El stack se alinea con requirements? (ACID, multi-tenancy, scale)
- [ ] **Skills:** ¿Al menos 1 persona del team conoce este stack?
- [ ] **Cost:** ¿Cabe en el budget? (free tier para MVP OK)
- [ ] **Community:** ¿Tiene comunidad activa? (Stack Overflow, docs, tutorials)
- [ ] **Hiring:** ¿Puedo contratar developers que conozcan esto? (si team crece)
- [ ] **Exit strategy:** ¿Puedo migrar después si es necesario? (evita vendor lock-in total)

**Si todos ✅ → Procede**
**Si alguno ❌ → Reconsidera**

---

## EJEMPLOS DE DECISIONES

### Ejemplo 1: E-commerce MVP

**Requirements:**
- Usuarios: 100-1000
- Necesita: ACID (inventory + payments)
- Budget: $50/mes
- Team: 1 fullstack dev (conoce React + Python)

**Decision:**
```yaml
Frontend: Next.js (SEO critical)
Backend: FastAPI + PostgreSQL
Payments: Stripe (no manejar cards directamente)
Deploy: Vercel + Railway
```

**Rationale:**
- PostgreSQL: ACID garantizado
- Stripe: PCI compliance handled
- Railway: Simple, dentro de budget

**Alternatives considered:**
- MongoDB: NO - sin ACID robusto
- Node.js: NO - team conoce Python mejor

---

### Ejemplo 2: Internal Analytics Dashboard

**Requirements:**
- Usuarios: 20 (equipo interno)
- Data: 5M filas (sales data)
- Budget: $10/mes
- Team: 1 data analyst (conoce Python, no web dev)

**Decision:**
```yaml
Framework: Streamlit
Data: DuckDB (in-process)
Deploy: Streamlit Cloud (free)
```

**Rationale:**
- Streamlit: Data analyst puede buildear sin aprender React
- DuckDB: Analytics ultra-rápido, no necesita DB server
- Free tier: Dentro de budget

**Alternatives considered:**
- React dashboard: NO - data analyst no sabe frontend
- PostgreSQL: NO - DuckDB más rápido para analytics

---

## TEMPLATE DE DOCUMENTACIÓN

**Guarda tu decisión en:** `DISCOVERY.md`

```markdown
## Tech Stack Decision

### Frontend
**Choice:** [Framework]
**Rationale:** [Por qué]
**Alternatives:** [Qué NO elegiste y por qué]

### Backend
**Choice:** [Framework + Language]
**Database:** [PostgreSQL/MySQL/MongoDB]
**Rationale:** [Por qué]

### Infrastructure
**Deployment:** [Vercel/Railway/Cloud Run]
**Cost estimate:** [$X/mes]
**Rationale:** [Por qué]

### Key Trade-offs
**What we're optimizing for:** [Simplicidad/Performance/Cost]
**What we're sacrificing:** [Ej: "Sacrificamos performance por simplicidad"]

### Decision Date
[DATE] - Tech stack frozen for MVP. Can revisit after launch.
```

---

## NEXT STEPS

**Después de elegir tech stack:**

1. **Crear CLAUDE.md** (`02-planning/claude-md-creation.md`)
   - Documenta tu stack
   - Define project standards

2. **Setup proyecto**
   - Init git repo
   - Setup dev environment (docker-compose.yml)

3. **Primer PIV Loop**
   - Implementa health check endpoint
   - Valida que todo el stack funciona

---

**🎯 Remember: El mejor tech stack es el que te permite lanzar rápido y iterar.**

**Perfect stack que toma 6 meses aprender < Good enough stack que conoces hoy. 🚀**
