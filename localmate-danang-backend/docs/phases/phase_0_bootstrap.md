# **PHASE 0 – Project Bootstrap**

## 🎯 Mục tiêu
Có hệ thống FastAPI + Postgres + Neo4j chạy ổn định.  
**Chưa cần logic AI.**

---

## 📦 Deliverables

| Item | Path | Description |
|------|------|-------------|
| FastAPI Entry | `app/main.py` | Entry point với basic health check |
| Settings | `app/core/config.py` | Pydantic BaseSettings |
| DB Session | `app/shared/db/session.py` | AsyncSession + engine |
| Base Model | `app/shared/models/base.py` | SQLAlchemy Base + TimestampMixin |
| User Model | `app/shared/models/user_models.py` | User table |
| Itinerary Models | `app/shared/models/itinerary_models.py` | Itinerary + ItineraryStop |
| Neo4j Client | `app/shared/integrations/neo4j_client.py` | Basic Neo4j wrapper |
| Alembic Config | `alembic.ini` + `app/shared/db/migrations/` | Migration setup |

---

## 📋 Tasks Chi tiết

### Task 0.1: Khởi tạo Project Structure

**Files cần tạo:**

```
localmate-danang-backend/
├─ README.md
├─ pyproject.toml
├─ alembic.ini
├─ .env.example
└─ app/
   └─ __init__.py
```

**Steps:**
1. Tạo `pyproject.toml` với dependencies:
   ```toml
   [project]
   name = "localmate-backend"
   version = "0.1.0"
   dependencies = [
       "fastapi>=0.104.0",
       "uvicorn[standard]>=0.24.0",
       "sqlalchemy>=2.0.0",
       "asyncpg>=0.29.0",
       "alembic>=1.12.0",
       "pydantic>=2.5.0",
       "pydantic-settings>=2.1.0",
       "neo4j>=5.14.0",
       "python-dotenv>=1.0.0",
   ]
   ```

2. Tạo `.env.example`:
   ```env
   # FastAPI
   APP_ENV=local
   APP_DEBUG=true
   
   # Postgres
   POSTGRES_URL=postgresql+asyncpg://user:password@localhost:5432/localmate
   
   # Neo4j
   NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=CHANGE_ME
   ```

---

### Task 0.2: Core Configuration

**File:** `app/core/config.py`

```python
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App
    app_env: str = "local"
    app_debug: bool = True
    
    # Postgres
    postgres_url: str
    
    # Neo4j
    neo4j_uri: str
    neo4j_user: str
    neo4j_password: str
    
    # LLM (phase sau)
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    google_api_key: str | None = None
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
```

---

### Task 0.3: Database Session Setup

**File:** `app/shared/db/session.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.config import settings

engine = create_async_engine(
    settings.postgres_url,
    echo=settings.app_debug,
    future=True
)

async_session = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
```

---

### Task 0.4: SQLAlchemy Models

**File:** `app/shared/models/base.py`

```python
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, func

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
```

**File:** `app/shared/models/user_models.py`

```python
import uuid
from sqlalchemy import String, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base, TimestampMixin

class User(Base, TimestampMixin):
    __tablename__ = "users"
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    user_email: Mapped[str] = mapped_column(String, unique=True, index=True)
    user_password_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    user_full_name: Mapped[str] = mapped_column(String, nullable=False)
    user_phone: Mapped[str | None] = mapped_column(String, nullable=True)
    user_role: Mapped[str] = mapped_column(String, nullable=False)
    user_locale: Mapped[str] = mapped_column(String, default="vi_VN")
    timezone: Mapped[str] = mapped_column(String, default="Asia/Ho_Chi_Minh")
    
    __table_args__ = (
        CheckConstraint(
            "user_role IN ('tourist', 'driver', 'admin')",
            name="user_role_check"
        ),
    )
```

**File:** `app/shared/models/itinerary_models.py`

```python
import uuid
from datetime import date, datetime
from sqlalchemy import String, Integer, Date, ForeignKey, ARRAY, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin

class Itinerary(Base, TimestampMixin):
    __tablename__ = "itineraries"
    
    itinerary_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    itinerary_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("users.user_id"), 
        nullable=False
    )
    itinerary_title: Mapped[str] = mapped_column(String, nullable=False)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    itinerary_total_days: Mapped[int] = mapped_column(Integer, nullable=False)
    itinerary_total_budget: Mapped[float | None] = mapped_column(
        Numeric(12, 2), 
        nullable=True
    )
    itinerary_currency: Mapped[str] = mapped_column(String, default="VND")
    itinerary_meta: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    
    # Relationship
    stops = relationship("ItineraryStop", back_populates="itinerary")


class ItineraryStop(Base, TimestampMixin):
    __tablename__ = "itinerary_stops"
    
    stop_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    stop_itinerary_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("itineraries.itinerary_id"),
        nullable=False
    )
    stop_day_index: Mapped[int] = mapped_column(Integer, nullable=False)
    stop_order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    stop_place_id: Mapped[str] = mapped_column(String, nullable=False)  # Neo4j Place.id
    arrival_time: Mapped[datetime | None] = mapped_column(nullable=True)
    stay_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stop_notes: Mapped[str | None] = mapped_column(String, nullable=True)
    stop_tags: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    stop_snapshot: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    
    # Relationship
    itinerary = relationship("Itinerary", back_populates="stops")
```

---

### Task 0.5: Neo4j Client

**File:** `app/shared/integrations/neo4j_client.py`

```python
from neo4j import AsyncGraphDatabase, AsyncDriver
from app.core.config import settings

class Neo4jClient:
    def __init__(self, uri: str, user: str, password: str):
        self._driver: AsyncDriver = AsyncGraphDatabase.driver(
            uri, 
            auth=(user, password)
        )
    
    async def close(self):
        await self._driver.close()
    
    async def run_cypher(
        self, 
        query: str, 
        params: dict | None = None
    ) -> list[dict]:
        async with self._driver.session() as session:
            result = await session.run(query, params or {})
            records = await result.data()
            return records
    
    async def verify_connectivity(self) -> bool:
        try:
            await self._driver.verify_connectivity()
            return True
        except Exception:
            return False

# Global instance
neo4j_client = Neo4jClient(
    settings.neo4j_uri,
    settings.neo4j_user,
    settings.neo4j_password
)
```

---

### Task 0.6: FastAPI Main Entry

**File:** `app/main.py`

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.shared.integrations.neo4j_client import neo4j_client
from app.shared.db.session import engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown
    await neo4j_client.close()
    await engine.dispose()

app = FastAPI(
    title="LocalMate Da Nang",
    description="Danang Tourism Super Agent API",
    version="0.1.0",
    lifespan=lifespan
)

@app.get("/health")
async def health_check():
    neo4j_ok = await neo4j_client.verify_connectivity()
    return {
        "status": "healthy",
        "neo4j": "connected" if neo4j_ok else "disconnected"
    }
```

---

### Task 0.7: Alembic Setup

**File:** `alembic.ini`
- Set `script_location = app/shared/db/migrations`
- Set `sqlalchemy.url` từ env

**File:** `app/shared/db/migrations/env.py`
- Import `Base.metadata` từ models
- Configure async migration

**Command:**
```bash
# Tạo migration
alembic revision --autogenerate -m "init_core_schema"

# Apply migration
alembic upgrade head
```

---

## ✅ Acceptance Criteria

| Criteria | Test Command |
|----------|-------------|
| FastAPI chạy được | `uvicorn app.main:app --reload` |
| Health check respond | `GET /health` → 200 OK |
| Alembic migration | `alembic upgrade head` không lỗi |
| Neo4j connectivity | Health check trả về `neo4j: connected` |
| Tables tồn tại | Kiểm tra `users`, `itineraries`, `itinerary_stops` trong Postgres |

---

## 📂 Folder Structure sau Phase 0

```
localmate-danang-backend/
├─ README.md
├─ pyproject.toml
├─ alembic.ini
├─ .env.example
├─ .env                        # gitignore
└─ app/
   ├─ __init__.py
   ├─ main.py                  # ✅ FastAPI entry
   ├─ core/
   │  ├─ __init__.py
   │  └─ config.py             # ✅ Settings
   └─ shared/
      ├─ __init__.py
      ├─ db/
      │  ├─ __init__.py
      │  ├─ session.py         # ✅ AsyncSession
      │  └─ migrations/        # ✅ Alembic
      │     ├─ env.py
      │     └─ versions/
      ├─ models/
      │  ├─ __init__.py
      │  ├─ base.py            # ✅ Base + Mixin
      │  ├─ user_models.py     # ✅ User
      │  └─ itinerary_models.py # ✅ Itinerary + Stop
      └─ integrations/
         ├─ __init__.py
         └─ neo4j_client.py    # ✅ Neo4j wrapper
```

---

## ⏰ Estimated Time: 2-3 hours
