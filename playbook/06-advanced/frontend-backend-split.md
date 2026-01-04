# Frontend-Backend Split - Separar Monolito

**Cómo separar fullstack monolito en frontend + backend independientes**

---

## 🎯 Objetivo

Separar monolito en 2 repos/services independientes para escalar separadamente.

**Antes:**
```
monolito/
├── frontend/  (React)
├── backend/   (FastAPI)
└── Deploy juntos
```

**Después:**
```
frontend-repo/  → Deploy a Netlify
backend-repo/   → Deploy a Railway/Cloud Run
```

**Tiempo:** 1-2 semanas

---

## 📋 Cuándo Hacer el Split

**Señales:**
- [ ] Team >5 personas (frontend vs backend devs)
- [ ] Frontend y backend tienen diferentes scaling needs
- [ ] Deploys de uno rompen el otro
- [ ] CI/CD toma >10 minutos (build both)

**NO hagas split si:**
- ❌ Equipo de 1-2 personas
- ❌ App funciona bien en monolito
- ❌ No tienes usuarios que justifiquen complejidad

---

## 🚀 PASO 1: Design API Contract (2 días)

### 1.1 Definir API Endpoints

```typescript
// shared/api-contract.ts
export interface API {
  // Auth
  'POST /auth/login': {
    request: { email: string; password: string }
    response: { token: string; user: User }
  }

  // Users
  'GET /users/me': {
    request: {}
    response: { user: User }
  }

  // Documents
  'GET /documents': {
    request: { limit?: number; offset?: number }
    response: { documents: Document[]; total: number }
  }

  'POST /documents': {
    request: { title: string; content: string }
    response: { document: Document }
  }
}

export interface User {
  id: string
  email: string
  tenant_id: string
}

export interface Document {
  id: string
  title: string
  content: string
  created_at: string
}
```

### 1.2 OpenAPI Spec (Opcional pero Recomendado)

```yaml
# openapi.yaml
openapi: 3.0.0
info:
  title: MyApp API
  version: 1.0.0

paths:
  /auth/login:
    post:
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                email: { type: string }
                password: { type: string }
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  token: { type: string }
                  user: { $ref: '#/components/schemas/User' }

components:
  schemas:
    User:
      type: object
      properties:
        id: { type: string }
        email: { type: string }
        tenant_id: { type: string }
```

---

## 🔧 PASO 2: Split Repos (1 semana)

### 2.1 Crear Backend Repo

```bash
# Nuevo repo
mkdir myapp-backend
cd myapp-backend

# Copy backend code
cp -r ../monolito/backend/* .

# Install dependencies
uv init
uv add fastapi uvicorn supabase pydantic

# Setup CORS
# main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Local dev
        "https://myapp.netlify.app"  # Production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2.2 Crear Frontend Repo

```bash
# Nuevo repo
mkdir myapp-frontend
cd myapp-frontend

# Copy frontend code
cp -r ../monolito/frontend/* .

# Install dependencies
npm install

# Setup API client
# src/lib/api.ts
const API_URL = import.meta.env.VITE_API_URL

export async function fetchAPI<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getToken()}`,
      ...options?.headers
    }
  })

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`)
  }

  return response.json()
}
```

---

## 🔐 PASO 3: Authentication Flow (2-3 días)

### 3.1 JWT Backend

```python
# backend/auth.py
from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthCredentials

SECRET_KEY = os.getenv("JWT_SECRET")
security = HTTPBearer()

def create_token(user_id: str, tenant_id: str) -> str:
    payload = {
        "user_id": user_id,
        "tenant_id": tenant_id,
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(credentials: HTTPAuthCredentials = Depends(security)) -> dict:
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/auth/login")
async def login(email: str, password: str):
    # Verify credentials
    user = authenticate_user(email, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token(user.id, user.tenant_id)
    return {"token": token, "user": user}
```

### 3.2 Frontend Auth

```typescript
// frontend/src/lib/auth.ts
export function setToken(token: string) {
  localStorage.setItem('auth_token', token)
}

export function getToken(): string | null {
  return localStorage.getItem('auth_token')
}

export function removeToken() {
  localStorage.removeItem('auth_token')
}

export async function login(email: string, password: string) {
  const { token, user } = await fetchAPI('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password })
  })

  setToken(token)
  return user
}

export function logout() {
  removeToken()
  window.location.href = '/login'
}
```

---

## 📊 PASO 4: State Management (2 días)

```typescript
// frontend/src/lib/store.ts (usando Zustand)
import create from 'zustand'

interface AppState {
  user: User | null
  documents: Document[]

  setUser: (user: User | null) => void
  fetchDocuments: () => Promise<void>
  createDocument: (title: string, content: string) => Promise<void>
}

export const useStore = create<AppState>((set, get) => ({
  user: null,
  documents: [],

  setUser: (user) => set({ user }),

  fetchDocuments: async () => {
    const { documents } = await fetchAPI<{ documents: Document[] }>('/documents')
    set({ documents })
  },

  createDocument: async (title, content) => {
    const { document } = await fetchAPI<{ document: Document }>('/documents', {
      method: 'POST',
      body: JSON.stringify({ title, content })
    })
    set({ documents: [...get().documents, document] })
  }
}))
```

---

## ✅ PASO 5: Testing & Deployment

### 5.1 Test Locally

```bash
# Terminal 1: Backend
cd myapp-backend
uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd myapp-frontend
npm run dev  # Port 5173

# Test: http://localhost:5173 → API calls to localhost:8000
```

### 5.2 Deploy

```bash
# Backend → Railway
cd myapp-backend
railway init
railway up

# Frontend → Netlify
cd myapp-frontend
# Add VITE_API_URL=https://myapp-backend.railway.app to Netlify env vars
netlify deploy --prod
```

---

## 🎓 Key Takeaways

1. **API contract first** - Define interface antes de split
2. **CORS critical** - Frontend en dominio diferente necesita CORS
3. **JWT for auth** - Stateless auth works best para split
4. **Test local first** - Verifica que funciona antes de deploy
5. **Independent deploy** - Frontend y backend se despliegan separado

**Tiempo total:** 1-2 semanas para split completo y tested.
