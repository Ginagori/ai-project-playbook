# Guía Completa de Vertical Slice Architecture

> **Fuente:** Artículo de Rasmus Widing, adaptado para el AI Project Playbook
> **Aplicable a:** Todos los proyectos (MVP → Enterprise)

---

## 💡 La Idea Central

**La parte más difícil no es entender la teoría - es saber DÓNDE PONER LAS COSAS.**

- ¿Dónde va la configuración de base de datos?
- ¿Qué pasa con el logging?
- Si construyes un agente AI, ¿dónde pones el cliente de OpenAI?
- ¿Qué código está bien duplicar y cuál debe seguir DRY?

Esta guía responde estas preguntas con ejemplos concretos.

---

## La Paradoja del Setup: Infraestructura Antes de Features

VSA organiza por features, pero antes de tener features, necesitas infraestructura:
- Database connections
- Logging
- Configuration
- API clients

**La solución:** Una estructura pragmática que balancea pureza con practicidad.

```
my-fastapi-app/
├── app/
│   ├── core/              # Infraestructura fundacional
│   ├── shared/            # Utilidades cross-feature
│   ├── products/          # Feature slice
│   ├── inventory/         # Feature slice
│   └── categories/        # Feature slice
├── tests/
├── .env
├── pyproject.toml
└── README.md
```

---

## El Directorio `core/`: Fundación de tu Aplicación

El `core/` contiene infraestructura que existe **ANTES** de features y es **UNIVERSAL** en toda la aplicación.

> **Regla de oro:** Si remover un feature slice todavía requeriría este código, va en `core/`.

### Estructura de `core/`

```
app/core/
├── __init__.py
├── config.py              # Configuración de aplicación
├── database.py            # Conexión y session management
├── logging.py             # Setup de logging
├── middleware.py          # Request/response middleware
├── exceptions.py          # Clases base de excepciones
├── dependencies.py        # Dependencias globales de FastAPI
├── events.py              # Eventos de lifecycle de aplicación
├── cache.py               # Setup de cliente Redis (opcional)
├── worker.py              # Configuración Celery/background jobs (opcional)
├── health.py              # Health check implementations (opcional)
├── rate_limit.py          # Rate limiting utilities (opcional)
├── feature_flags.py       # Feature flag management (opcional)
└── uow.py                 # Unit of Work pattern (opcional)
```

### Ejemplo: `core/config.py`

```python
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application-wide configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # Application
    app_name: str = "My FastAPI App"
    debug: bool = False
    version: str = "1.0.0"

    # Database
    database_url: str

    # Observability
    log_level: str = "INFO"
    enable_metrics: bool = True

    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
```

**Por qué importa para AI:** Configuración centralizada = single source of truth. El agente no gasta tokens buscando settings esparcidos.

### Ejemplo: `core/database.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.core.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Decisión clave:** Database setup va en `core/` porque es infraestructura universal. Los models individuales van en sus propios feature slices.

### Ejemplo: `core/logging.py`

```python
import logging
import structlog
from typing import Any
from contextvars import ContextVar
import uuid

from app.core.config import get_settings

# Context variable for request correlation ID
request_id_var: ContextVar[str] = ContextVar("request_id", default="")


def get_request_id() -> str:
    """Get the current request ID from context."""
    return request_id_var.get()


def set_request_id(request_id: str | None = None) -> str:
    """Set request ID in context, generating one if not provided."""
    if not request_id:
        request_id = str(uuid.uuid4())
    request_id_var.set(request_id)
    return request_id


def add_request_id(logger, method_name, event_dict):
    """Processor to add request ID to all log entries."""
    request_id = get_request_id()
    if request_id:
        event_dict["request_id"] = request_id
    return event_dict


def setup_logging() -> None:
    """Configure structured logging for the application."""
    settings = get_settings()

    structlog.configure(
        processors=[
            add_request_id,
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(settings.log_level)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> Any:
    """Get a logger instance for a module."""
    return structlog.get_logger(name)
```

**Crítico para AI agents:** El `format_exc_info` processor formatea stack traces como strings en JSON. Cuando usas `exc_info=True`, los agentes AI obtienen el stack trace completo parseable.

**Ejemplo de output:**

```json
{
  "event": "product.create.failed",
  "sku": "TEST-001",
  "error": "IntegrityError: duplicate key value",
  "exception": "Traceback (most recent call last):\n  File \"/app/products/service.py\", line 45...",
  "level": "error",
  "timestamp": "2025-01-15T14:23:45.123Z"
}
```

### Ejemplo: `core/middleware.py`

```python
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from typing import Callable
import time

from app.core.logging import set_request_id, get_logger

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging with correlation ID."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get("X-Request-ID")
        set_request_id(request_id)

        start_time = time.time()
        logger.info(
            "request.started",
            method=request.method,
            path=request.url.path,
            client_host=request.client.host if request.client else None,
        )

        try:
            response = await call_next(request)
            duration = time.time() - start_time
            logger.info(
                "request.completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_seconds=round(duration, 3),
            )
            response.headers["X-Request-ID"] = get_request_id()
            return response

        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                "request.failed",
                method=request.method,
                path=request.url.path,
                error=str(e),
                duration_seconds=round(duration, 3),
                exc_info=True,
            )
            raise


def setup_cors(app):
    """Configure CORS middleware."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def setup_middleware(app):
    """Configure all middleware for the application."""
    app.add_middleware(RequestLoggingMiddleware)
    setup_cors(app)
```

---

## El Directorio `shared/`: Utilidades Cross-Feature

El `shared/` es para código que **múltiples features usan** pero no es infraestructura fundacional. Esta es la zona gris que causa más confusión.

> **Regla de decisión:** Código se mueve a `shared/` cuando **3 o más** feature slices lo necesitan. Hasta entonces, duplica.

### Estructura de `shared/`

```
app/shared/
├── __init__.py
├── models.py              # Base models, mixins (ej: TimestampMixin)
├── schemas.py             # Schemas comunes (ej: PaginationParams)
├── utils.py               # Utilidades genéricas
├── validators.py          # Validadores reutilizables
├── responses.py           # Formatos estándar de respuesta API
├── events.py              # Domain events y event bus
├── tasks.py               # Background tasks cross-feature
└── integrations/          # Clientes de APIs externas (3+ features)
    ├── __init__.py
    ├── email.py           # SendGrid, SES, etc.
    ├── storage.py         # S3, GCS, etc.
    └── payment.py         # Stripe, PayPal, etc.
```

### Ejemplo: `shared/models.py`

```python
from datetime import datetime
from sqlalchemy import Column, DateTime
from sqlalchemy.ext.declarative import declared_attr


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""

    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=datetime.utcnow, nullable=False)

    @declared_attr
    def updated_at(cls):
        return Column(
            DateTime,
            default=datetime.utcnow,
            onupdate=datetime.utcnow,
            nullable=False
        )
```

**Por qué shared:** Todos los database models necesitan timestamps. Es comportamiento genuinamente compartido.

### Ejemplo: `shared/schemas.py`

```python
from pydantic import BaseModel, Field
from typing import Generic, TypeVar, List

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Standard pagination parameters."""
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated response format."""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
```

**Por qué shared:** Cada feature que lista items usa paginación igual. Interfaz común, código común.

---

## Feature Slices: Donde Vive tu Business Logic

Cada feature slice es auto-contenido. TODO lo necesario para entender y modificar esa feature vive en su directorio.

### Estructura Completa de Feature

```
app/products/
├── __init__.py
├── routes.py              # FastAPI endpoints
├── service.py             # Business logic
├── repository.py          # Database operations
├── models.py              # SQLAlchemy models
├── schemas.py             # Pydantic request/response models
├── validators.py          # Feature-specific validation
├── exceptions.py          # Feature-specific exceptions
├── dependencies.py        # Feature-specific dependencies
├── constants.py           # Feature-specific constants
├── types.py               # Feature-specific type definitions
├── cache.py               # Caching logic (opcional)
├── tasks.py               # Background tasks (opcional)
├── storage.py             # File operations (opcional)
├── cli.py                 # CLI commands (opcional)
├── config.py              # Feature config (opcional, si 5+ settings)
├── test_routes.py         # Endpoint tests
├── test_service.py        # Business logic tests
└── README.md              # Feature documentation
```

**No toda feature necesita todos los archivos.** Empieza con `routes.py`, `service.py`, y `schemas.py`. Agrega otros según necesites.

### Ejemplo Completo: Feature de Productos

**`products/models.py`**

```python
from sqlalchemy import Column, Integer, String, Numeric, Boolean, Text
from app.core.database import Base
from app.shared.models import TimestampMixin


class Product(Base, TimestampMixin):
    """Product database model."""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
```

**`products/schemas.py`**

```python
from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime


class ProductBase(BaseModel):
    """Shared product attributes."""
    name: str = Field(..., min_length=1, max_length=200)
    sku: str = Field(..., min_length=1, max_length=50)
    description: str | None = None
    price: Decimal = Field(..., gt=0)


class ProductCreate(ProductBase):
    """Schema for creating a product."""
    pass


class ProductUpdate(BaseModel):
    """Schema for updating a product (all fields optional)."""
    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    price: Decimal | None = Field(None, gt=0)
    is_active: bool | None = None


class ProductResponse(ProductBase):
    """Schema for product responses."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
```

**`products/repository.py`**

```python
from sqlalchemy.orm import Session
from typing import List, Optional

from app.products.models import Product
from app.products.schemas import ProductCreate, ProductUpdate


class ProductRepository:
    """Data access layer for products."""

    def __init__(self, db: Session):
        self.db = db

    def get(self, product_id: int) -> Optional[Product]:
        """Get product by ID."""
        return self.db.query(Product).filter(Product.id == product_id).first()

    def get_by_sku(self, sku: str) -> Optional[Product]:
        """Get product by SKU."""
        return self.db.query(Product).filter(Product.sku == sku).first()

    def list(self, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[Product]:
        """List products with pagination."""
        query = self.db.query(Product)
        if active_only:
            query = query.filter(Product.is_active == True)
        return query.offset(skip).limit(limit).all()

    def create(self, product_data: ProductCreate) -> Product:
        """Create a new product."""
        product = Product(**product_data.model_dump())
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def update(self, product: Product, product_data: ProductUpdate) -> Product:
        """Update an existing product."""
        update_data = product_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)
        self.db.commit()
        self.db.refresh(product)
        return product

    def delete(self, product: Product) -> None:
        """Delete a product (hard delete)."""
        self.db.delete(product)
        self.db.commit()
```

**`products/service.py`**

```python
from sqlalchemy.orm import Session
from typing import List

from app.products.repository import ProductRepository
from app.products.schemas import ProductCreate, ProductUpdate, ProductResponse
from app.products.exceptions import ProductNotFoundError, ProductAlreadyExistsError
from app.core.logging import get_logger

logger = get_logger(__name__)


class ProductService:
    """Business logic for products."""

    def __init__(self, db: Session):
        self.repository = ProductRepository(db)

    def get_product(self, product_id: int) -> ProductResponse:
        """Get a product by ID."""
        logger.info("product.get.started", product_id=product_id)

        product = self.repository.get(product_id)
        if not product:
            logger.warning("product.get.not_found", product_id=product_id)
            raise ProductNotFoundError(f"Product {product_id} not found")

        return ProductResponse.model_validate(product)

    def list_products(self, skip: int = 0, limit: int = 100) -> List[ProductResponse]:
        """List active products."""
        logger.info("product.list.started", skip=skip, limit=limit)

        products = self.repository.list(skip=skip, limit=limit)
        return [ProductResponse.model_validate(p) for p in products]

    def create_product(self, product_data: ProductCreate) -> ProductResponse:
        """Create a new product."""
        logger.info("product.create.started", sku=product_data.sku, name=product_data.name)

        existing = self.repository.get_by_sku(product_data.sku)
        if existing:
            logger.warning("product.create.duplicate_sku", sku=product_data.sku)
            raise ProductAlreadyExistsError(f"Product with SKU {product_data.sku} already exists")

        product = self.repository.create(product_data)
        logger.info("product.create.completed", product_id=product.id, sku=product.sku)

        return ProductResponse.model_validate(product)

    def update_product(self, product_id: int, product_data: ProductUpdate) -> ProductResponse:
        """Update a product."""
        logger.info("product.update.started", product_id=product_id)

        product = self.repository.get(product_id)
        if not product:
            raise ProductNotFoundError(f"Product {product_id} not found")

        updated_product = self.repository.update(product, product_data)
        logger.info("product.update.completed", product_id=product_id)

        return ProductResponse.model_validate(updated_product)

    def delete_product(self, product_id: int) -> None:
        """Delete a product."""
        logger.info("product.delete.started", product_id=product_id)

        product = self.repository.get(product_id)
        if not product:
            raise ProductNotFoundError(f"Product {product_id} not found")

        self.repository.delete(product)
        logger.info("product.delete.completed", product_id=product_id)
```

**`products/exceptions.py`**

```python
class ProductError(Exception):
    """Base exception for product-related errors."""
    pass


class ProductNotFoundError(ProductError):
    """Raised when a product is not found."""
    pass


class ProductAlreadyExistsError(ProductError):
    """Raised when attempting to create a product with duplicate SKU."""
    pass
```

**`products/routes.py`**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.products.service import ProductService
from app.products.schemas import ProductCreate, ProductUpdate, ProductResponse
from app.products.exceptions import ProductNotFoundError, ProductAlreadyExistsError
from app.shared.schemas import PaginationParams

router = APIRouter(prefix="/products", tags=["products"])


def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    """Dependency to get ProductService instance."""
    return ProductService(db)


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    service: ProductService = Depends(get_product_service)
):
    """Create a new product."""
    try:
        return service.create_product(product_data)
    except ProductAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    service: ProductService = Depends(get_product_service)
):
    """Get a product by ID."""
    try:
        return service.get_product(product_id)
    except ProductNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/", response_model=List[ProductResponse])
def list_products(
    pagination: PaginationParams = Depends(),
    service: ProductService = Depends(get_product_service)
):
    """List products with pagination."""
    return service.list_products(skip=pagination.offset, limit=pagination.page_size)


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    service: ProductService = Depends(get_product_service)
):
    """Update a product."""
    try:
        return service.update_product(product_id, product_data)
    except ProductNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    service: ProductService = Depends(get_product_service)
):
    """Delete a product."""
    try:
        service.delete_product(product_id)
    except ProductNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
```

**Por qué esta estructura funciona para AI:**

- Todo el código de productos está en un lugar
- AI puede cargar `products/` y entender toda la feature
- Separación clara: routes → service → repository → database
- Cada archivo tiene una responsabilidad única y clara

---

## Matriz de Decisión: Duplicación vs DRY

Esta es la pregunta con la que todos luchan: "¿Debo extraer esto a shared, o duplicarlo?"

### Cuándo Duplicar (Preferir Coupling a Feature)

**Duplica cuando:**

| Situación | Ejemplo |
|-----------|---------|
| **Usado por 1-2 features** | Espera hasta que la tercera feature lo necesite |
| **Existen variaciones** | Si features necesitan comportamiento diferente, no fuerces abstracción |
| **Lógica feature-specific** | Aunque el código se vea similar, si resuelve problemas diferentes, mantenlo separado |
| **Estabilidad incierta** | Si requisitos podrían cambiar independientemente por feature, duplica |

**Ejemplo: Lógica de validación**

```python
# products/validators.py
def validate_price(price: Decimal) -> Decimal:
    """Validate product price is positive and has max 2 decimal places."""
    if price <= 0:
        raise ValueError("Price must be positive")
    if price.as_tuple().exponent < -2:
        raise ValueError("Price cannot have more than 2 decimal places")
    return price

# inventory/validators.py
def validate_quantity(quantity: int) -> int:
    """Validate inventory quantity is non-negative."""
    if quantity < 0:
        raise ValueError("Quantity cannot be negative")
    return quantity
```

**Por qué duplicar:** Estos resuelven problemas diferentes. Extraer a `shared/validators.py` crearía coupling entre features no relacionadas.

### Cuándo Extraer a Shared (DRY Gana)

**Extrae cuando:**

| Situación | Ejemplo |
|-----------|---------|
| **Usado por 3+ features** | Patrón claro de reuso |
| **Lógica idéntica** | Sin variaciones entre features |
| **Nivel de infraestructura** | Database mixins, base schemas, auth helpers |
| **Interfaz estable** | No necesitará modificaciones feature-specific |

**Ejemplo: Utilidades de fecha**

```python
# shared/utils.py
from datetime import datetime, timezone

def utcnow() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)

def format_iso(dt: datetime) -> str:
    """Format datetime as ISO 8601 string."""
    return dt.isoformat()
```

**Por qué shared:** Cada feature necesita manejo de fechas consistente. Sin variaciones feature-specific.

### La Regla de las Tres Features

> **Regla:** Cuando te encuentres escribiendo el mismo código por tercera vez, extráelo a `shared/`.

**Por qué tres?**

- Una instancia: específico de esa feature
- Dos instancias: podría ser coincidencia
- Tres instancias: patrón probado que vale abstraer

**Proceso:**

1. Primera feature: Escribe el código inline
2. Segunda feature: Duplica (agrega comentario notando duplicación)
3. Tercera feature: Extrae a `shared/` y refactoriza las tres features

Esto previene abstracción prematura mientras captura comportamiento genuinamente compartido.

---

## Infraestructura para AI Agents: LLM Clients

Si construyes un agente AI o app LLM-powered, necesitas infraestructura adicional.

### Opción 1: En `core/` (apps pequeñas)

```python
# core/llm.py
from anthropic import Anthropic
from openai import OpenAI
from functools import lru_cache

from app.core.config import get_settings


@lru_cache()
def get_anthropic_client() -> Anthropic:
    """Get cached Anthropic client."""
    settings = get_settings()
    return Anthropic(api_key=settings.anthropic_api_key)


@lru_cache()
def get_openai_client() -> OpenAI:
    """Get cached OpenAI client."""
    settings = get_settings()
    return OpenAI(api_key=settings.openai_api_key)
```

**Usar cuando:** Tu app entera es un agente AI, y LLM calls son universales.

### Opción 2: Módulo dedicado `llm/` (apps grandes)

```
app/llm/
├── __init__.py
├── clients.py             # LLM client initialization
├── prompts.py             # Centralized prompt management
├── tools.py               # Tool/function definitions
├── messages.py            # Message formatting utilities
└── schemas.py             # LLM-specific Pydantic schemas
```

**Usar cuando:** Múltiples features usan LLMs de forma diferente, o tienes necesidades complejas de prompt management.

---

## Resumen de Reglas de Decisión

### ¿Dónde va este código?

| Pregunta | Si SÍ → | Si NO → |
|----------|---------|---------|
| ¿Existiría sin ninguna feature? | `core/` | Siguiente pregunta |
| ¿Lo usan 3+ features idénticamente? | `shared/` | Siguiente pregunta |
| ¿Es específico de una feature? | `feature/` | Probablemente `shared/` |

### Checklist Rápido

- [ ] **Infraestructura universal** → `core/`
- [ ] **Usado 1-2 veces** → Duplicar en cada feature
- [ ] **Usado 3+ veces idénticamente** → `shared/`
- [ ] **Lógica de negocio de feature** → `feature/`
- [ ] **LLM clients para toda la app** → `core/` o `llm/`
- [ ] **Integraciones externas (3+ features)** → `shared/integrations/`

---

## Conclusión

VSA no es solo una estructura de carpetas. Es una **filosofía de organización** que:

1. **Aísla contexto** - Cada feature es auto-contenida
2. **Reduce navegación** - AI y humanos encuentran código rápido
3. **Previene coupling** - Features no dependen unas de otras
4. **Escala naturalmente** - Agregar features no complica existentes

**La estructura correcta hace que el código se escriba solo - tanto para ti como para tus agentes AI.**
