# 🔧 Common Patterns - Snippets Reutilizables

Copy-paste patterns para tareas comunes.

## Backend Patterns

### Pattern 1: FastAPI Endpoint con Validación

```python
from fastapi import APIRouter, HTTPException
from app.models.user import User, UserCreate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=User, status_code=201)
def create_user(user: UserCreate, service: UserService = Depends()):
    try:
        return service.create(user)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(500, "Internal server error")
```

### Pattern 2: Service Layer

```python
from sqlalchemy.orm import Session

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, user: UserCreate) -> User:
        # Validation
        if not user.email:
            raise ValueError("Email required")
        
        # Business logic
        db_user = User(**user.dict())
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
```

### Pattern 3: Tests

```python
def test_create_user_success(client):
    response = client.post("/users/", json={
        "email": "test@example.com",
        "name": "Test User"
    })
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"

def test_create_user_invalid_email(client):
    response = client.post("/users/", json={
        "email": "invalid",
        "name": "Test"
    })
    assert response.status_code == 400
```

## Frontend Patterns

### Pattern 1: React Component con Data Fetching

```tsx
import { useState, useEffect } from 'react';

export function UserList() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('/api/users')
      .then(r => r.json())
      .then(setUsers)
      .catch(setError)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <ul>
      {users.map(u => <li key={u.id}>{u.name}</li>)}
    </ul>
  );
}
```

### Pattern 2: Form with Validation

```tsx
import { useForm } from 'react-hook-form';

export function UserForm() {
  const { register, handleSubmit, errors } = useForm();

  const onSubmit = async (data) => {
    const response = await fetch('/api/users', {
      method: 'POST',
      body: JSON.stringify(data)
    });
    if (response.ok) {
      // Success
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('email', { required: true })} />
      {errors.email && <span>Required</span>}
      
      <button type="submit">Submit</button>
    </form>
  );
}
```

## Database Patterns

### Pattern 1: Migration

```python
# alembic revision
def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )

def downgrade():
    op.drop_table('users')
```

## Más Patterns

Ver proyecto-specific patterns en CLAUDE.md sección "Common Patterns"
