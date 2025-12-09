# Coding Conventions

Quick reference cho coding standards trong dự án LocalMate.

---

## 📁 File Organization

```
app/
├── core/           # Config, security, logging (không import từ nơi khác)
├── shared/         # Code dùng chung (models, repos, integrations)
├── planner_app/    # Feature module (api, schemas, agents, services)
└── guide_app/      # Feature module
```

**Rule:** Feature modules (`planner_app`) có thể import từ `shared/` và `core/`, nhưng KHÔNG import lẫn nhau.

---

## 🏷️ Naming

| Type | Convention | Example |
|------|------------|---------|
| Files | `snake_case.py` | `itinerary_service.py` |
| Classes | `PascalCase` | `ItineraryService` |
| Functions | `snake_case` | `create_itinerary` |
| Constants | `UPPER_SNAKE` | `DEFAULT_CURRENCY` |
| DB Tables | `snake_case` | `itinerary_stops` |
| DB Columns | `snake_case` | `user_id`, `place_id` |

---

## 📦 Imports

```python
# 1. Standard library
import uuid
from datetime import datetime

# 2. Third-party
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

# 3. Local - absolute imports only
from app.core.config import settings
from app.shared.models.itinerary import Itinerary
```

---

## ⚡ Async Patterns

```python
# ✅ GOOD: Async DB operations
async def get_itinerary(db: AsyncSession, id: UUID) -> Itinerary:
    result = await db.execute(select(Itinerary).where(Itinerary.id == id))
    return result.scalar_one_or_none()

# ✅ GOOD: Async HTTP
async with httpx.AsyncClient() as client:
    response = await client.get(url)

# ❌ BAD: Blocking calls in async context
import requests  # Don't use this, use httpx
```

---

## 🔒 Error Handling

```python
from fastapi import HTTPException, status

# Service layer: raise HTTPException
async def get_itinerary(db, id) -> ItineraryPlanResponse:
    itinerary = await repo.get_with_stops(db, id)
    if not itinerary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Itinerary not found"
        )
    return itinerary

# Integration layer: wrap external errors
async def call_external_api():
    try:
        response = await client.get(url)
        response.raise_for_status()
    except httpx.HTTPError as e:
        raise ExternalServiceError(f"API failed: {e}")
```

---

## 📝 Type Hints

```python
# ✅ Always use type hints
async def create_itinerary(
    db: AsyncSession,
    user_id: uuid.UUID,
    request: ItineraryPlanRequest,
) -> ItineraryPlanResponse:
    ...

# ✅ Use | None instead of Optional
def get_name(user: User) -> str | None:
    return user.full_name
```

---

## 🗄️ Database

```python
# ✅ Use repository pattern
result = await itinerary_repository.get_with_stops(db, id)

# ✅ Use Pydantic for validation
class ItineraryPlanRequest(BaseModel):
    duration_days: int = Field(ge=1)

# ✅ Use transactions for multi-step operations
async with db.begin():
    await db.execute(...)
    await db.execute(...)
```

---

## 🔑 Auth

```python
from app.core.security import get_current_user

@router.post("/plan")
async def plan_itinerary(
    request: ItineraryPlanRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # Always include for protected routes
):
    user_id = uuid.UUID(current_user.id)
    ...
```
