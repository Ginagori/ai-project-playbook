# Growth Deployment - Escala a 10,000 Usuarios

**Migración: Railway → Cloud Run | Supabase → Cloud SQL | Auto-scaling habilitado**

---

## 🎯 Objetivo

Manejar 100-10,000 usuarios con auto-scaling y alta disponibilidad.

**Stack:**
- Frontend: Netlify (sin cambios)
- Backend: Google Cloud Run (serverless, auto-scale)
- Database: Cloud SQL + Pinecone
- Monitoring: Sentry + Cloud Logging

**Costo:** $1,500-3,000/mes

---

## 📋 Pre-requisitos

- [ ] MVP funcionando en producción
- [ ] >100 usuarios activos
- [ ] Performance issues evidentes (>2s response time)
- [ ] Google Cloud account con billing habilitado
- [ ] `gcloud` CLI instalado

---

## 🚀 PASO 1: Setup Google Cloud Run (2 horas)

### 1.1 Crear Proyecto GCP

```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Login y crear proyecto
gcloud auth login
gcloud projects create myapp-production --name="My App Production"
gcloud config set project myapp-production

# Habilitar APIs necesarias
gcloud services enable \
  run.googleapis.com \
  sql-component.googleapis.com \
  sqladmin.googleapis.com \
  compute.googleapis.com
```

### 1.2 Dockerizar Backend

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

# Run app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

```yaml
# .dockerignore
__pycache__
*.pyc
.env
.git
.venv
node_modules
```

### 1.3 Build y Push a Artifact Registry

```bash
# Crear Artifact Registry repository
gcloud artifacts repositories create myapp \
  --repository-format=docker \
  --location=us-central1

# Configure Docker auth
gcloud auth configure-docker us-central1-docker.pkg.dev

# Build y push
docker build -t us-central1-docker.pkg.dev/myapp-production/myapp/api:latest .
docker push us-central1-docker.pkg.dev/myapp-production/myapp/api:latest
```

### 1.4 Deploy a Cloud Run

```bash
gcloud run deploy api \
  --image us-central1-docker.pkg.dev/myapp-production/myapp/api:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --min-instances 1 \
  --max-instances 10 \
  --cpu 2 \
  --memory 2Gi \
  --concurrency 80 \
  --timeout 300 \
  --set-env-vars "ENVIRONMENT=production"

# Obtener URL
gcloud run services describe api --region us-central1 --format 'value(status.url)'
# Output: https://api-xxx-uc.a.run.app
```

---

## 🗄️ PASO 2: Migrar a Cloud SQL (3 horas)

### 2.1 Crear Cloud SQL Instance

```bash
gcloud sql instances create myapp-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --storage-type=SSD \
  --storage-size=10GB \
  --storage-auto-increase \
  --backup-start-time=03:00 \
  --enable-bin-log \
  --maintenance-window-day=SUN \
  --maintenance-window-hour=4

# Set password
gcloud sql users set-password postgres \
  --instance=myapp-db \
  --password=STRONG_PASSWORD_HERE
```

### 2.2 Migrar Data desde Supabase

```bash
# 1. Dump desde Supabase
pg_dump "postgresql://postgres:PASSWORD@db.xxx.supabase.co:5432/postgres" \
  --no-owner --no-acl --clean --if-exists \
  -f backup.sql

# 2. Restore a Cloud SQL
gcloud sql import sql myapp-db gs://myapp-backups/backup.sql \
  --database=postgres

# Or via Cloud SQL Proxy:
cloud_sql_proxy -instances=myapp-production:us-central1:myapp-db=tcp:5432 &
psql -h localhost -U postgres -d postgres -f backup.sql
```

### 2.3 Conectar Cloud Run → Cloud SQL

```bash
# Update Cloud Run service
gcloud run services update api \
  --region us-central1 \
  --add-cloudsql-instances myapp-production:us-central1:myapp-db \
  --set-env-vars "DATABASE_URL=postgresql://postgres:PASSWORD@/postgres?host=/cloudsql/myapp-production:us-central1:myapp-db"
```

---

## 🔍 PASO 3: Setup Vector DB (Pinecone) (1 hora)

### 3.1 Crear Index

```python
import pinecone

pinecone.init(api_key=os.getenv("PINECONE_API_KEY"))

pinecone.create_index(
    name="documents",
    dimension=1536,
    metric="cosine",
    pod_type="s1",  # Starter pod
    metadata_config={"indexed": ["tenant_id"]}
)
```

### 3.2 Migrar Embeddings

```python
# Fetch from Supabase vector store
old_vectors = supabase.table("embeddings").select("*").execute()

# Upsert to Pinecone
index = pinecone.Index("documents")
batch_size = 100

for i in range(0, len(old_vectors.data), batch_size):
    batch = old_vectors.data[i:i+batch_size]
    vectors = [(
        item["id"],
        item["embedding"],
        {"tenant_id": item["tenant_id"], "text": item["text"]}
    ) for item in batch]
    index.upsert(vectors=vectors)
```

---

## 📊 PASO 4: Setup Monitoring (1 hora)

### 4.1 Sentry para Error Tracking

```python
# Install
pip install sentry-sdk[fastapi]

# Initialize en main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="https://xxx@xxx.ingest.sentry.io/xxx",
    environment="production",
    traces_sample_rate=0.1,
    integrations=[FastApiIntegration()]
)
```

### 4.2 Cloud Logging

```python
# Install
pip install google-cloud-logging

# Setup
import google.cloud.logging

client = google.cloud.logging.Client()
client.setup_logging()

# Logs automáticamente van a Cloud Console
import logging
logging.info("Request processed", extra={"tenant_id": tenant_id})
```

---

## 🔄 PASO 5: CI/CD con GitHub Actions (1 hora)

```yaml
# .github/workflows/deploy-production.yml
name: Deploy to Cloud Run

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Authenticate to Google Cloud
      uses: google-github-actions/auth@v1
      with:
        credentials_json: ${{ secrets.GCP_SA_KEY }}

    - name: Set up Cloud SDK
      uses: google-github-actions/setup-gcloud@v1

    - name: Build Docker image
      run: |
        gcloud builds submit \
          --tag us-central1-docker.pkg.dev/myapp-production/myapp/api:${{ github.sha }}

    - name: Deploy to Cloud Run
      run: |
        gcloud run deploy api \
          --image us-central1-docker.pkg.dev/myapp-production/myapp/api:${{ github.sha }} \
          --region us-central1 \
          --platform managed
```

---

## 💰 Costos Estimados (Growth Phase)

| Servicio | Configuración | Costo/mes |
|----------|--------------|-----------|
| Netlify | Pro | $49 |
| Cloud Run | 2 vCPU, 2GB, 1-10 instances | $500-1,500 |
| Cloud SQL | db-f1-micro, 10GB | $50-100 |
| Pinecone | Starter pod | $70 |
| Sentry | Team | $26 |
| **Total** | | **$1,500-3,000** |

---

## ✅ Verificación

- [ ] Cloud Run health endpoint responde
- [ ] Database connection funciona (Cloud SQL)
- [ ] Vector search funciona (Pinecone)
- [ ] Auto-scaling probado (load test)
- [ ] CI/CD: Push a main → auto deploy
- [ ] Sentry captura errors
- [ ] Logs visibles en Cloud Console

---

## 📈 Cuándo Migrar a Scale Phase

- [ ] >10,000 usuarios activos
- [ ] Cloud Run hitting max instances (10) regularmente
- [ ] Database CPU >70% sustained
- [ ] Clientes requieren SLA >99.9%
- [ ] Multi-región necesaria

**Próximo paso:** [scale-deployment.md](./scale-deployment.md)

---

## 🎓 Key Takeaways

1. **Cloud Run = Serverless magic** - Auto-scaling sin configurar nada
2. **Cloud SQL > Supabase** - Para 1K+ usuarios
3. **Pinecone namespace isolation** - Multi-tenancy en vector search
4. **Sentry catches everything** - Errors no pasan desapercibidos
5. **CI/CD automático** - Push → Deploy en 5 minutos
