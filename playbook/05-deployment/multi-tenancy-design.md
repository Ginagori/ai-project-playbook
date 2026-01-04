# Multi-Tenancy Design - Arquitectura desde Día 1

**Cómo construir multi-tenancy correctamente desde el inicio, evitando rewrites costosos**

---

## 📋 Por Qué Multi-Tenancy desde Día 1

### El Problema

**Escenario común:**
1. Construyes SaaS para 1 cliente
2. No implementas multi-tenancy ("no lo necesitamos aún")
3. Consigues cliente #2
4. Te das cuenta: **data está mezclada**, no hay isolación
5. Reescritura completa: 2-3 meses de trabajo

**Costo de NO hacerlo desde día 1:** 10x más caro retrof

itar.

### La Solución

**Construye multi-tenancy SIEMPRE, incluso para 1 tenant:**
- Level 1: Row-Level Security (Postgres RLS)
- Level 2: Namespace Isolation (Vector DB)
- Level 3: Dedicated Infrastructure (Enterprise)

**Tiempo extra inicial:** 2-4 horas
**Tiempo ahorrado después:** Semanas o meses

---

## 🎯 Los 3 Niveles de Multi-Tenancy

### Comparativa Rápida

| Level | Aislamiento | Costo | Cuándo Usar |
|-------|-------------|-------|-------------|
| **Level 1: RLS** | Logical (DB rows) | Bajo | MVP-Growth (0-10K users) |
| **Level 2: Namespaces** | Logical (DB + Vector) | Medio | Growth-Scale (1K-100K) |
| **Level 3: Dedicated** | Physical (infra separada) | Alto | Enterprise (clientes tier-1) |

---

## 🔒 LEVEL 1: Row-Level Security (RLS)

### Concepto

Todos los tenants comparten las mismas tablas, pero **Postgres filtra automáticamente** las rows basado en tenant_id.

### Arquitectura

```
┌─────────────────────────────────────┐
│         Shared Database             │
│  ┌───────────────────────────────┐  │
│  │  users table                  │  │
│  ├─────┬──────────┬──────────────┤  │
│  │ id  │ email    │ tenant_id    │  │
│  ├─────┼──────────┼──────────────┤  │
│  │ 1   │ a@t1.com │ tenant_1     │  ← Tenant 1 solo ve esto
│  │ 2   │ b@t2.com │ tenant_2     │  ← Tenant 2 solo ve esto
│  │ 3   │ c@t1.com │ tenant_1     │  ← Tenant 1 solo ve esto
│  └─────┴──────────┴──────────────┘  │
└─────────────────────────────────────┘

RLS Policy: WHERE tenant_id = current_setting('app.tenant_id')
```

### Implementación en Supabase

**1. Agregar tenant_id a TODAS las tablas:**

```sql
-- Cada tabla necesita tenant_id
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL,
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    content TEXT,
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    user_id UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Tabla maestra de tenants
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    plan TEXT DEFAULT 'free',
    created_at TIMESTAMPTZ DEFAULT now()
);
```

**2. Habilitar RLS:**

```sql
-- Habilitar RLS en TODAS las tablas
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
```

**3. Crear políticas RLS:**

```sql
-- Política para users: solo ve su tenant
CREATE POLICY tenant_isolation_policy ON users
    USING (tenant_id = current_setting('app.tenant_id')::UUID);

-- Política para documents: solo ve su tenant
CREATE POLICY tenant_isolation_policy ON documents
    USING (tenant_id = current_setting('app.tenant_id')::UUID);

-- Política para tenants: solo ve su tenant
CREATE POLICY tenant_isolation_policy ON tenants
    USING (id = current_setting('app.tenant_id')::UUID);
```

**4. Set tenant_id en cada request (Backend):**

```python
# FastAPI example
from fastapi import Depends, Request
from supabase import create_client

async def get_tenant_id(request: Request) -> str:
    """Extract tenant from JWT or subdomain"""
    # Option 1: From JWT claim
    token = request.headers.get("Authorization")
    claims = decode_jwt(token)
    return claims.get("tenant_id")

    # Option 2: From subdomain
    # acme.myapp.com → tenant_id for "acme"
    host = request.headers.get("Host")
    subdomain = host.split(".")[0]
    tenant = get_tenant_by_slug(subdomain)
    return tenant.id

@app.get("/api/documents")
async def list_documents(tenant_id: str = Depends(get_tenant_id)):
    # Set tenant context in Postgres
    supabase.rpc("set_tenant", {"tenant_id": tenant_id})

    # Query automatically filtered by RLS
    docs = supabase.table("documents").select("*").execute()
    return docs.data

# Postgres function to set context
"""
CREATE OR REPLACE FUNCTION set_tenant(tenant_id UUID)
RETURNS void AS $$
BEGIN
    PERFORM set_config('app.tenant_id', tenant_id::TEXT, false);
END;
$$ LANGUAGE plpgsql;
"""
```

### Ventajas
- ✅ Simple de implementar
- ✅ Bajo costo (single database)
- ✅ Fácil de mantener

### Desventajas
- ❌ Single point of failure (1 DB para todos)
- ❌ No performance isolation (tenant ruidoso afecta a otros)
- ❌ No cumple compliance estricto (data físicamente compartida)

### Cuándo Usar
- **MVP - Growth phase** (0-10K usuarios)
- Tenants pequeños/medianos
- No hay clientes enterprise con requisitos de compliance

---

## 🏷️ LEVEL 2: Namespace Isolation

### Concepto

**Postgres:** Usa RLS (Level 1)
**Vector DB:** Cada tenant tiene su propio namespace

### Arquitectura

```
┌──────────────────────┐      ┌──────────────────────┐
│   Shared Postgres    │      │    Pinecone Vector   │
│                      │      │                      │
│  All tenants         │      │  tenant_1 namespace  │
│  (filtered by RLS)   │      │  tenant_2 namespace  │
│                      │      │  tenant_3 namespace  │
└──────────────────────┘      └──────────────────────┘
```

### Implementación en Pinecone

**1. Create index con metadata filtering:**

```python
import pinecone

# Initialize Pinecone
pinecone.init(api_key="your-key", environment="us-west1-gcp")

# Create index (una vez)
pinecone.create_index(
    name="documents",
    dimension=1536,  # OpenAI embeddings
    metric="cosine",
    metadata_config={
        "indexed": ["tenant_id", "user_id", "doc_type"]
    }
)
```

**2. Upsert vectors con tenant_id en metadata:**

```python
from pinecone import Index

index = Index("documents")

# Insert document embeddings
index.upsert(vectors=[
    {
        "id": "doc_1",
        "values": embedding_vector,  # [0.1, 0.2, ..., 0.9]
        "metadata": {
            "tenant_id": "tenant_1",
            "user_id": "user_123",
            "doc_type": "invoice",
            "created_at": "2025-01-15"
        }
    }
])
```

**3. Query con tenant filter automático:**

```python
async def search_documents(query: str, tenant_id: str, top_k: int = 10):
    # Generate query embedding
    query_embedding = get_embedding(query)

    # Search with tenant filter
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        filter={"tenant_id": {"$eq": tenant_id}},  # ← Aislamiento
        include_metadata=True
    )

    return results.matches
```

**4. Namespace approach (Pinecone Serverless):**

```python
# Alternative: Use namespaces (más estricto)
index = Index("documents")

# Insert to tenant-specific namespace
index.upsert(
    vectors=[{
        "id": "doc_1",
        "values": embedding,
        "metadata": {"user_id": "user_123"}
    }],
    namespace=f"tenant_{tenant_id}"  # ← Aislamiento físico
)

# Query from tenant namespace only
results = index.query(
    vector=query_embedding,
    top_k=10,
    namespace=f"tenant_{tenant_id}",  # ← Solo busca en su namespace
    include_metadata=True
)
```

### Ventajas
- ✅ Performance isolation en Vector DB
- ✅ Más seguro que Level 1 solo
- ✅ Costo moderado

### Desventajas
- ❌ Aún single DB en Postgres
- ❌ No cumple compliance enterprise

### Cuándo Usar
- **Growth - Scale phase** (1K-100K usuarios)
- Aplicaciones con RAG/semantic search
- Tenants medianos con performance concerns

---

## 🏢 LEVEL 3: Dedicated Infrastructure

### Concepto

Clientes tier-1 obtienen su propia infraestructura:
- Database dedicada
- Backend pods dedicados (Kubernetes)
- Opcionalmente: región geográfica específica

### Arquitectura

```
┌─────────────────────────────────────────────┐
│            Shared Infrastructure            │
│  ┌────────────┐  ┌────────────┐            │
│  │ Tenant A   │  │ Tenant B   │            │
│  │ (Shared DB)│  │ (Shared DB)│            │
│  └────────────┘  └────────────┘            │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│       Dedicated Infrastructure              │
│  ┌──────────────────────────────────────┐   │
│  │  Tenant C (Enterprise)               │   │
│  │  - Dedicated Cloud SQL instance      │   │
│  │  - Dedicated K8s node pool           │   │
│  │  - Dedicated Vector DB namespace     │   │
│  │  - Custom region (EU for GDPR)       │   │
│  └──────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

### Implementación (Kubernetes)

**1. Tenant routing in ingress:**

```yaml
# kubernetes/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api-ingress
spec:
  rules:
  # Enterprise tenant (dedicated)
  - host: enterprise-client.myapp.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-enterprise-client
            port:
              number: 80

  # Shared tenants
  - host: "*.myapp.com"
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-shared
            port:
              number: 80
```

**2. Dedicated deployment:**

```yaml
# kubernetes/deployment-enterprise.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-enterprise-client
  labels:
    tenant: enterprise-client
    tier: dedicated
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api
      tenant: enterprise-client
  template:
    metadata:
      labels:
        app: api
        tenant: enterprise-client
    spec:
      # Dedicated node pool
      nodeSelector:
        tenant: enterprise-client

      containers:
      - name: api
        image: myapp/api:latest
        env:
        - name: DATABASE_URL
          value: "postgresql://enterprise-db:5432/myapp"
        - name: TENANT_ID
          value: "enterprise-client"
        - name: TIER
          value: "dedicated"
        resources:
          requests:
            cpu: "2"
            memory: "4Gi"
          limits:
            cpu: "4"
            memory: "8Gi"
```

**3. Dedicated database:**

```bash
# Create dedicated Cloud SQL instance
gcloud sql instances create enterprise-client-db \
    --tier=db-n1-standard-4 \
    --region=europe-west1 \
    --database-version=POSTGRES_15 \
    --backup-start-time=03:00 \
    --enable-bin-log \
    --availability-type=REGIONAL
```

### Ventajas
- ✅ Complete isolation (performance, security)
- ✅ Cumple compliance enterprise (SOC 2, HIPAA)
- ✅ Custom SLA por tenant
- ✅ Geographic data residency (GDPR)

### Desventajas
- ❌ Alto costo (+$2K-10K/mes por tenant)
- ❌ Complejidad operacional
- ❌ Requiere Kubernetes knowledge

### Cuándo Usar
- **Enterprise phase**
- Clientes pagando >$10K/mes
- Compliance requirements (HIPAA, SOC 2, FedRAMP)
- SLA >99.99% requerido
- Geographic data residency (GDPR EU, etc.)

---

## 🔀 Hybrid Approach (Recomendado)

### Estrategia

**Mayoría de tenants:** Level 1 + 2 (shared infra)
**Clientes enterprise:** Level 3 (dedicated)

```python
# Routing logic
def get_database_connection(tenant_id: str):
    tenant = get_tenant(tenant_id)

    if tenant.tier == "enterprise":
        # Dedicated database
        return get_connection(tenant.dedicated_db_url)
    else:
        # Shared database with RLS
        conn = get_shared_connection()
        conn.execute(f"SET app.tenant_id = '{tenant_id}'")
        return conn
```

### Costos Ejemplo

**Startup con 50 tenants:**
- 49 tenants en shared infra: $1,500/mes total
- 1 tenant enterprise en dedicated: $3,000/mes
- **Total:** $4,500/mes
- **Revenue de enterprise:** $10,000/mes
- **Profit margin:** Saludable ✅

---

## 📋 Checklist de Implementación

### Día 1 (MVP Setup)
- [ ] Agregar `tenant_id` a tabla `users`
- [ ] Crear tabla `tenants`
- [ ] Habilitar RLS en ambas tablas
- [ ] Crear políticas RLS básicas
- [ ] Test: Crear 2 tenants, verificar aislamiento

### Semana 1 (Completar RLS)
- [ ] Agregar `tenant_id` a TODAS las tablas
- [ ] Habilitar RLS en todas
- [ ] Políticas RLS para cada tabla
- [ ] Backend: Set tenant context en cada request
- [ ] Tests: Verificar no data leakage entre tenants

### Mes 1 (Namespace Isolation)
- [ ] Setup Pinecone con metadata filtering
- [ ] Implementar tenant_id en embeddings
- [ ] Query filtering automático
- [ ] Tests: Verificar vector search isolation

### Cuando sea necesario (Dedicated)
- [ ] Identificar enterprise clients
- [ ] Setup dedicated database
- [ ] Dedicated K8s node pool
- [ ] Migration plan (shared → dedicated)
- [ ] Monitoring específico

---

## ⚠️ Errores Comunes

### Error 1: "Lo agregaremos después"
❌ NO implementar multi-tenancy desde día 1
✅ 2-4 horas extra ahora = semanas ahorradas después

### Error 2: Olvidar RLS en alguna tabla
❌ Habilitar RLS solo en `users`, olvidar `documents`
✅ Checklist: TODAS las tablas con tenant_id + RLS

### Error 3: No testear aislamiento
❌ Asumir que RLS funciona sin verificar
✅ Tests automáticos: User de tenant A NO ve data de tenant B

### Error 4: Tenant ID en JWT inseguro
❌ Permitir que frontend envíe tenant_id (puede mentir)
✅ Tenant ID viene de backend (JWT claim o subdomain lookup)

---

## 🎓 Key Takeaways

1. **Implementa multi-tenancy desde día 1** - Aunque tengas 1 cliente
2. **RLS es tu amigo** - Simple, efectivo, bajo costo
3. **Namespaces para Vector DBs** - Performance isolation importante
4. **Dedicated solo para enterprise** - Alto costo, justifica con revenue
5. **Test isolation** - Data leakage es tu peor pesadilla

---

**Próximos pasos:** Ver [mvp-deployment.md](./mvp-deployment.md) para implementar RLS en tu primer deployment.
