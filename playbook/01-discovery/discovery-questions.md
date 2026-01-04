# 📋 Discovery Questions - Cuestionario Completo

**40 preguntas sistemáticas para entender tu proyecto antes de codear**

---

## 🎯 Cómo Usar Este Cuestionario

**Opciones de uso:**

1. **Solo (15-30 min):** Responde todas las preguntas en un documento
2. **Con AI (20-40 min):** Pasa tus respuestas a Claude para análisis y tech stack recommendation
3. **Con equipo (45-60 min):** Workshop colaborativo para alinear visión

**Output:** Discovery Document completo que guiará todo el proyecto

---

## SECCIÓN 1: PROBLEM & VISION (10 preguntas)

### 1.1 ¿Qué problema específico resuelve tu proyecto?

**Formato de respuesta:**
- Problema: [Describe el pain point en 2-3 frases]
- Ejemplo: "Los product managers pierden 5 horas/semana creando reportes manualmente copiando datos de múltiples dashboards a Excel"

**Por qué importa:** Si no puedes articular el problema claramente, probablemente estés solucionando el problema equivocado.

---

### 1.2 ¿Para quién es este proyecto?

**Formato de respuesta:**
- Usuario primario: [Rol/persona específica]
- Usuario secundario: [Si aplica]
- Ejemplo: "Primario: Product Managers en startups B2B (50-200 empleados). Secundario: Data Analysts que generan reportes para PMs"

**Detalles útiles:**
- Tamaño de la organización
- Nivel técnico (principiante/intermedio/avanzado)
- Contexto de uso (trabajo/personal/educación)

---

### 1.3 ¿Cómo resuelven este problema HOY (sin tu solución)?

**Formato de respuesta:**
- Solución actual: [Qué hacen ahora]
- Tiempo que toma: [X minutos/horas]
- Pain points: [Qué es frustrante]
- Ejemplo: "Exportan datos de 5 dashboards diferentes a CSV, copian/pegan en Excel, crean charts manualmente. Toma 3 horas, propenso a errores, difícil de actualizar"

**Por qué importa:** Entender la solución actual te dice qué features son realmente necesarios vs nice-to-have.

---

### 1.4 ¿Por qué las soluciones existentes no funcionan?

**Opciones comunes:**
- [ ] Muy caras ($X/mes es prohibitivo)
- [ ] Demasiado complejas (curva de aprendizaje alta)
- [ ] No cubren mi caso de uso específico
- [ ] Requieren integraciones que no tenemos
- [ ] Performance es mala (lento/crashes)
- [ ] Vendor lock-in preocupante
- [ ] Otro: [especificar]

**Ejemplo:** "Herramientas existentes (Tableau, Looker) cuestan $70/usuario/mes. Nuestro equipo de 20 PMs = $1,400/mes, fuera de presupuesto"

---

### 1.5 ¿Cuál es el outcome ideal? (No features, sino resultado)

**Formato de respuesta:**
- Outcome: [Estado final deseado]
- Ejemplo MALO: "Una app con dashboard bonito" (feature, no outcome)
- Ejemplo BUENO: "PMs pueden generar reportes ejecutivos en 5 minutos en vez de 3 horas"

**Métricas de éxito:**
- Tiempo ahorrado: [X horas/semana]
- Dinero ahorrado: [$X/mes]
- Usuarios activos: [X usuarios usando semanalmente]

---

### 1.6 ¿Qué sucede si NO construyes esto?

**Formato de respuesta:**
- Consecuencia de no actuar: [Qué se pierde]
- Ejemplo: "PMs seguirán perdiendo 15 horas/mes en reportes manuales. Oportunidad cost = $15,000/mes (suponiendo $100/hora). También, decisiones más lentas porque los datos están desactualizados"

**Por qué importa:** Si la consecuencia de no actuar es baja, quizás no vale la pena construirlo.

---

### 1.7 ¿Este proyecto es para ti, para tu equipo, o para vender?

**Opciones:**
- [ ] Personal (solo yo lo usaré)
- [ ] Equipo interno (5-50 personas en mi empresa)
- [ ] SaaS para vender (público general o B2B)
- [ ] Open source (comunidad)

**Implicaciones técnicas:**
- Personal → puede ser MVP "quick & dirty"
- Equipo → necesita ser mantenible, documentado
- SaaS → necesita multi-tenancy, billing, support
- Open source → necesita ser fácil de self-host

---

### 1.8 ¿Tienes competidores o alternativas similares?

**Lista 3-5 competidores:**
1. [Nombre]: [URL] - [Qué hace bien / mal]
2. [Nombre]: [URL] - [Qué hace bien / mal]

**Si no hay competidores:**
- ¿Por qué crees que no existen? (Red flag: quizás no hay demanda)
- ¿O simplemente no los has encontrado?

**Análisis competitivo ayuda a:**
- Aprender de sus decisiones técnicas
- Identificar tu diferenciación
- Validar que hay demanda

---

### 1.9 ¿Cuánto tiempo tienes para construir la v1?

**Opciones:**
- [ ] 1-2 semanas (MVP mínimo)
- [ ] 1 mes (MVP robusto)
- [ ] 2-3 meses (producto completo)
- [ ] 6+ meses (producto enterprise-grade)

**Implicaciones:**
- 1-2 semanas → solo features críticos, tech stack simple
- 1 mes → MVP con calidad, test coverage básico
- 2-3 meses → producto pulido, test coverage completo
- 6+ meses → considera microservices, escalabilidad avanzada

---

### 1.10 ¿Cuál es tu definición de "éxito" en 3 meses?

**Formato de respuesta:**
- Métrica 1: [X usuarios activos semanalmente]
- Métrica 2: [$X revenue, o X% adoption interna]
- Métrica 3: [X% de tiempo ahorrado vs. solución manual]

**Ejemplo:** "Éxito = 10 PMs usando la herramienta semanalmente, generando promedio de 5 reportes/semana cada uno, tiempo de generación < 5 min"

**Por qué importa:** Métricas claras te permiten saber si estás construyendo lo correcto.

---

## SECCIÓN 2: USERS & PERSONAS (5 preguntas)

### 2.1 ¿Puedes nombrar 3 personas específicas que usarían esto?

**Formato de respuesta:**
- Persona 1: [Nombre], [Rol], [Contexto]
- Persona 2: [Nombre], [Rol], [Contexto]
- Persona 3: [Nombre], [Rol], [Contexto]

**Ejemplo:**
- Sarah, Product Manager en Acme Corp, gestiona 3 productos SaaS
- John, Data Analyst en Beta Inc, crea reportes para 5 PMs
- Lisa, VP of Product en Startup X, revisa reportes ejecutivos semanalmente

**Por qué importa:** Usuarios abstractos ("product managers") son difíciles de diseñar. Personas específicas ("Sarah que gestiona 3 productos") son tangibles.

---

### 2.2 ¿Qué nivel técnico tienen tus usuarios?

**Opciones:**
- [ ] No técnico (nunca ha visto código)
- [ ] Semi-técnico (usa Excel, entiende fórmulas)
- [ ] Técnico (sabe SQL, puede leer código)
- [ ] Desarrolladores (escriben código profesionalmente)

**Implicaciones de UX:**
- No técnico → UI super simple, cero configuración
- Semi-técnico → pueden manejar configuración, no quieren ver código
- Técnico → aprecian poder avanzado, shortcuts de teclado
- Desarrolladores → valoran CLI, API, extensibilidad

---

### 2.3 ¿En qué dispositivos usarán tu producto?

**Opciones:**
- [ ] Desktop solamente (web app o desktop app)
- [ ] Desktop + móvil (responsive o apps nativas)
- [ ] Móvil solamente (app móvil o PWA)
- [ ] Tablet principalmente

**Implicaciones técnicas:**
- Desktop only → no necesitas preocuparte por responsive
- Desktop + móvil → responsive design crítico, o considera PWA
- Móvil only → considera React Native/Flutter vs PWA

---

### 2.4 ¿Cuántos usuarios concurrentes esperas?

**Opciones:**
- [ ] 1-10 (personal/equipo pequeño)
- [ ] 10-100 (equipo mediano)
- [ ] 100-1,000 (pequeña empresa)
- [ ] 1,000-10,000 (mediana empresa)
- [ ] 10,000+ (enterprise)

**Implicaciones técnicas:**
- 1-10 → serverless OK, DB pequeña
- 10-100 → serverless OK, considera caching
- 100-1K → necesitas caching (Redis), DB con indexing
- 1K-10K → load balancing, CDN, DB replication
- 10K+ → microservices, Kubernetes, sharding de DB

---

### 2.5 ¿Los usuarios pagarían por esto? ¿Cuánto?

**Formato de respuesta:**
- Disposición a pagar: [$X/mes por usuario]
- Modelo: [Freemium / Solo pago / Open source con enterprise tier]

**Ejemplo:** "Usuarios pagarían $10-20/usuario/mes. Modelo: Freemium (3 reportes/mes gratis, ilimitado en plan pago)"

**Por qué importa:** Si nadie pagaría, quizás no es un pain point suficientemente fuerte. O es mejor como open source.

---

## SECCIÓN 3: TECHNICAL REQUIREMENTS (10 preguntas)

### 3.1 ¿Qué tipo de datos manejarás?

**Opciones:**
- [ ] Datos de usuarios (emails, perfiles, preferencias)
- [ ] Contenido generado por usuarios (posts, comments, archivos)
- [ ] Datos transaccionales (compras, pagos, inventario)
- [ ] Analytics/métricas (events, logs, time-series)
- [ ] Archivos/media (imágenes, videos, PDFs)

**Implicaciones:**
- Datos de usuarios → necesitas auth, GDPR compliance
- UGC → necesitas moderación, storage escalable
- Transaccional → necesitas ACID, transacciones robustas
- Analytics → considera columnar DBs (ClickHouse, DuckDB)
- Media → necesitas CDN, object storage (S3)

---

### 3.2 ¿Cuántos datos esperas almacenar?

**Opciones:**
- [ ] < 1 GB (miles de filas)
- [ ] 1-10 GB (decenas de miles de filas)
- [ ] 10-100 GB (cientos de miles de filas)
- [ ] 100 GB - 1 TB (millones de filas)
- [ ] 1+ TB (decenas de millones de filas)

**Implicaciones:**
- < 1 GB → SQLite o PostgreSQL básico OK
- 1-10 GB → PostgreSQL con indexing adecuado
- 10-100 GB → PostgreSQL + partitioning, considera read replicas
- 100 GB - 1 TB → considera sharding, columnar DB para analytics
- 1+ TB → definitivamente necesitas estrategia de sharding/partitioning

---

### 3.3 ¿Necesitas transacciones ACID?

**¿Qué son transacciones ACID?**
Atomicidad, Consistencia, Isolación, Durabilidad = operaciones críticas que no pueden fallar a medias.

**Escenarios donde SÍ necesitas ACID:**
- [ ] E-commerce (inventario + payment debe ser atómico)
- [ ] Finanzas (transferencias de dinero)
- [ ] Reservaciones (bookings de hotel/vuelo)
- [ ] Multi-step operations críticas

**Escenarios donde NO necesitas ACID:**
- [ ] Blog/CMS (si un post se pierde, no es fin del mundo)
- [ ] Analytics (eventual consistency OK)
- [ ] Social media (likes pueden ser eventually consistent)

**Implicaciones:**
- Necesitas ACID → PostgreSQL, MySQL (NO MongoDB, NO DynamoDB sin cuidado)
- No necesitas ACID → más flexibilidad (MongoDB, DynamoDB, Firebase OK)

---

### 3.4 ¿Necesitas búsqueda full-text?

**Ejemplos de búsqueda:**
- [ ] Búsqueda simple (email exact match) → no es full-text
- [ ] Búsqueda por keywords (productos por nombre/descripción) → sí es full-text
- [ ] Búsqueda avanzada (fuzzy matching, typo tolerance) → full-text avanzado

**Implicaciones técnicas:**
- No necesitas → búsqueda básica con SQL LIKE OK
- Sí necesitas básico → PostgreSQL full-text search (pg_trgm)
- Sí necesitas avanzado → Elasticsearch, MeiliSearch, Typesense

---

### 3.5 ¿Necesitas actualizaciones en tiempo real?

**Escenarios:**
- [ ] Chat/mensajería → SÍ (WebSockets)
- [ ] Colaboración (Google Docs-style) → SÍ (WebSockets + CRDT)
- [ ] Dashboard con métricas → DEPENDE (Server-Sent Events puede bastar)
- [ ] Blog/sitio estático → NO (polling cada 5 min OK)

**Implicaciones técnicas:**
- Sí real-time → WebSockets, Socket.io, Server-Sent Events
- No real-time → HTTP polling, o simplemente refresh manual

---

### 3.6 ¿Necesitas multi-tenancy?

**¿Qué es multi-tenancy?**
Múltiples "customers" (organizaciones) usan la misma instancia de tu app, con datos completamente aislados.

**Escenarios donde SÍ:**
- [ ] B2B SaaS (cada empresa es un tenant)
- [ ] Plataforma educativa (cada escuela es un tenant)
- [ ] White-label solution (cada cliente tiene su propia instancia lógica)

**Escenarios donde NO:**
- [ ] B2C (usuarios individuales, no organizaciones)
- [ ] Herramienta interna (solo tu empresa usa)

**Implicaciones arquitectónicas:**
- Sí multi-tenancy → DISEÑA DESDE DÍA 1
  - tenant_id en TODAS las tablas
  - Row-level security en queries
  - Isolation de datos en todos los flows
- No multi-tenancy → arquitectura más simple

**WARNING:** Agregar multi-tenancy DESPUÉS = refactoring masivo. Decide desde el inicio.

---

### 3.7 ¿Necesitas integraciones externas?

**Lista APIs/servicios que necesitarás:**
- [ ] Autenticación: [Google OAuth, Auth0, etc.]
- [ ] Pagos: [Stripe, PayPal]
- [ ] Email: [SendGrid, Mailgun]
- [ ] Storage: [AWS S3, Cloudinary]
- [ ] Analytics: [Mixpanel, Amplitude]
- [ ] AI/ML: [OpenAI API, Anthropic]
- [ ] Otros: [especificar]

**Implicaciones:**
- Cada integración = dependency a manejar
- Considera rate limits, costos, latency
- Necesitarás environment variables, secrets management

---

### 3.8 ¿Qué nivel de seguridad/compliance necesitas?

**Opciones:**
- [ ] Básico (password hashing, HTTPS)
- [ ] GDPR compliance (EU users)
- [ ] HIPAA (datos de salud en USA)
- [ ] SOC 2 (enterprise customers)
- [ ] PCI DSS (si manejas credit cards directamente)

**Implicaciones:**
- Básico → suficiente para mayoría de apps
- GDPR → necesitas data deletion, export, consent tracking
- HIPAA → encryption at rest + in transit, audit logs, BAA con vendors
- SOC 2 → security controls formales, pentesting, documentación extensa
- PCI DSS → casi nunca manejes cards directamente, usa Stripe/PayPal

**Consejo:** Si no estás seguro, empieza con "Básico". Agregar compliance después es posible (pero costoso).

---

### 3.9 ¿Necesitas background jobs/async processing?

**Escenarios donde SÍ:**
- [ ] Email sending (no bloquear request)
- [ ] Report generation (puede tomar > 30 segundos)
- [ ] Image processing (resize, thumbnails)
- [ ] Data imports (CSV con 100K filas)
- [ ] Scheduled tasks (cron jobs)

**Implicaciones técnicas:**
- Sí necesitas → Celery (Python), BullMQ (Node), Sidekiq (Ruby)
- También necesitas message queue → Redis, RabbitMQ

---

### 3.10 ¿Qué latencia/performance necesitas?

**Formato de respuesta:**
- API response time: [< X ms]
- Page load time: [< X segundos]
- Background job completion: [< X minutos]

**Benchmarks típicos:**
- API: < 200ms (bueno), < 500ms (aceptable), > 1s (malo)
- Page load: < 2s (bueno), < 5s (aceptable), > 5s (malo)
- Background: depende del caso de uso

**Implicaciones:**
- Si necesitas < 100ms → caching agresivo, CDN, DB optimization crítico
- Si < 500ms OK → optimization normal basta
- Si > 1s OK → puedes priorizar features sobre performance

---

## SECCIÓN 4: TEAM & RESOURCES (5 preguntas)

### 4.1 ¿Quién está en el equipo?

**Formato de respuesta:**
- Solo yo: [frontend/backend/fullstack]
- Team de X personas: [roles]

**Ejemplo:** "Solo yo (fullstack), con experiencia en React + Python. Tengo amigo diseñador que puede ayudar con UI ocasionalmente"

**Implicaciones:**
- Solo → elige stack que conoces bien
- Team pequeño → coordinación simple, monorepo OK
- Team grande → microservices, APIs bien definidas

---

### 4.2 ¿Qué tecnologías conoce el equipo?

**Lista de skills:**
- Lenguajes: [Python, JavaScript, Go, etc.]
- Frameworks: [React, Vue, Django, FastAPI, etc.]
- Databases: [PostgreSQL, MySQL, MongoDB, etc.]
- DevOps: [Docker, Kubernetes, AWS, etc.]

**Regla de oro:** Elige tech que el equipo ya conoce (al menos 1 persona).

**Excepción:** OK aprender 1 tech nueva si hay razón fuerte. NO aprendas 3 techs nuevas a la vez.

---

### 4.3 ¿Cuál es tu presupuesto mensual?

**Categorías de presupuesto:**
- [ ] $0 (free tier only)
- [ ] $10-50/mes (hobby/side project)
- [ ] $50-200/mes (startup MVP)
- [ ] $200-1,000/mes (growing startup)
- [ ] $1,000+/mes (established business)

**Implicaciones:**
- $0 → Vercel free, Railway free, Supabase free, SQLite
- $10-50 → Railway Hobby, Vercel Pro, pequeña DB
- $50-200 → Cloud Run, RDS pequeño, CDN
- $200-1K → Producción robusta, redundancia
- $1K+ → Enterprise features, high availability

---

### 4.4 ¿Tienes experiencia con DevOps/deployment?

**Opciones:**
- [ ] Nunca he deployed nada → usa plataformas managed (Vercel, Railway)
- [ ] He usado Heroku/Vercel → puedes manejar Railway, Fly.io
- [ ] Sé Docker básico → puedes usar Cloud Run, ECS
- [ ] Sé Kubernetes → tienes opciones enterprise-grade

**Consejo:** No sobre-compliques deployment. Empieza simple (Railway/Vercel), escala después si necesitas.

---

### 4.5 ¿Cuántas horas/semana puedes dedicar?

**Opciones:**
- [ ] 5-10 horas (side project, fines de semana)
- [ ] 20-30 horas (part-time)
- [ ] 40+ horas (full-time)

**Implicaciones para scope:**
- 5-10 hrs → MVP ultra-minimal, 1-2 meses para lanzar
- 20-30 hrs → MVP robusto, 3-4 semanas para lanzar
- 40+ hrs → producto completo, 2-3 semanas para MVP

---

## SECCIÓN 5: ARCHITECTURE & PATTERNS (5 preguntas)

### 5.1 ¿Prefieres monolito o microservices?

**Monolito:**
- ✅ Más simple, todo en un repo
- ✅ Deploy más fácil
- ✅ Debugging más fácil
- ❌ Escala vertical (upgrade server entero)

**Microservices:**
- ✅ Escala horizontal (cada servicio independiente)
- ✅ Tech stack diferente por servicio
- ❌ Más complejo (networking, service discovery)
- ❌ Debugging distribuido difícil

**Consejo:** Empieza con monolito. Casi siempre es la respuesta correcta para MVP.

---

### 5.2 ¿Server-Side Rendering (SSR) o Client-Side (SPA)?

**SSR (Next.js, Remix, SvelteKit):**
- ✅ Mejor SEO
- ✅ Faster First Contentful Paint
- ❌ Más complejo (servidor + cliente)

**SPA (React + Vite, Vue + Vite):**
- ✅ Más simple (solo frontend)
- ✅ UX más fluida (no full page reloads)
- ❌ SEO más difícil

**Consejo:**
- Necesitas SEO (marketing site, blog) → SSR
- App dashboard interno → SPA OK

---

### 5.3 ¿REST API o GraphQL?

**REST:**
- ✅ Más simple, más estándar
- ✅ Caching más fácil
- ❌ Puede hacer over-fetching/under-fetching

**GraphQL:**
- ✅ Cliente pide exactamente lo que necesita
- ✅ Menos endpoints
- ❌ Más complejo de setup
- ❌ Caching más difícil

**Consejo:** Empieza con REST. GraphQL solo si tienes caso de uso claro (mobile app con data fetching complejo).

---

### 5.4 ¿SQL o NoSQL?

**SQL (PostgreSQL, MySQL):**
- ✅ Transacciones ACID
- ✅ Relaciones entre datos
- ✅ Esquema estructurado
- ❌ Menos flexible para cambios de schema

**NoSQL (MongoDB, DynamoDB):**
- ✅ Flexible schema
- ✅ Escala horizontal más fácil
- ❌ Sin transacciones robustas (o limitadas)
- ❌ Difícil hacer joins

**Consejo:**
- Default a PostgreSQL (90% de casos)
- NoSQL solo si tienes caso específico (schema muy variable, escala masiva)

---

### 5.5 ¿Hosting: Serverless, Containers, o VMs?

**Serverless (Vercel, Railway, Fly.io):**
- ✅ Zero DevOps, auto-scaling
- ✅ Pay per use
- ❌ Vendor lock-in
- ❌ Cold starts

**Containers (Cloud Run, ECS, Kubernetes):**
- ✅ Control sobre environment
- ✅ Portable entre clouds
- ❌ Más setup
- ❌ Tienes que manejar scaling

**VMs (EC2, DigitalOcean Droplets):**
- ✅ Control total
- ✅ Predecible cost
- ❌ Tienes que manejar TODA la infra
- ❌ No auto-scaling (sin config manual)

**Consejo:** Serverless para MVP, containers si creces, VMs solo si tienes razón muy específica.

---

## SECCIÓN 6: CONSTRAINTS & RISKS (5 preguntas)

### 6.1 ¿Qué te preocupa más de este proyecto?

**Opciones comunes:**
- [ ] No sé si hay demanda real
- [ ] No sé si puedo construirlo técnicamente
- [ ] No sé si tengo tiempo para terminarlo
- [ ] No sé cómo monetizar
- [ ] No sé cómo escalar si crece mucho

**Identificar preocupaciones temprano te permite mitigarlas.**

---

### 6.2 ¿Qué es lo que NO sabes hacer aún?

**Ejemplo de gaps de conocimiento:**
- [ ] No sé deployment/DevOps
- [ ] No sé backend (solo sé frontend)
- [ ] No sé design/UI
- [ ] No sé testing
- [ ] No sé security best practices

**Consejo:** Identifica 1-2 gaps más críticos, aprende esos ANTES de empezar (o busca ayuda).

---

### 6.3 ¿Hay alguna fecha límite?

**Formato de respuesta:**
- Fecha límite: [fecha o "no hay"]
- Razón: [por qué esa fecha]

**Ejemplo:** "Deadline: 1 de marzo (quiero lanzar antes de conferencia donde puedo demostrar)"

**Implicaciones:**
- Con deadline → reduce scope agresivamente, solo features críticos
- Sin deadline → puedes ir más pausado, priorizar calidad

---

### 6.4 ¿Qué pasaría si el proyecto falla?

**Opciones:**
- [ ] Nada grave (side project por diversión)
- [ ] Aprendizaje perdido (tiempo invertido)
- [ ] Oportunidad perdida (competidor lanza primero)
- [ ] Costo financiero (gasté $X en MVP)
- [ ] Riesgo reputacional (prometí a customers)

**Consejo:** Si riesgo es alto, valida MÁS antes de codear (prototipos, landing page, user interviews).

---

### 6.5 ¿Qué te haría abandonar este proyecto?

**Opciones comunes:**
- [ ] Nadie lo usa después de 3 meses
- [ ] No puedo monetizarlo
- [ ] Es muy difícil de construir técnicamente
- [ ] Me aburro del problema
- [ ] Otra oportunidad más interesante aparece

**Por qué importa:** Saber cuándo "quitar el plug" evita desperdiciar tiempo en proyectos muertos.

---

## 📊 ANÁLISIS DE RESPUESTAS

**Después de completar las 40 preguntas:**

### Paso 1: Categoriza tu proyecto

Basado en tus respuestas, tu proyecto es:

**A) Personal Tool**
- Solo tú lo usas
- < 10 usuarios
- No monetizado
→ Tech stack: Lo más simple posible, lo que ya conoces

**B) Team/Internal Tool**
- 10-100 usuarios internos
- No monetizado externamente
→ Tech stack: Balancear simplicidad + mantenibilidad

**C) SaaS Product**
- 100+ usuarios externos
- Monetizado
- Multi-tenancy probable
→ Tech stack: Robusto, escalable, multi-tenant desde día 1

**D) Analytics/Data Project**
- Principalmente data processing
- Visualización de insights
→ Tech stack: Polars/DuckDB, Streamlit/Plotly

---

### Paso 2: Identifica Tech Stack Apropiado

**Usa tus respuestas para:**

1. **Database:**
   - Necesitas ACID? → PostgreSQL
   - No necesitas ACID pero quieres relaciones? → PostgreSQL igual
   - Schema muy variable + no necesitas ACID? → MongoDB

2. **Backend:**
   - Team sabe Python? → FastAPI
   - Team sabe JavaScript? → Express.js o Fastify
   - Performance crítico? → Go

3. **Frontend:**
   - SSR para SEO? → Next.js
   - SPA para dashboard? → React + Vite
   - Simplicidad máxima? → Svelte + SvelteKit

4. **Deployment:**
   - 0-100 usuarios, presupuesto bajo? → Railway, Vercel
   - 100-10K usuarios? → Cloud Run
   - 10K+ usuarios? → Kubernetes

---

### Paso 3: Documenta tu Discovery

**Crea archivo:** `my_workspace/projects/[project-name]/DISCOVERY.md`

**Usa template de:** `01-discovery/README.md`

**Incluye:**
- Problem statement (Q1.1)
- Users & personas (Q2.1, 2.2)
- Tech requirements (Q3.1-3.10)
- Tech stack decision (con rationale)
- Risks (Q6.1-6.5)
- MVP scope

---

### Paso 4: Validar con AI

**Prompt para Claude:**

```markdown
He completado Discovery para mi proyecto.

Mis respuestas a las 40 preguntas:
[pega tus respuestas aquí]

Tareas:
1. Analiza si hay gaps o inconsistencias en mis respuestas
2. Recomienda tech stack apropiado con rationale
3. Identifica los 3 mayores riesgos de este proyecto
4. Propón MVP scope (qué construir primero)
5. Sugiere timeline realista

Genera Discovery Document completo.
```

---

## ✅ Checklist Final

**Antes de pasar a Planning:**

- [ ] Respondí las 40 preguntas
- [ ] Identifiqué tipo de proyecto (Personal/Team/SaaS/Analytics)
- [ ] Tengo tech stack recomendado con rationale
- [ ] Documenté risks y mitigaciones
- [ ] Definí MVP scope (qué SÍ y qué NO en v1)
- [ ] Tengo métricas de éxito cuantificables
- [ ] Validé con AI o con equipo

**Si todos marcados → Avanza a Planning (`02-planning/claude-md-creation.md`)**

---

**🎯 Remember: Estas 40 preguntas toman 30-45 minutos, pero ahorran semanas de refactoring. 🚀**

**Discovery profundo = fundación sólida para todo el proyecto.**
