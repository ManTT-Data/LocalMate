# PHASE 0 – Project Bootstrap

## 🎯 Mục tiêu

Có hệ thống FastAPI + Supabase + Neo4j + Gemini chạy ổn định.
**Chưa cần logic AI.**

---

## 📦 Deliverables

| Item | Path |
|------|------|
| FastAPI Entry | `app/main.py` |
| Settings | `app/core/config.py` |
| Security | `app/core/security.py` |
| DB Session | `app/shared/db/session.py` |
| Base Model | `app/shared/models/base.py` |
| Profile Model | `app/shared/models/profile.py` |
| Itinerary Models | `app/shared/models/itinerary.py` |
| Supabase Client | `app/shared/integrations/supabase_client.py` |
| Neo4j Client | `app/shared/integrations/neo4j_client.py` |
| Gemini Client | `app/shared/integrations/gemini_client.py` |

---

## 📋 Tasks

### Task 0.1: Project Structure

```
localmate-danang-backend/
├── README.md
├── pyproject.toml
├── .env.example
└── app/
   └── __init__.py
```

**pyproject.toml:**
```toml
[project]
name = "localmate-backend"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "sqlalchemy>=2.0.0",
    "asyncpg>=0.30.0",
    "alembic>=1.14.0",
    "pydantic>=2.10.0",
    "pydantic-settings>=2.6.0",
    "supabase>=2.10.0",
    "neo4j>=5.26.0",
    "google-genai>=1.0.0",
    "pgvector>=0.3.0",
    "python-dotenv>=1.0.0",
    "httpx>=0.28.0",
]

[project.optional-dependencies]
dev = ["pytest", "pytest-asyncio", "httpx"]
```

---

### Task 0.2: Environment Config

**`.env.example`:**
```env
# FastAPI
APP_ENV=local
APP_DEBUG=true

# Supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
DATABASE_URL=postgresql+asyncpg://postgres:password@db.xxxxx.supabase.co:5432/postgres

# Neo4j
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=CHANGE_ME

# Google AI
GOOGLE_API_KEY=your_google_api_key
```

**`app/core/config.py`:**
```python
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_env: str = "local"
    app_debug: bool = True
    
    # Supabase
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str
    database_url: str
    
    # Neo4j
    neo4j_uri: str
    neo4j_user: str
    neo4j_password: str
    
    # Google AI
    google_api_key: str
    gemini_model: str = "gemini-2.5-flash-preview-05-20"
    embedding_model: str = "text-embedding-004"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
```

---

### Task 0.3: Supabase Client

**`app/shared/integrations/supabase_client.py`:**
```python
from supabase import create_client, Client
from app.core.config import settings

supabase: Client = create_client(
    settings.supabase_url,
    settings.supabase_service_role_key
)

def get_supabase() -> Client:
    return supabase
```

---

### Task 0.4: Security (JWT Verification)

**`app/core/security.py`:**
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.shared.integrations.supabase_client import supabase

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Verify Supabase JWT and return user info."""
    try:
        token = credentials.credentials
        user = supabase.auth.get_user(token)
        return user.user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
```

---

### Task 0.5: Database Session

**`app/shared/db/session.py`:**
```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=settings.app_debug,
)

async_session = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db():
    async with async_session() as session:
        yield session
```

---

### Task 0.6: SQLAlchemy Models

**`app/shared/models/base.py`:**
```python
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, func

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
```

**`app/shared/models/profile.py`:**
```python
import uuid
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base, TimestampMixin

class Profile(Base, TimestampMixin):
    __tablename__ = "profiles"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str | None] = mapped_column(String, nullable=True)
    role: Mapped[str] = mapped_column(String, nullable=False, default="tourist")
    locale: Mapped[str] = mapped_column(String, default="vi_VN")
    avatar_url: Mapped[str | None] = mapped_column(String, nullable=True)
```

**`app/shared/models/itinerary.py`:**
```python
import uuid
from datetime import date, datetime
from sqlalchemy import String, Integer, Date, ForeignKey, ARRAY, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin

class Itinerary(Base, TimestampMixin):
    __tablename__ = "itineraries"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("profiles.id"))
    title: Mapped[str] = mapped_column(String, nullable=False)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    total_days: Mapped[int] = mapped_column(Integer, nullable=False)
    total_budget: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String, default="VND")
    meta: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    
    stops = relationship("ItineraryStop", back_populates="itinerary")

class ItineraryStop(Base, TimestampMixin):
    __tablename__ = "itinerary_stops"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    itinerary_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("itineraries.id"))
    day_index: Mapped[int] = mapped_column(Integer, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    place_id: Mapped[str] = mapped_column(String, nullable=False)
    arrival_time: Mapped[datetime | None] = mapped_column(nullable=True)
    stay_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(String, nullable=True)
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    snapshot: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    
    itinerary = relationship("Itinerary", back_populates="stops")
```

---

### Task 0.7: Neo4j Client

**`app/shared/integrations/neo4j_client.py`:**
```python
from neo4j import AsyncGraphDatabase
from app.core.config import settings

class Neo4jClient:
    def __init__(self, uri: str, user: str, password: str):
        self._driver = AsyncGraphDatabase.driver(uri, auth=(user, password))
    
    async def close(self):
        await self._driver.close()
    
    async def run_cypher(self, query: str, params: dict | None = None) -> list[dict]:
        async with self._driver.session() as session:
            result = await session.run(query, params or {})
            return await result.data()
    
    async def verify_connectivity(self) -> bool:
        try:
            await self._driver.verify_connectivity()
            return True
        except Exception:
            return False

neo4j_client = Neo4jClient(
    settings.neo4j_uri,
    settings.neo4j_user,
    settings.neo4j_password
)
```

---

### Task 0.8: Gemini Client

**`app/shared/integrations/gemini_client.py`:**
```python
from google import genai
from app.core.config import settings

client = genai.Client(api_key=settings.google_api_key)

async def chat_completion(
    messages: list[dict],
    model: str | None = None,
    temperature: float = 0.7,
) -> str:
    """Generate chat completion using Gemini."""
    model = model or settings.gemini_model
    
    response = client.models.generate_content(
        model=model,
        contents=messages,
        config={"temperature": temperature}
    )
    return response.text

async def generate_embedding(text: str) -> list[float]:
    """Generate text embedding using text-embedding-004."""
    response = client.models.embed_content(
        model=settings.embedding_model,
        contents=text
    )
    return response.embeddings[0].values
```

---

### Task 0.9: FastAPI Main

**`app/main.py`:**
```python
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.shared.integrations.neo4j_client import neo4j_client
from app.shared.db.session import engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
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

## ✅ Acceptance Criteria

| Criteria | Test |
|----------|------|
| FastAPI runs | `uvicorn app.main:app --reload` |
| Health check | `GET /health` → 200 OK |
| Neo4j connected | Health returns `neo4j: connected` |
| Supabase JWT works | Token verification không lỗi |

---

## ⏰ Estimated Time: 2-3 hours
