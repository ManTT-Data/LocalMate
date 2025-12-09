# **PHASE 1 – Planner API Skeleton (No AI, No Graph Yet)**

## 🎯 Mục tiêu
API hoạt động end-to-end với **dữ liệu dummy**.  
Chưa cần Neo4j query hay AI logic.

---

## 📦 Deliverables

| Item | Path | Description |
|------|------|-------------|
| Itinerary Schemas | `app/planner_app/schemas/itinerary_schemas.py` | Request/Response models |
| Planner Router | `app/planner_app/api/router.py` | Root router |
| Itineraries Router | `app/planner_app/api/itineraries_router.py` | POST /plan, GET /{id} |
| Itinerary Service | `app/planner_app/services/itinerary_service.py` | Business logic |
| Planner Agent | `app/planner_app/agents/planner_agent.py` | Dummy agent |
| Itinerary Repository | `app/shared/repositories/itinerary_repository.py` | DB operations |
| Base Repository | `app/shared/repositories/base_repository.py` | Abstract base |
| API v1 Router | `app/api/v1/router.py` | Include planner router |
| Unit Tests | `app/planner_app/tests/test_itinerary_api.py` | API tests |

---

## 📋 Tasks Chi tiết

### Task 1.1: Pydantic Schemas

**File:** `app/planner_app/schemas/itinerary_schemas.py`

```python
import uuid
from datetime import date, datetime
from pydantic import BaseModel, Field

class ItineraryPlanRequest(BaseModel):
    """Request để tạo itinerary mới"""
    user_id: uuid.UUID
    duration_days: int = Field(ge=1, description="Số ngày du lịch")
    family_size: int | None = None
    interests: list[str] | None = None  # ["beach", "seafood", "coffee"]
    budget: str | None = None           # "low", "medium", "high"
    start_date: date | None = None
    start_location_lat: float | None = None
    start_location_lng: float | None = None


class ItineraryStopResponse(BaseModel):
    """Response cho mỗi stop trong itinerary"""
    id: uuid.UUID
    day_index: int
    order_index: int
    place_id: str
    arrival_time: datetime | None = None
    stay_minutes: int | None = None
    snapshot: dict | None = None  # { "name": "...", "category": "...", ... }
    
    class Config:
        from_attributes = True


class ItineraryPlanResponse(BaseModel):
    """Response cho itinerary đầy đủ"""
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

**File:** `app/shared/repositories/base_repository.py`

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
    
    async def get_by_id(
        self, 
        db: AsyncSession, 
        id: UUID
    ) -> ModelType | None:
        result = await db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def create(
        self, 
        db: AsyncSession, 
        obj: ModelType
    ) -> ModelType:
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj
```

---

### Task 1.3: Itinerary Repository

**File:** `app/shared/repositories/itinerary_repository.py`

```python
import uuid
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.models.itinerary_models import Itinerary, ItineraryStop
from .base_repository import BaseRepository

class ItineraryRepository(BaseRepository[Itinerary]):
    def __init__(self):
        super().__init__(Itinerary)
    
    async def create_with_stops(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        title: str,
        total_days: int,
        currency: str,
        meta: dict | None,
        stops: list[dict],
    ) -> Itinerary:
        """Tạo itinerary cùng với stops trong 1 transaction"""
        
        # Tạo itinerary
        itinerary = Itinerary(
            itinerary_user_id=user_id,
            itinerary_title=title,
            itinerary_total_days=total_days,
            itinerary_currency=currency,
            itinerary_meta=meta,
        )
        db.add(itinerary)
        await db.flush()  # Get itinerary_id
        
        # Tạo stops
        for stop_data in stops:
            stop = ItineraryStop(
                stop_itinerary_id=itinerary.itinerary_id,
                stop_day_index=stop_data["day_index"],
                stop_order_index=stop_data["order_index"],
                stop_place_id=stop_data["place_id"],
                stay_minutes=stop_data.get("stay_minutes"),
                stop_snapshot=stop_data.get("snapshot"),
            )
            db.add(stop)
        
        await db.commit()
        await db.refresh(itinerary)
        return itinerary
    
    async def get_with_stops(
        self,
        db: AsyncSession,
        itinerary_id: uuid.UUID,
    ) -> Itinerary | None:
        """Lấy itinerary kèm stops"""
        result = await db.execute(
            select(Itinerary)
            .options(selectinload(Itinerary.stops))
            .where(Itinerary.itinerary_id == itinerary_id)
        )
        return result.scalar_one_or_none()


# Singleton instance
itinerary_repository = ItineraryRepository()
```

---

### Task 1.4: Planner Agent (Dummy)

**File:** `app/planner_app/agents/planner_agent.py`

```python
from dataclasses import dataclass
from app.planner_app.schemas.itinerary_schemas import ItineraryPlanRequest

@dataclass
class PlannerStop:
    """Đại diện 1 stop trong kết quả planning"""
    place_id: str
    lat: float
    lng: float
    day_index: int
    order_index: int
    snapshot: dict | None = None


@dataclass
class PlannerItineraryResult:
    """Kết quả trả về từ PlannerAgent"""
    title: str
    total_days: int
    currency: str
    stops: list[PlannerStop]


class PlannerAgent:
    """
    Agent tạo itinerary.
    Phase 1: Trả về dummy data.
    Phase sau: Sử dụng Neo4j + LLM.
    """
    
    async def create_itinerary(
        self,
        request: ItineraryPlanRequest,
    ) -> PlannerItineraryResult:
        """
        MVP flow (dummy):
        - Trả về 2-3 địa điểm hardcoded
        """
        
        # Dummy places cho Đà Nẵng
        dummy_places = [
            {
                "place_id": "my-khe-beach",
                "lat": 16.0544,
                "lng": 108.2480,
                "name": "Bãi biển Mỹ Khê",
                "category": "beach"
            },
            {
                "place_id": "be-man-seafood",
                "lat": 16.0512,
                "lng": 108.2465,
                "name": "Nhà hàng Bé Mặn",
                "category": "restaurant"
            },
            {
                "place_id": "son-tra-peninsula",
                "lat": 16.1167,
                "lng": 108.2667,
                "name": "Bán đảo Sơn Trà",
                "category": "nature"
            },
        ]
        
        # Tạo stops
        stops = []
        for idx, place in enumerate(dummy_places[:request.duration_days + 1]):
            stops.append(PlannerStop(
                place_id=place["place_id"],
                lat=place["lat"],
                lng=place["lng"],
                day_index=1,  # Tất cả đều ở Day 1 cho đơn giản
                order_index=idx + 1,
                snapshot={
                    "name": place["name"],
                    "category": place["category"]
                }
            ))
        
        return PlannerItineraryResult(
            title=f"Khám phá Đà Nẵng {request.duration_days} ngày",
            total_days=request.duration_days,
            currency="VND",
            stops=stops
        )


# Singleton instance
planner_agent = PlannerAgent()
```

---

### Task 1.5: Itinerary Service

**File:** `app/planner_app/services/itinerary_service.py`

```python
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.repositories.itinerary_repository import itinerary_repository
from app.planner_app.agents.planner_agent import planner_agent
from app.planner_app.schemas.itinerary_schemas import (
    ItineraryPlanRequest,
    ItineraryPlanResponse,
    ItineraryStopResponse,
)

class ItineraryService:
    """Service orchestration cho Itinerary"""
    
    async def create_itinerary_plan(
        self,
        db: AsyncSession,
        request: ItineraryPlanRequest,
    ) -> ItineraryPlanResponse:
        """
        Flow:
        1. Gọi planner_agent.create_itinerary() để nhận kết quả
        2. Lưu itinerary + stops vào Postgres
        3. Map sang ItineraryPlanResponse
        """
        
        # 1. Planning
        result = await planner_agent.create_itinerary(request)
        
        # 2. Chuẩn bị data cho repository
        stops_data = [
            {
                "day_index": stop.day_index,
                "order_index": stop.order_index,
                "place_id": stop.place_id,
                "stay_minutes": 60,  # Default 1 hour
                "snapshot": stop.snapshot,
            }
            for stop in result.stops
        ]
        
        # 3. Lưu vào DB
        itinerary = await itinerary_repository.create_with_stops(
            db=db,
            user_id=request.user_id,
            title=result.title,
            total_days=result.total_days,
            currency=result.currency,
            meta={"interests": request.interests, "budget": request.budget},
            stops=stops_data,
        )
        
        # 4. Fetch lại with stops
        itinerary = await itinerary_repository.get_with_stops(
            db, itinerary.itinerary_id
        )
        
        # 5. Map to response
        return self._to_response(itinerary)
    
    async def get_itinerary(
        self,
        db: AsyncSession,
        itinerary_id: uuid.UUID,
    ) -> ItineraryPlanResponse | None:
        """Lấy itinerary theo ID"""
        itinerary = await itinerary_repository.get_with_stops(db, itinerary_id)
        if not itinerary:
            return None
        return self._to_response(itinerary)
    
    def _to_response(self, itinerary) -> ItineraryPlanResponse:
        """Map model to response schema"""
        return ItineraryPlanResponse(
            id=itinerary.itinerary_id,
            user_id=itinerary.itinerary_user_id,
            title=itinerary.itinerary_title,
            total_days=itinerary.itinerary_total_days,
            currency=itinerary.itinerary_currency,
            created_at=itinerary.created_at,
            stops=[
                ItineraryStopResponse(
                    id=stop.stop_id,
                    day_index=stop.stop_day_index,
                    order_index=stop.stop_order_index,
                    place_id=stop.stop_place_id,
                    arrival_time=stop.arrival_time,
                    stay_minutes=stop.stay_minutes,
                    snapshot=stop.stop_snapshot,
                )
                for stop in sorted(
                    itinerary.stops, 
                    key=lambda s: (s.stop_day_index, s.stop_order_index)
                )
            ]
        )


# Singleton instance
itinerary_service = ItineraryService()
```

---

### Task 1.6: Itineraries Router

**File:** `app/planner_app/api/itineraries_router.py`

```python
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.db.session import get_db
from app.planner_app.schemas.itinerary_schemas import (
    ItineraryPlanRequest,
    ItineraryPlanResponse,
)
from app.planner_app.services.itinerary_service import itinerary_service

router = APIRouter()


@router.post("/plan", response_model=ItineraryPlanResponse)
async def plan_itinerary(
    request: ItineraryPlanRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Tạo itinerary mới dựa trên yêu cầu của user.
    
    - **user_id**: ID của user
    - **duration_days**: Số ngày du lịch
    - **interests**: Sở thích (beach, seafood, coffee...)
    - **budget**: Mức ngân sách (low, medium, high)
    """
    return await itinerary_service.create_itinerary_plan(db, request)


@router.get("/{itinerary_id}", response_model=ItineraryPlanResponse)
async def get_itinerary(
    itinerary_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Lấy itinerary theo ID"""
    result = await itinerary_service.get_itinerary(db, itinerary_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Itinerary not found"
        )
    return result
```

---

### Task 1.7: Planner Router

**File:** `app/planner_app/api/router.py`

```python
from fastapi import APIRouter
from .itineraries_router import router as itineraries_router

router = APIRouter()

router.include_router(
    itineraries_router,
    prefix="/itineraries",
    tags=["itineraries"]
)
```

---

### Task 1.8: API v1 Router

**File:** `app/api/v1/router.py`

```python
from fastapi import APIRouter
from app.planner_app.api.router import router as planner_router

api_router = APIRouter()

api_router.include_router(
    planner_router,
    prefix="/planner",
    tags=["planner"]
)
```

---

### Task 1.9: Update Main.py

**File:** `app/main.py` (update)

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.shared.integrations.neo4j_client import neo4j_client
from app.shared.db.session import engine
from app.api.v1.router import api_router

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

# Include API v1 router
app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    neo4j_ok = await neo4j_client.verify_connectivity()
    return {
        "status": "healthy",
        "neo4j": "connected" if neo4j_ok else "disconnected"
    }
```

---

### Task 1.10: Unit Tests

**File:** `app/planner_app/tests/test_itinerary_api.py`

```python
import pytest
import uuid
from httpx import AsyncClient
from app.main import app

@pytest.fixture
def anyio_backend():
    return 'asyncio'

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


class TestItineraryAPI:
    """Test cases cho Itinerary API"""
    
    @pytest.mark.anyio
    async def test_plan_itinerary_success(self, client: AsyncClient):
        """Test tạo itinerary thành công"""
        request_data = {
            "user_id": str(uuid.uuid4()),
            "duration_days": 2,
            "interests": ["beach", "seafood"],
            "budget": "medium"
        }
        
        response = await client.post(
            "/api/v1/planner/itineraries/plan",
            json=request_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "stops" in data
        assert len(data["stops"]) >= 1
        assert data["total_days"] == 2
    
    @pytest.mark.anyio
    async def test_get_itinerary_success(self, client: AsyncClient):
        """Test lấy itinerary sau khi tạo"""
        # 1. Tạo itinerary
        request_data = {
            "user_id": str(uuid.uuid4()),
            "duration_days": 1,
        }
        create_response = await client.post(
            "/api/v1/planner/itineraries/plan",
            json=request_data
        )
        assert create_response.status_code == 200
        itinerary_id = create_response.json()["id"]
        
        # 2. Lấy lại
        get_response = await client.get(
            f"/api/v1/planner/itineraries/{itinerary_id}"
        )
        assert get_response.status_code == 200
        assert get_response.json()["id"] == itinerary_id
    
    @pytest.mark.anyio
    async def test_get_itinerary_not_found(self, client: AsyncClient):
        """Test lấy itinerary không tồn tại"""
        fake_id = uuid.uuid4()
        response = await client.get(
            f"/api/v1/planner/itineraries/{fake_id}"
        )
        assert response.status_code == 404
    
    @pytest.mark.anyio
    async def test_plan_itinerary_invalid_days(self, client: AsyncClient):
        """Test validation: duration_days phải >= 1"""
        request_data = {
            "user_id": str(uuid.uuid4()),
            "duration_days": 0,  # Invalid
        }
        
        response = await client.post(
            "/api/v1/planner/itineraries/plan",
            json=request_data
        )
        
        assert response.status_code == 422
```

---

## ✅ Acceptance Criteria

| Criteria | Test Method |
|----------|------------|
| POST /plan tạo itinerary | `curl -X POST ... -d {...}` → 200 + id |
| GET /{id} trả về đúng | Dùng id từ POST → GET → đúng data |
| Stops được lưu | Response có `stops` array không rỗng |
| Validation hoạt động | `duration_days: 0` → 422 |
| Unit tests pass | `pytest app/planner_app/tests/` |

---

## 📂 Folder Structure sau Phase 1

```
app/
├─ main.py                         # ✅ Updated
├─ api/
│  └─ v1/
│     ├─ __init__.py
│     └─ router.py                 # ✅ NEW
├─ planner_app/
│  ├─ __init__.py
│  ├─ api/
│  │  ├─ __init__.py
│  │  ├─ router.py                 # ✅ NEW
│  │  └─ itineraries_router.py     # ✅ NEW
│  ├─ schemas/
│  │  ├─ __init__.py
│  │  └─ itinerary_schemas.py      # ✅ NEW
│  ├─ agents/
│  │  ├─ __init__.py
│  │  └─ planner_agent.py          # ✅ NEW (dummy)
│  ├─ services/
│  │  ├─ __init__.py
│  │  └─ itinerary_service.py      # ✅ NEW
│  └─ tests/
│     ├─ __init__.py
│     └─ test_itinerary_api.py     # ✅ NEW
└─ shared/
   └─ repositories/
      ├─ __init__.py
      ├─ base_repository.py        # ✅ NEW
      └─ itinerary_repository.py   # ✅ NEW
```

---

## 🔗 Dependencies

| Depends on | Description |
|------------|-------------|
| Phase 0 | User model, DB session, models |

---

## ⏰ Estimated Time: 3-4 hours
