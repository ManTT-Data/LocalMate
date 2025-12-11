# **LocalMate Da Nang – Backend Implementation Plan**

**Idea:** 🌟 TÓM TẮT NGẮN: LocalMate – Danang Tourism Super Agent

LocalMate là một Du lịch siêu trợ lý AI dành cho Đà Nẵng, hoạt động theo mô hình Dual-Agent:

1. AI Travel Planner – Cho khách du lịch

Một trợ lý du lịch thông minh, hiểu sở thích người dùng, ngân sách, thời gian.
Nó có khả năng:

Phân tích hình ảnh để nhận diện địa điểm/đồ ăn

Tìm kiếm địa điểm bằng Graph-RAG (hiểu quan hệ gần – xa, tuyến đường)

Lên kế hoạch tối ưu theo thời gian (giải bài toán TSP)

Gợi ý nhà hàng/quán café/bãi biển hợp nhu cầu

Thực hiện hành động thật như đặt Grab qua MCP

Trải nghiệm: Tất cả trong một chat — hỏi → lên lịch → đặt xe → đi.

2. AI Guide Pack – Cho tài xế Grab

Khi du khách đi theo lịch trình được AI tạo, tài xế sẽ nhận được một "gói hướng dẫn mini" tự động:

Giới thiệu ngắn gọn về địa điểm

Fun facts / lịch sử

Góc chụp đẹp / giờ đông – giờ vắng

Câu nói nhanh đa ngôn ngữ

Gợi ý chia sẻ như một "local buddy"

Mục tiêu: Biến tài xế thành một bạn đồng hành bản địa – tạo trải nghiệm du lịch sâu hơn, thân thiện hơn.

🎯 Giá trị chính

Khách du lịch không phải dùng 4–5 app nữa → tất cả nằm trong một trợ lý AI.

Hiểu không gian, hiểu sở thích, lên kế hoạch thông minh.

Trải nghiệm sâu sắc hơn nhờ "local buddy".

Tài xế được hỗ trợ nội dung để tạo cảm giác thân thiện mà không mất công chuẩn bị.

---

## **0\. Bối cảnh & Nguyên tắc**

### **0.1. Mục tiêu dự án (phiên bản v0.1 – MVP)**

* Xây dựng backend cho **LocalMate – Danang Tourism Super Agent**.

* Tập trung triển khai **Planning Agent** (Planner App) cho du khách:

  * Nhận yêu cầu dạng ngôn ngữ tự nhiên / JSON.

  * Tìm địa điểm phù hợp từ **Neo4j**.

  * Sắp xếp lộ trình hợp lý (TSP heuristic).

  * Lưu itinerary vào **Supabase PostgreSQL**.

  * Cung cấp API để frontend hiển thị lại itinerary.

* **Guide Pack Agent** cho tài xế chỉ là **phase sau**, hiện tại chỉ cần placeholder.

### **0.2. Công nghệ & phiên bản**

| Component | Technology | Version/Notes |
|-----------|------------|---------------|
| Ngôn ngữ | Python | 3.11+ |
| Framework | FastAPI | Latest |
| Database | **Supabase** | PostgreSQL + Auth + Realtime |
| Auth | **Supabase Auth** | JWT-based |
| Graph DB | Neo4j Aura | 302 địa điểm có sẵn |
| LLM | **Google Gemini 2.5 Flash** | `gemini-2.5-flash-preview-05-20` |
| Text Embedding | **text-embedding-004** | 768 dimensions |
| Image Embedding | **CLIP** | Via API (HuggingFace/Replicate) |
| Vector Store | **Supabase pgvector** | Cho semantic search |

**Style bắt buộc:**

* Sử dụng **async/await** cho I/O (DB, HTTP, Neo4j).
* Luôn dùng **type hints** đầy đủ.
* Dùng **Pydantic v2**.
* Code phải **theo cấu trúc project** bên dưới.

---

## **2\. Cấu hình & Environment**

### **2.1. File `.env.example`**

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

# CLIP (optional - for image embeddings)
HUGGINGFACE_API_KEY=your_hf_api_key
```

### **2.2. `app/core/config.py`**

```python
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App
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
    
    # Google AI (Gemini + Embeddings)
    google_api_key: str
    
    # CLIP (optional)
    huggingface_api_key: str | None = None
    
    # Model configs
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

## **3. Database**

> [!NOTE]
> Chi tiết schema và models đã được chuyển sang file riêng.
> Xem chi tiết tại: [Database.md](Database.md)

---

## **4\. Neo4j Integration**

### **4.1. `app/shared/integrations/neo4j_client.py`**

* Class `Neo4jClient` với:

```python
class Neo4jClient:
    def __init__(self, uri: str, user: str, password: str): ...
    async def run_cypher(self, query: str, params: dict | None = None) -> list[dict]: ...
```

* Sử dụng Neo4j Python driver (async).
* Tạo instance global: `neo4j_client = Neo4jClient(settings.neo4j_uri, ...)`.

---

## **5\. Planner API – Spec chi tiết**

### **5.1. Endpoints**

1. `POST /api/v1/planner/itineraries/plan`
2. `GET /api/v1/planner/itineraries/{itinerary_id}`

> [!NOTE]
> Tất cả endpoints yêu cầu **Supabase JWT** trong header `Authorization: Bearer <token>`.

### **5.2. Request / Response Models**

**File:** `app/planner_app/schemas/itinerary_schemas.py`

#### **`ItineraryPlanRequest`**

```python
class ItineraryPlanRequest(BaseModel):
    duration_days: int = Field(ge=1)
    family_size: int | None = None
    interests: list[str] | None = None   # ["beach", "seafood", "coffee"]
    budget: str | None = None            # "low", "medium", "high"
    start_date: date | None = None
    start_location_lat: float | None = None
    start_location_lng: float | None = None
    # user_id lấy từ JWT token, không cần truyền
```

#### **`ItineraryStopResponse`**

```python
class ItineraryStopResponse(BaseModel):
    id: uuid.UUID
    day_index: int
    order_index: int
    place_id: str
    arrival_time: datetime | None = None
    stay_minutes: int | None = None
    snapshot: dict | None = None        # { "name": "...", "category": "...", ... }
```

#### **`ItineraryPlanResponse`**

```python
class ItineraryPlanResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    total_days: int
    currency: str
    created_at: datetime
    stops: list[ItineraryStopResponse]
```

---

## **6\. Planner Router & Service**

### **6.1. `app/planner_app/api/router.py`**

* Tạo `APIRouter(prefix="/planner", tags=["planner"])`.
* Include `itineraries_router`.

### **6.2. `app/planner_app/api/itineraries_router.py`**

```python
@router.post("/itineraries/plan", response_model=ItineraryPlanResponse)
async def plan_itinerary(
    request: ItineraryPlanRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),  # From Supabase JWT
):
    ...

@router.get("/itineraries/{itinerary_id}", response_model=ItineraryPlanResponse)
async def get_itinerary(
    itinerary_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ...
```

### **6.3. `app/api/v1/router.py`**

```python
api_router.include_router(planner_router, prefix="/planner", tags=["planner"])
api_router.include_router(guide_router, prefix="/guide", tags=["guide"])  # optional
```

### **6.4. `app/main.py`**

* Tạo app FastAPI, include `api/v1/router.py`.

---

## **7\. Itinerary Service & Repository**

### **7.1. Repository – `app/shared/repositories/itinerary_repository.py`**

```python
class ItineraryRepository(BaseRepository):
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
        ...

    async def get_with_stops(
        self,
        db: AsyncSession,
        itinerary_id: uuid.UUID,
    ) -> Itinerary:
        ...
```

### **7.2. Service – `app/planner_app/services/itinerary_service.py`**

```python
class ItineraryService:
    def __init__(self, itinerary_repo: ItineraryRepository, planner_agent: PlannerAgent):
        ...

    async def create_itinerary_plan(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,  # From JWT
        request: ItineraryPlanRequest,
    ) -> ItineraryPlanResponse:
        """
        1. Gọi planner_agent.create_itinerary(...) để nhận PlannerItineraryResult.
        2. Lưu itinerary + stops vào Supabase Postgres.
        3. Map sang ItineraryPlanResponse.
        """

    async def get_itinerary(
        self,
        db: AsyncSession,
        itinerary_id: uuid.UUID,
    ) -> ItineraryPlanResponse:
        ...
```

---

## **8\. Planner Agent & Graph Logic**

### **8.1. TSP Solver – `app/shared/graph/tsp_solver.py`**

```python
async def nearest_neighbor_tsp(
    points: list[tuple[float, float]],
    start_index: int = 0,
) -> list[int]:
    """
    points: list of (lat, lng)
    return: order of indices representing visiting sequence
    """
```

### **8.2. Place Graph Service – `app/shared/graph/place_graph_service.py`**

```python
class PlaceGraphService:
    def __init__(self, neo4j_client: Neo4jClient):
        ...

    async def find_restaurant_and_cafe_for_evening(
        self,
        interests: list[str] | None,
        max_distance_km: float = 3.0,
    ) -> dict:
        """MVP: Hardcode logic đơn giản"""
```

### **8.3. PlannerAgent – `app/planner_app/agents/planner_agent.py`**

```python
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
    def __init__(self, place_graph_service: PlaceGraphService):
        ...

    async def create_itinerary(
        self,
        request: ItineraryPlanRequest,
    ) -> PlannerItineraryResult:
        """MVP: Rule-based, không dùng LLM"""
```

---

## **9\. Testing**

### **9.1. `app/planner_app/tests/test_itinerary_api.py`**

1. Test `POST /api/v1/planner/itineraries/plan`:
   * Input: sample request + valid JWT
   * Expect: Status 200, có `id`, `stops` length >= 1

2. Test `GET /api/v1/planner/itineraries/{id}`:
   * Gọi sau khi tạo
   * Expect trả đúng itinerary

3. Test unauthorized access:
   * No JWT → 401
