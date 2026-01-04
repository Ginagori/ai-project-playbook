# VetCare SaaS - Global Rules

**Multi-tenant SaaS platform para clínicas veterinarias**

---

## Core Principles

### VERBOSE_NAMING
```python
# BAD
def get_a(id): ...

# GOOD
def get_appointment_by_id(appointment_id: str) -> Appointment: ...
```

### TYPE_SAFETY
```python
# All functions must have type hints
from typing import Optional, List
from datetime import datetime

def create_medical_record(
    pet_id: str,
    vet_id: str,
    diagnosis: str,
    treatment: str,
    notes: Optional[str] = None,
    created_at: datetime = datetime.now()
) -> MedicalRecord:
    ...
```

### AI_FRIENDLY_LOGGING
```python
import structlog

logger = structlog.get_logger()

logger.info(
    "appointment_created",
    appointment_id=appointment.id,
    pet_id=pet.id,
    clinic_id=clinic.id,
    scheduled_at=appointment.scheduled_at.isoformat(),
    fix_suggestion="Check timezone handling if appointment shows wrong time"
)
```

### MULTI_TENANCY_FIRST
```sql
-- Every table MUST have clinic_id (tenant)
CREATE TABLE pets (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    species TEXT NOT NULL,
    clinic_id UUID NOT NULL REFERENCES clinics(id),
    owner_id UUID REFERENCES pet_owners(id)
);

-- RLS policy
ALTER TABLE pets ENABLE ROW LEVEL SECURITY;

CREATE POLICY clinic_isolation ON pets
    USING (clinic_id::TEXT = current_setting('app.clinic_id', true));
```

---

## Tech Stack

- **Language:** Python 3.11+
- **Backend:** FastAPI 0.109+
- **Database:** Supabase (Postgres 15 + RLS)
- **Auth:** Supabase Auth
- **Storage:** Supabase Storage (pet photos, medical records)
- **Frontend:** React 18 + TypeScript
- **State:** Zustand
- **UI:** Tailwind CSS + shadcn/ui
- **Deployment:** Railway (backend) + Netlify (frontend)

---

## Architecture

### Three-Layer Architecture

```
presentation/     # FastAPI routes
├── routes/
│   ├── appointments.py
│   ├── pets.py
│   ├── medical_records.py
│   └── billing.py

business/         # Business logic
├── services/
│   ├── appointment_service.py
│   ├── pet_service.py
│   └── notification_service.py

data/             # Database access
├── repositories/
│   ├── appointment_repo.py
│   ├── pet_repo.py
│   └── base_repo.py
```

### Multi-Tenancy Architecture

```
┌─────────────────────────────────┐
│        Shared Database          │
│  ┌───────────────────────────┐  │
│  │ Clinic A (tenant_1)       │  │
│  │  - 50 pets                │  │
│  │  - 3 vets                 │  │
│  │  - 200 appointments       │  │
│  └───────────────────────────┘  │
│  ┌───────────────────────────┐  │
│  │ Clinic B (tenant_2)       │  │
│  │  - 80 pets                │  │
│  │  - 5 vets                 │  │
│  │  - 350 appointments       │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘

RLS Policies enforce isolation
```

---

## Code Style

### Naming Conventions
- **Files:** `snake_case.py`
- **Classes:** `PascalCase`
- **Functions:** `snake_case`
- **Constants:** `UPPER_SNAKE_CASE`
- **Private:** `_leading_underscore`

### Import Order
```python
# 1. Standard library
import os
from datetime import datetime
from typing import Optional

# 2. Third-party
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from supabase import Client

# 3. Local
from business.services import appointment_service
from data.models import Appointment, Pet
```

### Docstrings
```python
def schedule_appointment(
    pet_id: str,
    vet_id: str,
    scheduled_at: datetime,
    reason: str,
    clinic_id: str
) -> Appointment:
    """
    Schedule a new veterinary appointment.

    Args:
        pet_id: UUID of the pet
        vet_id: UUID of the veterinarian
        scheduled_at: Appointment date/time (UTC)
        reason: Reason for visit
        clinic_id: Clinic tenant ID

    Returns:
        Created Appointment object

    Raises:
        HTTPException: If pet not found, vet not available, or time slot taken
    """
    ...
```

---

## Testing

### Test Structure (Mirror Production)
```
tests/
├── presentation/
│   └── routes/
│       └── test_appointments.py
├── business/
│   └── services/
│       └── test_appointment_service.py
└── data/
    └── repositories/
        └── test_appointment_repo.py
```

### Test Naming
```python
def test_create_appointment_with_valid_data_succeeds():
    """GIVEN valid pet_id, vet_id, and time slot
    WHEN creating appointment
    THEN appointment is created and persisted
    """
    ...

def test_create_appointment_with_taken_slot_fails():
    """GIVEN time slot already taken
    WHEN attempting to create appointment
    THEN HTTPException 409 is raised
    """
    ...
```

### Test Fixtures
```python
@pytest.fixture
def sample_pet(supabase: Client, clinic_id: str):
    """Create test pet"""
    pet_data = {
        "name": "Max",
        "species": "Dog",
        "breed": "Golden Retriever",
        "age": 3,
        "clinic_id": clinic_id,
        "owner_id": "test-owner-id"
    }
    result = supabase.table("pets").insert(pet_data).execute()
    return result.data[0]
```

---

## Common Patterns

### Pattern 1: Multi-Tenant Service

```python
# business/services/appointment_service.py
from data.repositories import AppointmentRepository

class AppointmentService:
    def __init__(self, clinic_id: str):
        self.clinic_id = clinic_id
        self.repo = AppointmentRepository(clinic_id)

    def create(self, pet_id: str, vet_id: str, scheduled_at: datetime) -> Appointment:
        # Validate pet belongs to clinic
        pet = self.repo.get_pet(pet_id)
        if not pet or pet.clinic_id != self.clinic_id:
            raise HTTPException(404, "Pet not found")

        # Validate vet belongs to clinic
        vet = self.repo.get_vet(vet_id)
        if not vet or vet.clinic_id != self.clinic_id:
            raise HTTPException(404, "Vet not found")

        # Check time slot availability
        if not self.repo.is_slot_available(vet_id, scheduled_at):
            raise HTTPException(409, "Time slot not available")

        # Create appointment
        appointment = self.repo.create_appointment({
            "pet_id": pet_id,
            "vet_id": vet_id,
            "scheduled_at": scheduled_at,
            "clinic_id": self.clinic_id,
            "status": "scheduled"
        })

        # Send notification
        self._send_confirmation_email(appointment)

        return appointment
```

### Pattern 2: Repository with RLS

```python
# data/repositories/base_repository.py
from supabase import Client

class BaseRepository:
    def __init__(self, clinic_id: str, supabase: Client):
        self.clinic_id = clinic_id
        self.supabase = supabase

        # Set RLS context
        self.supabase.rpc("set_clinic_context", {"clinic_id": clinic_id}).execute()

    def _ensure_clinic_isolation(self, data: dict) -> dict:
        """Ensure clinic_id is set on all operations"""
        data["clinic_id"] = self.clinic_id
        return data
```

### Pattern 3: FastAPI Route with Auth

```python
# presentation/routes/appointments.py
from fastapi import APIRouter, Depends
from business.services import AppointmentService
from presentation.dependencies import get_current_user, get_clinic_id

router = APIRouter(prefix="/appointments", tags=["appointments"])

@router.post("/", response_model=AppointmentResponse)
async def create_appointment(
    request: CreateAppointmentRequest,
    user = Depends(get_current_user),
    clinic_id: str = Depends(get_clinic_id)
):
    """Create new appointment"""
    service = AppointmentService(clinic_id)
    appointment = service.create(
        pet_id=request.pet_id,
        vet_id=request.vet_id,
        scheduled_at=request.scheduled_at,
        reason=request.reason
    )
    return appointment
```

---

## Database Schema

```sql
-- Clinics (tenants)
CREATE TABLE clinics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    address TEXT,
    plan TEXT DEFAULT 'basic',  -- basic, pro, enterprise
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Pet Owners
CREATE TABLE pet_owners (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id UUID NOT NULL REFERENCES clinics(id),
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Pets
CREATE TABLE pets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id UUID NOT NULL REFERENCES clinics(id),
    owner_id UUID REFERENCES pet_owners(id),
    name TEXT NOT NULL,
    species TEXT NOT NULL,  -- dog, cat, bird, etc.
    breed TEXT,
    age INTEGER,
    weight DECIMAL(5,2),  -- kg
    photo_url TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Veterinarians
CREATE TABLE veterinarians (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id UUID NOT NULL REFERENCES clinics(id),
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    specialization TEXT,
    license_number TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Appointments
CREATE TABLE appointments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id UUID NOT NULL REFERENCES clinics(id),
    pet_id UUID REFERENCES pets(id),
    vet_id UUID REFERENCES veterinarians(id),
    scheduled_at TIMESTAMPTZ NOT NULL,
    duration_minutes INTEGER DEFAULT 30,
    reason TEXT,
    status TEXT DEFAULT 'scheduled',  -- scheduled, completed, cancelled, no-show
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Medical Records
CREATE TABLE medical_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id UUID NOT NULL REFERENCES clinics(id),
    pet_id UUID REFERENCES pets(id),
    vet_id UUID REFERENCES veterinarians(id),
    appointment_id UUID REFERENCES appointments(id),
    diagnosis TEXT NOT NULL,
    treatment TEXT NOT NULL,
    prescriptions TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Enable RLS on all tables
ALTER TABLE pet_owners ENABLE ROW LEVEL SECURITY;
ALTER TABLE pets ENABLE ROW LEVEL SECURITY;
ALTER TABLE veterinarians ENABLE ROW LEVEL SECURITY;
ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;
ALTER TABLE medical_records ENABLE ROW LEVEL SECURITY;

-- Create isolation policies
CREATE POLICY clinic_isolation ON pet_owners USING (clinic_id::TEXT = current_setting('app.clinic_id', true));
CREATE POLICY clinic_isolation ON pets USING (clinic_id::TEXT = current_setting('app.clinic_id', true));
CREATE POLICY clinic_isolation ON veterinarians USING (clinic_id::TEXT = current_setting('app.clinic_id', true));
CREATE POLICY clinic_isolation ON appointments USING (clinic_id::TEXT = current_setting('app.clinic_id', true));
CREATE POLICY clinic_isolation ON medical_records USING (clinic_id::TEXT = current_setting('app.clinic_id', true));
```

---

## Environment Variables

```bash
# .env
ENVIRONMENT=development
DATABASE_URL=postgresql://...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=xxx
JWT_SECRET=xxx
SENDGRID_API_KEY=xxx  # For appointment reminders
```

---

## Feature Flags

```python
# config/features.py
FEATURE_FLAGS = {
    "ENABLE_SMS_REMINDERS": os.getenv("ENABLE_SMS_REMINDERS", "false") == "true",
    "ENABLE_ONLINE_PAYMENTS": os.getenv("ENABLE_ONLINE_PAYMENTS", "false") == "true",
    "ENABLE_TELEMEDICINE": os.getenv("ENABLE_TELEMEDICINE", "false") == "true",
}

# Usage
if FEATURE_FLAGS["ENABLE_SMS_REMINDERS"]:
    send_sms_reminder(appointment)
```

---

**Este CLAUDE.md debe estar siempre loaded. La AI sigue estas reglas automáticamente en cada código que genera.**
