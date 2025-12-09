# PHASE 1 – Planner API Skeleton

## 🎯 Mục tiêu

API hoạt động end-to-end với **dữ liệu dummy**.
Chưa cần Neo4j query hay AI logic.

---

## 📦 Deliverables

| Item | Path |
|------|------|
| Itinerary Schemas | `app/planner_app/schemas/itinerary_schemas.py` |
| Planner Router | `app/planner_app/api/router.py` |
| Itineraries Router | `app/planner_app/api/itineraries_router.py` |
| Itinerary Service | `app/planner_app/services/itinerary_service.py` |
| Planner Agent | `app/planner_app/agents/planner_agent.py` |
| Itinerary Repository | `app/shared/repositories/itinerary_repository.py` |
| Base Repository | `app/shared/repositories/base_repository.py` |
| API v1 Router | `app/api/v1/router.py` |

---

## 📋 Tasks

### Task 1.1: Pydantic Schemas

**`app/planner_app/schemas/itinerary_schemas.py`:**
```python
import uuid
from datetime import date, datetime
from pydantic import BaseModel, Field

class ItineraryPlanRequest(BaseModel):
    duration_days: int = Field(ge=1)
    family_size: int | None = None
    interests: list[str] | None = None
    budget: str | None = None
    start_date: date | None = None
    start_location_lat: float | None = None
    start_location_lng: float | None = None

class ItineraryStopResponse(BaseModel):
    id: uuid.UUID
    day_index: int
    order_index: int
    place_id: str
    arrival_time: datetime | None = None
    stay_minutes: int | None = None
    snapshot: dict | None = None
    
    class Config:
        from_attributes = True

class ItineraryPlanResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    total_days: int
    currency: str
    created_at: datetime
    stops: list[ItineraryStopResponse]
    
    class Config:
        from_attributes = True
```

---

### Task 1.2: Base Repository

**`app/shared/repositories/base_repository.py`:**
```python
from typing import TypeVar, Generic, Type
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    async def get_by_id(self, db: AsyncSession, id: UUID) -> ModelType | None:
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()
    
    async def create(self, db: AsyncSession, obj: ModelType) -> ModelType:
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj
```

---

### Task 1.3: Itinerary Repository

**`app/shared/repositories/itinerary_repository.py`:**
```python
import uuid
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.models.itinerary import Itinerary, ItineraryStop
from .base_repository import BaseRepository

class ItineraryRepository(BaseRepository[Itinerary]):
    def __init__(self):
        super().__init__(Itinerary)
    
    async def create_with_stops(
        self, db: AsyncSession, user_id: uuid.UUID,
        title: str, total_days: int, currency: str,
        meta: dict | None, stops: list[dict]
    ) -> Itinerary:
        itinerary = Itinerary(
            user_id=user_id, title=title,
            total_days=total_days, currency=currency, meta=meta
        )
        db.add(itinerary)
        await db.flush()
        
        for stop_data in stops:
            stop = ItineraryStop(
                itinerary_id=itinerary.id,
                day_index=stop_data["day_index"],
                order_index=stop_data["order_index"],
                place_id=stop_data["place_id"],
                stay_minutes=stop_data.get("stay_minutes"),
                snapshot=stop_data.get("snapshot"),
            )
            db.add(stop)
        
        await db.commit()
        await db.refresh(itinerary)
        return itinerary
    
    async def get_with_stops(self, db: AsyncSession, itinerary_id: uuid.UUID) -> Itinerary | None:
        result = await db.execute(
            select(Itinerary)
            .options(selectinload(Itinerary.stops))
            .where(Itinerary.id == itinerary_id)
        )
        return result.scalar_one_or_none()

itinerary_repository = ItineraryRepository()
```

---

### Task 1.4: Planner Agent (Dummy)

**`app/planner_app/agents/planner_agent.py`:**
```python
from dataclasses import dataclass
from app.planner_app.schemas.itinerary_schemas import ItineraryPlanRequest

@dataclass
class PlannerStop:
    place_id: str
    lat: float
    lng: float
    day_index: int
    order_index: int
    snapshot: dict | None = None

@dataclass
class PlannerItineraryResult:
    title: str
    total_days: int
    currency: str
    stops: list[PlannerStop]

class PlannerAgent:
    async def create_itinerary(self, request: ItineraryPlanRequest) -> PlannerItineraryResult:
        # Dummy places
        dummy_places = [
            {"place_id": "my-khe-beach", "lat": 16.0544, "lng": 108.2480, "name": "Bãi biển Mỹ Khê", "category": "beach"},
            {"place_id": "be-man-seafood", "lat": 16.0512, "lng": 108.2465, "name": "Nhà hàng Bé Mặn", "category": "restaurant"},
            {"place_id": "son-tra-peninsula", "lat": 16.1167, "lng": 108.2667, "name": "Bán đảo Sơn Trà", "category": "nature"},
        ]
        
        stops = [
            PlannerStop(
                place_id=p["place_id"], lat=p["lat"], lng=p["lng"],
                day_index=1, order_index=idx+1,
                snapshot={"name": p["name"], "category": p["category"]}
            )
            for idx, p in enumerate(dummy_places[:request.duration_days + 1])
        ]
        
        return PlannerItineraryResult(
            title=f"Khám phá Đà Nẵng {request.duration_days} ngày",
            total_days=request.duration_days,
            currency="VND",
            stops=stops
        )

planner_agent = PlannerAgent()
```

---

### Task 1.5: Itineraries Router

**`app/planner_app/api/itineraries_router.py`:**
```python
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.db.session import get_db
from app.core.security import get_current_user
from app.planner_app.schemas.itinerary_schemas import ItineraryPlanRequest, ItineraryPlanResponse
from app.planner_app.services.itinerary_service import itinerary_service

router = APIRouter()

@router.post("/plan", response_model=ItineraryPlanResponse)
async def plan_itinerary(
    request: ItineraryPlanRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = uuid.UUID(current_user.id)
    return await itinerary_service.create_itinerary_plan(db, user_id, request)

@router.get("/{itinerary_id}", response_model=ItineraryPlanResponse)
async def get_itinerary(
    itinerary_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    result = await itinerary_service.get_itinerary(db, itinerary_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Itinerary not found")
    return result
```

---

### Task 1.6: Update main.py

```python
# Add to app/main.py
from app.api.v1.router import api_router

app.include_router(api_router, prefix="/api/v1")
```

---

## ✅ Acceptance Criteria

| Criteria | Test |
|----------|------|
| POST /plan creates itinerary | With valid JWT → 200 + id |
| GET /{id} returns data | Returns correct itinerary |
| Auth required | No JWT → 401 |
| Validation works | `duration_days: 0` → 422 |

---

## ⏰ Estimated Time: 3-4 hours
