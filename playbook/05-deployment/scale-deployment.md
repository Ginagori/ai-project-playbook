# Scale Deployment - 10K-100K Usuarios

**Kubernetes (GKE) + High Availability + Distributed Tracing**

---

## 🎯 Objetivo

Infraestructura enterprise-grade para 10K-100K usuarios activos.

**Stack:**
- Frontend: Netlify
- Backend: Google Kubernetes Engine (GKE)
- Database: Cloud SQL HA (High Availability)
- Observability: OpenTelemetry + Grafana
- **Costo:** $8,000-15,000/mes

---

## 📋 Pre-requisitos

- [ ] Growth deployment funcionando
- [ ] >10,000 usuarios activos
- [ ] Team con Kubernetes knowledge
- [ ] SLA requirements >99.9%

---

## 🚢 PASO 1: Setup GKE Cluster (1 semana)

### 1.1 Crear Cluster Multi-Zona

```bash
gcloud container clusters create myapp-prod \
  --region us-central1 \
  --num-nodes 3 \
  --machine-type n1-standard-4 \
  --enable-autoscaling \
  --min-nodes 3 \
  --max-nodes 10 \
  --enable-autorepair \
  --enable-autoupgrade \
  --enable-ip-alias \
  --network "default" \
  --subnetwork "default" \
  --addons HorizontalPodAutoscaling,HttpLoadBalancing,GcePersistentDiskCsiDriver

# Connect kubectl
gcloud container clusters get-credentials myapp-prod --region us-central1
```

### 1.2 Deploy Backend

```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
      - name: api
        image: us-central1-docker.pkg.dev/myapp-production/myapp/api:latest
        ports:
        - containerPort: 8080
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        resources:
          requests:
            cpu: "1"
            memory: "2Gi"
          limits:
            cpu: "2"
            memory: "4Gi"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: api
spec:
  selector:
    app: api
  ports:
  - port: 80
    targetPort: 8080
  type: LoadBalancer
```

### 1.3 Auto-Scaling

```yaml
# kubernetes/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

## 🗄️ PASO 2: Cloud SQL High Availability

### 2.1 Upgrade a HA

```bash
gcloud sql instances patch myapp-db \
  --availability-type=REGIONAL \
  --backup-start-time=03:00 \
  --enable-point-in-time-recovery \
  --tier=db-n1-standard-4

# Crea failover replica automáticamente
```

### 2.2 Connection Pooling

```yaml
# kubernetes/pgbouncer.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pgbouncer
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: pgbouncer
        image: edoburu/pgbouncer:latest
        env:
        - name: DATABASE_URL
          value: "postgresql://postgres:PASSWORD@/postgres?host=/cloudsql/myapp-production:us-central1:myapp-db"
        - name: POOL_MODE
          value: "transaction"
        - name: MAX_CLIENT_CONN
          value: "1000"
        - name: DEFAULT_POOL_SIZE
          value: "25"
```

---

## 📊 PASO 3: Observability Stack

### 3.1 OpenTelemetry

```python
# Install
pip install opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation-fastapi

# main.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Setup tracer
trace.set_tracer_provider(TracerProvider())
otlp_exporter = OTLPSpanExporter(endpoint="http://otel-collector:4317")
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_exporter))

# Auto-instrument FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
FastAPIInstrumentor.instrument_app(app)
```

### 3.2 Grafana Dashboard

```yaml
# kubernetes/grafana.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-dashboards
data:
  api-dashboard.json: |
    {
      "dashboard": {
        "title": "API Performance",
        "panels": [
          {
            "title": "Request Rate",
            "targets": [{"expr": "rate(http_requests_total[5m])"}]
          },
          {
            "title": "Error Rate",
            "targets": [{"expr": "rate(http_requests_total{status=~'5..'}[5m])"}]
          },
          {
            "title": "p95 Latency",
            "targets": [{"expr": "histogram_quantile(0.95, http_request_duration_seconds)"}]
          }
        ]
      }
    }
```

---

## 🔄 PASO 4: GitOps con ArgoCD

```yaml
# argocd/application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp-api
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/yourorg/myapp
    targetRevision: HEAD
    path: kubernetes
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
    - CreateNamespace=true
```

---

## 💰 Costos Estimados

| Servicio | Config | Costo/mes |
|----------|--------|-----------|
| GKE Cluster | 3-10 nodes (n1-standard-4) | $4,000-8,000 |
| Cloud SQL HA | db-n1-standard-4 | $500-800 |
| Pinecone | Standard pod | $300 |
| Load Balancer | GCP LB | $200 |
| Monitoring | Grafana Cloud | $500 |
| **Total** | | **$8,000-15,000** |

---

## ✅ Success Criteria

- [ ] 99.9% uptime (measured)
- [ ] p95 latency <200ms
- [ ] Auto-scaling 3-20 pods works
- [ ] Database failover <30s
- [ ] Zero-downtime deployments
- [ ] Full observability (traces, metrics, logs)

---

## 🎓 Key Takeaways

1. **Kubernetes = Control total** pero requiere expertise
2. **HA database = No más outages** por DB failures
3. **Observability = Critical** a esta escala
4. **GitOps = Deployments confiables** y auditable
5. **Costo 10x mayor** que Growth - asegura ROI claro
