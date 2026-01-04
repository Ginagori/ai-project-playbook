# MVP Deployment - Despliega en 2-4 Horas

**Setup completo: Netlify + Railway + Supabase para 0-100 usuarios**

---

## 🎯 Objetivo

Tener tu app live en producción en 2-4 horas, gastando $300-500/mes.

**Stack:**
- Frontend: Netlify (CDN global, SSL gratis)
- Backend: Railway (deploy con git push)
- Database: Supabase (Postgres + Auth + Storage)

---

## ✅ Pre-requisitos

- [ ] Código en GitHub (frontend + backend separados o monorepo)
- [ ] Cuentas creadas: Netlify, Railway, Supabase
- [ ] Environment variables documentadas

---

## 🚀 PASO 1: Deploy Frontend a Netlify (5 min)

### 1.1 Conectar GitHub

1. Ve a [app.netlify.com](https://app.netlify.com)
2. Click "Add new site" → "Import an existing project"
3. Selecciona GitHub → Autoriza → Elige repo

### 1.2 Configurar Build

```yaml
# netlify.toml
[build]
  command = "npm run build"
  publish = "dist"  # o "build" para Create React App

[build.environment]
  NODE_VERSION = "20"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

### 1.3 Deploy

1. Click "Deploy site"
2. Espera 2-3 minutos
3. Tu sitio está live: `https://random-name-123.netlify.app`

### 1.4 Custom Domain (Opcional)

1. Compra dominio (Namecheap, Google Domains)
2. Netlify → Domain settings → Add custom domain
3. Agrega DNS records:
   ```
   Type: A
   Name: @
   Value: 75.2.60.5

   Type: CNAME
   Name: www
   Value: random-name-123.netlify.app
   ```

---

## 🔧 PASO 2: Deploy Backend a Railway (10 min)

### 2.1 Crear Proyecto

1. Ve a [railway.app](https://railway.app)
2. "New Project" → "Deploy from GitHub repo"
3. Selecciona tu backend repo

### 2.2 Configurar Service

```yaml
# Railway detecta automáticamente:
# - Python → Instala dependencies de requirements.txt
# - Node.js → Ejecuta npm install

# Pero puedes customizar con railway.toml:
[build]
  builder = "NIXPACKS"

[deploy]
  startCommand = "uvicorn main:app --host 0.0.0.0 --port $PORT"
  restartPolicyType = "ON_FAILURE"
  restartPolicyMaxRetries = 10
```

### 2.3 Environment Variables

```bash
# Railway Dashboard → Variables tab
DATABASE_URL=postgresql://...  # Vendrá de Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJhb...
OPENAI_API_KEY=sk-...
ENVIRONMENT=production
```

### 2.4 Obtener URL

Railway genera URL automática:
```
https://your-app-production.up.railway.app
```

---

## 🗄️ PASO 3: Setup Database en Supabase (10 min)

### 3.1 Crear Proyecto

1. Ve a [supabase.com](https://supabase.com)
2. "New project"
3. Nombre: `myapp-production`
4. Database password: Usa generador seguro
5. Region: `US West (Oregon)` o más cercana

### 3.2 Crear Tablas con RLS

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tenants table
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    plan TEXT DEFAULT 'free',
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Users table (multi-tenant)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT NOT NULL UNIQUE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Documents table (example)
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    content TEXT,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY tenant_isolation ON users
    USING (tenant_id::TEXT = current_setting('app.tenant_id', true));

CREATE POLICY tenant_isolation ON documents
    USING (tenant_id::TEXT = current_setting('app.tenant_id', true));
```

### 3.3 Copiar Credentials

```bash
# Supabase Dashboard → Settings → API
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGc...  # Public key (frontend)
SUPABASE_SERVICE_KEY=eyJhbGc...  # Secret key (backend only)

# Database URL
postgresql://postgres:[PASSWORD]@db.xxxxx.supabase.co:5432/postgres
```

---

## 🔗 PASO 4: Conectar Todo (5 min)

### 4.1 Backend → Database

Agrega en Railway env vars:
```bash
DATABASE_URL=postgresql://postgres:PASSWORD@db.xxxxx.supabase.co:5432/postgres
```

Test conexión:
```python
# main.py
from supabase import create_client
import os

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

@app.get("/health")
def health_check():
    # Test DB connection
    result = supabase.table("tenants").select("count").execute()
    return {"status": "healthy", "db": "connected"}
```

### 4.2 Frontend → Backend

```javascript
// frontend/.env.production
VITE_API_URL=https://your-app-production.up.railway.app
VITE_SUPABASE_URL=https://xxxxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGc...
```

Rebuild en Netlify:
```bash
# Netlify dashboard → Deploys → Trigger deploy
```

### 4.3 CORS Configuration

```python
# backend/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourapp.netlify.app",
        "https://yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## ✅ PASO 5: Verificación (5 min)

### 5.1 Smoke Tests

- [ ] Frontend carga: `https://yourapp.netlify.app`
- [ ] Backend health: `https://...railway.app/health`
- [ ] Database query funciona
- [ ] Auth flow (login/signup)
- [ ] Create/Read/Update/Delete de data

### 5.2 Monitoring Básico

**Railway Logs:**
```bash
# Railway dashboard → Logs tab
# Busca errors, warnings
```

**Supabase Logs:**
```bash
# Supabase → Logs → Postgres Logs
# Verifica queries lentas, errors
```

**Netlify Deploy:**
```bash
# Netlify → Deploys → Ver build logs
# Asegura que build fue exitoso
```

---

## 💰 Costos Estimados

| Servicio | Plan | Costo/mes |
|----------|------|-----------|
| Netlify | Starter | $19 |
| Railway | Hobby | $25 (500 horas) |
| Supabase | Free → Pro | $0-25 |
| **Total** | | **$44-69** |

**Nota:** Con traffic real, espera $300-500/mes (Railway scaling, Supabase storage).

---

## 🔄 CI/CD Automático (Bonus)

**Netlify:** Ya está configurado (git push → auto deploy)

**Railway:** Ya está configurado (git push → auto deploy)

**Result:** Push a `main` branch → Deploy automático en 3-5 minutos ✅

---

## 📊 Límites del MVP

**Cuándo necesitas actualizar a Growth:**

- [ ] >100 usuarios activos diarios
- [ ] Backend response time >2 segundos
- [ ] Railway crashea por out-of-memory
- [ ] Database >500MB (Supabase free limit)
- [ ] Necesitas auto-scaling

**Próximo paso:** [growth-deployment.md](./growth-deployment.md)

---

## ⚠️ Troubleshooting

### Frontend no conecta a backend

**Problema:** CORS error en console
**Solución:** Verifica `allow_origins` en backend incluye Netlify URL

### Database connection fails

**Problema:** `connection refused`
**Solución:**
1. Verifica DATABASE_URL correcto
2. Supabase → Settings → Database → Connection pooling enabled
3. Railway → Restart service

### Deploy fails en Netlify

**Problema:** Build error
**Solución:**
1. Verifica `netlify.toml` build command
2. Revisa build logs para error específico
3. Test local: `npm run build`

---

## 🎓 Key Takeaways

1. **MVP deployment es simple** - 2-4 horas total
2. **Multi-tenancy desde día 1** - RLS configurado ✅
3. **Auto-deploy configured** - Push → Production automático
4. **Monitoring básico** - Logs accesibles en dashboards
5. **Costo predecible** - $300-500/mes para 0-100 usuarios

---

**¿Listo para escalar?** Cuando llegues a 100+ usuarios, lee [growth-deployment.md](./growth-deployment.md) para migrar a Cloud Run + Cloud SQL.
