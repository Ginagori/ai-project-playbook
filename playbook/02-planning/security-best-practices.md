# Security Best Practices

**🔐 Comprehensive guide to securing your application**

---

## Overview

Security is **non-negotiable** in modern development. This guide covers essential security practices for protecting your application, data, and users.

**Key principle:** Security by default, not as an afterthought.

---

## Table of Contents

1. [Environment Variables & Secrets](#1-environment-variables--secrets)
2. [Authentication & Authorization](#2-authentication--authorization)
3. [Input Validation & Sanitization](#3-input-validation--sanitization)
4. [Common Vulnerabilities (OWASP Top 10)](#4-common-vulnerabilities-owasp-top-10)
5. [API Security](#5-api-security)
6. [Database Security](#6-database-security)
7. [Frontend Security](#7-frontend-security)
8. [Deployment Security](#8-deployment-security)
9. [Monitoring & Incident Response](#9-monitoring--incident-response)
10. [Security Checklist](#10-security-checklist)

---

## 1. Environment Variables & Secrets

### The Problem

**80% of security breaches involve exposed credentials.** Never hardcode secrets in your code.

### Setup: .env Files

**Step 1:** Create `.env.example` (commit to repo)
```bash
# Copy templates/.env.example to your project root
cp templates/.env.example .env.example

# Fill in placeholder values (not real secrets!)
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
JWT_SECRET=your-secret-key-here
OPENAI_API_KEY=sk-...
```

**Step 2:** Create `.env` (NEVER commit!)
```bash
# Copy .env.example to .env
cp .env.example .env

# Fill in REAL values
# This file stays on your machine only
```

**Step 3:** Add `.env` to `.gitignore`
```bash
# Copy templates/.gitignore to your project root
cp templates/.gitignore .gitignore

# Verify .env is ignored
git status  # .env should NOT appear
```

### Loading Environment Variables

**Backend (Python + FastAPI):**
```python
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Access variables
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set in environment")

# Use pydantic for validation
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    jwt_secret: str
    openai_api_key: str

    class Config:
        env_file = ".env"

settings = Settings()  # Raises error if vars missing
```

**Backend (Node.js + Express):**
```javascript
// Load .env file
require('dotenv').config();

// Access variables
const DATABASE_URL = process.env.DATABASE_URL;
if (!DATABASE_URL) {
    throw new Error("DATABASE_URL not set");
}

// Validation with joi or zod
const { z } = require('zod');

const envSchema = z.object({
    DATABASE_URL: z.string().url(),
    JWT_SECRET: z.string().min(32),
    OPENAI_API_KEY: z.string().startsWith('sk-'),
});

const env = envSchema.parse(process.env);
```

**Frontend (Next.js):**
```javascript
// IMPORTANT: Only expose variables with NEXT_PUBLIC_ prefix
// pages/index.js
const apiUrl = process.env.NEXT_PUBLIC_API_URL;

// NEVER do this (exposes secret to client):
// const apiKey = process.env.OPENAI_API_KEY;  // ❌ WRONG!
```

**Frontend (Vite + React):**
```javascript
// Only variables with VITE_ prefix are exposed
const apiUrl = import.meta.env.VITE_API_URL;

// Check .env is loaded
if (!apiUrl) {
    throw new Error("VITE_API_URL not set");
}
```

### Secret Rotation

**API Keys:**
- Rotate every 90 days minimum
- Immediately rotate if exposed (accidental commit, breach)

**How to rotate OpenAI key:**
```bash
# 1. Generate new key at https://platform.openai.com/api-keys
# 2. Update .env with new key
OPENAI_API_KEY=sk-new-key-here

# 3. Test in staging first
npm run test:integration

# 4. Deploy to production
# 5. Delete old key from OpenAI dashboard
```

### Production Secret Management

**DO NOT use .env files in production.** Use managed secret services:

**AWS Secrets Manager:**
```python
import boto3
import json

def get_secret(secret_name):
    client = boto3.client('secretsmanager', region_name='us-east-1')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

# Usage
secrets = get_secret('prod/myapp/database')
DATABASE_URL = secrets['DATABASE_URL']
```

**Google Secret Manager:**
```python
from google.cloud import secretmanager

def get_secret(project_id, secret_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode('UTF-8')

# Usage
DATABASE_URL = get_secret('my-project', 'database-url')
```

**Doppler (simpler alternative):**
```bash
# Install Doppler CLI
curl -Ls https://cli.doppler.com/install.sh | sh

# Login and setup
doppler login
doppler setup

# Run app with secrets injected
doppler run -- python main.py
```

### Common Mistakes to Avoid

❌ **Committing .env to git**
```bash
# Check your git history for exposed secrets
git log --all --full-history -- .env

# If you find .env in history, it's compromised!
# Rotate ALL secrets immediately
```

❌ **Logging secrets**
```python
# NEVER log secrets
logger.info(f"Connecting with key: {api_key}")  # ❌ WRONG!

# Instead
logger.info("Connecting to OpenAI API")  # ✅ Correct
```

❌ **Exposing backend secrets to frontend**
```javascript
// NEVER send secrets to browser
<script>
  const apiKey = "{process.env.OPENAI_API_KEY}";  // ❌ EXPOSED!
</script>
```

---

## 2. Authentication & Authorization

### Authentication (Who are you?)

**Use industry-standard libraries:**

**Backend (Python + FastAPI):**
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Protected route
@app.get("/protected")
def protected_route(user_id: str = Depends(verify_token)):
    return {"message": f"Hello user {user_id}"}
```

**Backend (Node.js + Express):**
```javascript
const jwt = require('jsonwebtoken');

function authMiddleware(req, res, next) {
    const token = req.headers.authorization?.split(' ')[1];

    if (!token) {
        return res.status(401).json({ error: 'No token provided' });
    }

    try {
        const payload = jwt.verify(token, process.env.JWT_SECRET);
        req.userId = payload.userId;
        next();
    } catch (error) {
        return res.status(401).json({ error: 'Invalid token' });
    }
}

// Protected route
app.get('/protected', authMiddleware, (req, res) => {
    res.json({ message: `Hello user ${req.userId}` });
});
```

### Password Hashing

**NEVER store passwords in plain text!**

**Python (using bcrypt):**
```python
import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# Usage
hashed_password = hash_password("user_password_123")
# Store hashed_password in database

# Later, when user logs in
is_valid = verify_password(input_password, stored_hash)
```

**Node.js (using bcrypt):**
```javascript
const bcrypt = require('bcrypt');

async function hashPassword(password) {
    const saltRounds = 10;
    return await bcrypt.hash(password, saltRounds);
}

async function verifyPassword(password, hash) {
    return await bcrypt.compare(password, hash);
}

// Usage
const hashedPassword = await hashPassword("user_password_123");
// Store hashedPassword in database

// Later, when user logs in
const isValid = await verifyPassword(inputPassword, storedHash);
```

### Authorization (What can you do?)

**Role-Based Access Control (RBAC):**

```python
from enum import Enum

class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

def require_role(required_role: Role):
    def decorator(func):
        async def wrapper(*args, user_role: Role = None, **kwargs):
            if user_role != required_role:
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Usage
@app.delete("/users/{user_id}")
@require_role(Role.ADMIN)
async def delete_user(user_id: str):
    # Only admins can delete users
    pass
```

### Session Management

**Security rules:**
1. Use HTTPS only (cookies with `Secure` flag)
2. Set `HttpOnly` flag (prevent XSS)
3. Set `SameSite=Strict` (prevent CSRF)
4. Short session timeout (15-30 min for sensitive apps)
5. Implement logout functionality

```python
from fastapi.responses import JSONResponse

@app.post("/login")
def login(credentials: LoginRequest):
    # Verify credentials...
    token = create_jwt_token(user_id)

    response = JSONResponse({"message": "Logged in"})
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,    # Prevent JavaScript access
        secure=True,      # HTTPS only
        samesite="strict", # CSRF protection
        max_age=1800      # 30 minutes
    )
    return response
```

---

## 3. Input Validation & Sanitization

### Why It Matters

**Rule #1 of security:** Never trust user input.

Every input is a potential attack vector:
- SQL injection
- XSS (Cross-Site Scripting)
- Command injection
- Path traversal

### Backend Validation (Python + Pydantic)

```python
from pydantic import BaseModel, EmailStr, Field, validator

class UserCreate(BaseModel):
    email: EmailStr  # Validates email format
    username: str = Field(min_length=3, max_length=20, regex="^[a-zA-Z0-9_]+$")
    age: int = Field(ge=13, le=120)  # 13-120 years old

    @validator('username')
    def username_must_not_be_reserved(cls, v):
        reserved = ['admin', 'root', 'system']
        if v.lower() in reserved:
            raise ValueError('Username is reserved')
        return v

# Usage
@app.post("/users")
def create_user(user: UserCreate):  # Pydantic validates automatically
    # user.email is guaranteed to be valid email
    # user.username is 3-20 chars, alphanumeric
    pass
```

### Frontend Validation (React + Zod)

```typescript
import { z } from 'zod';

const userSchema = z.object({
    email: z.string().email(),
    username: z.string().min(3).max(20).regex(/^[a-zA-Z0-9_]+$/),
    age: z.number().min(13).max(120),
});

function UserForm() {
    const handleSubmit = (data: FormData) => {
        try {
            const validatedData = userSchema.parse(data);
            // Data is guaranteed to be valid
            submitToAPI(validatedData);
        } catch (error) {
            // Show validation errors
            setErrors(error.errors);
        }
    };
}
```

### Sanitization

**HTML sanitization (prevent XSS):**

```javascript
import DOMPurify from 'isomorphic-dompurify';

// User input that might contain HTML
const userInput = '<script>alert("XSS")</script><p>Hello</p>';

// Sanitize before rendering
const sanitized = DOMPurify.sanitize(userInput);
// Result: '<p>Hello</p>' (script removed)

// Safe to render
<div dangerouslySetInnerHTML={{ __html: sanitized }} />
```

**SQL sanitization (use ORMs!):**

```python
# ❌ NEVER do this (SQL injection risk)
def get_user(user_id: str):
    query = f"SELECT * FROM users WHERE id = '{user_id}'"  # DANGER!
    # Attacker sends: "1' OR '1'='1" -> Returns all users!

# ✅ Use parameterized queries
def get_user(user_id: str):
    query = "SELECT * FROM users WHERE id = %s"
    cursor.execute(query, (user_id,))  # Safe - user_id is escaped

# ✅ Even better: Use ORM
def get_user(user_id: str):
    return db.query(User).filter(User.id == user_id).first()
    # SQLAlchemy handles escaping automatically
```

---

## 4. Common Vulnerabilities (OWASP Top 10)

### 1. SQL Injection

**Attack:**
```python
# Vulnerable code
username = request.form['username']
query = f"SELECT * FROM users WHERE username = '{username}'"
# Attacker input: "admin' --"
# Resulting query: SELECT * FROM users WHERE username = 'admin' --'
# (-- is SQL comment, bypasses password check)
```

**Protection:**
```python
# Use parameterized queries
query = "SELECT * FROM users WHERE username = %s"
cursor.execute(query, (username,))

# Or use ORM
user = db.query(User).filter(User.username == username).first()
```

### 2. Cross-Site Scripting (XSS)

**Attack:**
```javascript
// Vulnerable code
const comment = '<script>stealCookies()</script>';
document.getElementById('comments').innerHTML = comment;  // XSS!
```

**Protection:**
```javascript
// Use textContent instead of innerHTML
element.textContent = userInput;  // Safe - no HTML execution

// Or sanitize HTML
import DOMPurify from 'dompurify';
element.innerHTML = DOMPurify.sanitize(userInput);

// React automatically escapes
<div>{userInput}</div>  // Safe in React
```

### 3. Cross-Site Request Forgery (CSRF)

**Attack:**
Attacker tricks user into making unwanted request while authenticated.

**Protection:**
```python
# Use CSRF tokens
from fastapi_csrf_protect import CsrfProtect

@app.post("/transfer-money")
async def transfer(amount: int, csrf_protect: CsrfProtect = Depends()):
    await csrf_protect.validate_csrf(request)
    # Process transfer
```

### 4. Insecure Deserialization

**Attack:**
```python
# Vulnerable code
import pickle
user_data = pickle.loads(request.data)  # DANGER! Can execute code
```

**Protection:**
```python
# Use safe formats like JSON
import json
user_data = json.loads(request.data)  # Safe

# Or use pydantic for validation
user = UserModel.parse_raw(request.data)
```

### 5. Broken Access Control

**Attack:**
User accesses resources they shouldn't (e.g., editing other users' profiles).

**Protection:**
```python
@app.put("/users/{user_id}/profile")
def update_profile(
    user_id: str,
    profile: ProfileUpdate,
    current_user: User = Depends(get_current_user)
):
    # Verify user can only edit their own profile
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Update profile
    return update_user_profile(user_id, profile)
```

---

## 5. API Security

### Rate Limiting

**Prevent abuse and DoS attacks:**

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/login")
@limiter.limit("5/minute")  # Max 5 login attempts per minute
async def login(request: Request, credentials: LoginRequest):
    # Login logic
    pass
```

### API Key Authentication

```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

@app.get("/protected")
def protected_route(api_key: str = Depends(verify_api_key)):
    return {"message": "Access granted"}
```

### CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",  # Production
        "http://localhost:3000"    # Development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

---

## 6. Database Security

### Row-Level Security (Multi-tenancy)

**Supabase RLS Example:**
```sql
-- Enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own data
CREATE POLICY user_isolation ON users
    USING (id = auth.uid());

-- Policy: Tenants can only see their company's data
CREATE POLICY tenant_isolation ON employees
    USING (company_id::TEXT = current_setting('app.company_id', true));
```

### Prevent SQL Injection

```python
# ❌ NEVER concatenate user input into SQL
def get_users(search_term: str):
    query = f"SELECT * FROM users WHERE name LIKE '%{search_term}%'"  # DANGER!

# ✅ Use parameterized queries
def get_users(search_term: str):
    query = "SELECT * FROM users WHERE name LIKE %s"
    cursor.execute(query, (f"%{search_term}%",))

# ✅ Use ORM
def get_users(search_term: str):
    return db.query(User).filter(User.name.like(f"%{search_term}%")).all()
```

### Database Encryption

**Encrypt sensitive columns:**
```sql
-- Use pgcrypto extension in Postgres
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Encrypt SSN column
INSERT INTO users (name, ssn)
VALUES ('John', pgp_sym_encrypt('123-45-6789', 'encryption_key'));

-- Decrypt when querying
SELECT name, pgp_sym_decrypt(ssn, 'encryption_key') AS ssn
FROM users;
```

---

## 7. Frontend Security

### Content Security Policy (CSP)

```html
<!-- Prevent XSS by restricting resource loading -->
<meta http-equiv="Content-Security-Policy"
      content="default-src 'self';
               script-src 'self' https://trusted-cdn.com;
               style-src 'self' 'unsafe-inline';">
```

### Secure Cookie Handling

```javascript
// Set secure cookies
document.cookie = "session=abc123; Secure; HttpOnly; SameSite=Strict";

// NEVER store sensitive data in localStorage
// localStorage.setItem('api_key', key);  // ❌ WRONG! (accessible via XSS)

// Use httpOnly cookies for tokens instead
```

### Dependency Security

```bash
# Check for vulnerabilities in npm packages
npm audit

# Fix vulnerabilities automatically
npm audit fix

# For Python
pip install safety
safety check
```

---

## 8. Deployment Security

### HTTPS Only

```nginx
# Nginx config: Redirect HTTP to HTTPS
server {
    listen 80;
    server_name example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # Modern TLS only
    ssl_protocols TLSv1.2 TLSv1.3;
}
```

### Security Headers

```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# Add security headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

### Container Security

```dockerfile
# Use minimal base images
FROM python:3.12-slim  # Not 'latest' or 'alpine'

# Don't run as root
RUN useradd -m appuser
USER appuser

# Copy only necessary files
COPY --chown=appuser:appuser . /app

# Scan for vulnerabilities
# docker scan myimage:latest
```

---

## 9. Monitoring & Incident Response

### Logging Security Events

```python
import logging

# Log authentication failures
@app.post("/login")
def login(credentials: LoginRequest):
    user = authenticate(credentials)
    if not user:
        logger.warning(
            "Failed login attempt",
            extra={
                "email": credentials.email,
                "ip": request.client.host,
                "timestamp": datetime.utcnow()
            }
        )
        raise HTTPException(status_code=401, detail="Invalid credentials")

    logger.info(f"Successful login: {user.email}")
    return create_session(user)
```

### Intrusion Detection

```bash
# Use fail2ban to block repeated failed attempts
# /etc/fail2ban/jail.local
[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600  # Ban for 1 hour
```

---

## 10. Security Checklist

### Pre-Launch Checklist

**Environment:**
- [ ] `.env` in `.gitignore`
- [ ] No secrets in code
- [ ] Different secrets per environment (dev/staging/prod)
- [ ] Secrets rotated in last 90 days

**Authentication:**
- [ ] Passwords hashed with bcrypt/argon2
- [ ] JWT tokens with expiration
- [ ] HTTPS only (no HTTP)
- [ ] Session timeout implemented

**Input Validation:**
- [ ] All user inputs validated (backend + frontend)
- [ ] SQL queries parameterized (no string concatenation)
- [ ] HTML sanitized before rendering

**API Security:**
- [ ] Rate limiting enabled
- [ ] CORS configured (not `allow_origins=["*"]`)
- [ ] API authentication required
- [ ] Error messages don't leak info

**Database:**
- [ ] RLS enabled (multi-tenant apps)
- [ ] Backups automated
- [ ] Sensitive data encrypted

**Frontend:**
- [ ] CSP headers set
- [ ] No secrets in client code
- [ ] Dependencies scanned (`npm audit`)
- [ ] XSS protection enabled

**Deployment:**
- [ ] HTTPS enforced (redirect HTTP)
- [ ] Security headers set
- [ ] Containers run as non-root
- [ ] Firewall configured

**Monitoring:**
- [ ] Error tracking (Sentry)
- [ ] Failed login attempts logged
- [ ] Security events monitored
- [ ] Incident response plan documented

---

## Resources

**OWASP:**
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)

**Tools:**
- [npm audit](https://docs.npmjs.com/cli/v8/commands/npm-audit) - Check Node.js dependencies
- [Safety](https://github.com/pyupio/safety) - Check Python dependencies
- [git-secrets](https://github.com/awslabs/git-secrets) - Prevent committing secrets
- [Snyk](https://snyk.io/) - Comprehensive security scanning

**Secret Management:**
- [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/)
- [Google Secret Manager](https://cloud.google.com/secret-manager)
- [HashiCorp Vault](https://www.vaultproject.io/)
- [Doppler](https://www.doppler.com/)

---

**Remember:** Security is a continuous process, not a one-time setup. Review and update regularly.
