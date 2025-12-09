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

Khi du khách đi theo lịch trình được AI tạo, tài xế sẽ nhận được một “gói hướng dẫn mini” tự động:

Giới thiệu ngắn gọn về địa điểm

Fun facts / lịch sử

Góc chụp đẹp / giờ đông – giờ vắng

Câu nói nhanh đa ngôn ngữ

Gợi ý chia sẻ như một “local buddy”

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

  * Lưu itinerary vào **PostgreSQL**.

  * Cung cấp API để frontend hiển thị lại itinerary.

* **Guide Pack Agent** cho tài xế chỉ là **phase sau**, hiện tại chỉ cần placeholder (không phải làm ngay).

### **0.2. Công nghệ & phiên bản**

* **Ngôn ngữ**: Python 3.11+

* **Framework**: FastAPI

* **DB quan hệ**: PostgreSQL (SQLAlchemy Async \+ Alembic)

* **Graph DB**: Neo4j Aura (có sẵn data 302 địa điểm)

* **LLM**: OpenAI / Anthropic / Gemini (gói gọn trong `llm_client` – phase sau)

* **Style bắt buộc**:

  * Sử dụng **async/await** cho I/O (DB, HTTP, Neo4j).

  * Luôn dùng **type hints** đầy đủ.

  * Dùng **Pydantic v2** (nếu có thể).

  * Code phải **theo cấu trúc project** bên dưới.

---

## **2\. Cấu hình & Environment**

### **2.1. File `.env.example`**

Cursor phải tạo file `.env.example` với các biến sau:

`# FastAPI`  
`APP_ENV=local`  
`APP_DEBUG=true`

`# Postgres`  
`POSTGRES_URL=postgresql+asyncpg://user:password@localhost:5432/localmate`

`# Neo4j`  
`NEO4J_URI=neo4j+s://64ff7b02.databases.neo4j.io`  
`NEO4J_USER=neo4j`  
`NEO4J_PASSWORD=CHANGE_ME`

`# LLM (phase sau)`  
`OPENAI_API_KEY=your_openai_key_here`  
`ANTHROPIC_API_KEY=your_anthropic_key_here`  
`GOOGLE_API_KEY=your_gemini_key_here`

### **2.2. `app/core/config.py`**

* Tạo class `Settings(BaseSettings)` với các field trên.

* Tạo function `get_settings()` dùng `lru_cache()`.

---

## **3\. Database – PostgreSQL Schema (Supabase)**

### **3.1. `app/shared/models/base.py`**

* Tạo `Base = declarative_base()` (SQLAlchemy 2 style).

* Thêm mixin `TimestampMixin` có `created_at`, `updated_at`.

### **3.2. Model `User` – `user.py`**

Bảng `users`:

* user\_id: UUID, primary key

* user\_email: unique, not null

* user\_password\_hash: text, nullable (cho phép social login)

* user\_full\_name: text, not null

* user\_phone: text, nullable

* user\_role: text, not null (enum: `tourist`, `driver`, `admin`)

* user\_locale: text, default `'vi_VN'`

* timezone: text, default `'Asia/Ho_Chi_Minh'`

Tạo SQLAlchemy model:

`class User(Base, TimestampMixin):`  
    `__tablename__ = "users"`

    `user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)`  
    `user_email: Mapped[str] = mapped_column(String, unique=True, index=True)`  
    `user_password_hash: Mapped[str | None]`  
    `user_full_name: Mapped[str]`  
    `user_phone: Mapped[str | None]`  
    `user_role: Mapped[str]  # validate in code`  
    `user_locale: Mapped[str] = mapped_column(String, default="vi_VN")`  
    `timezone: Mapped[str] = mapped_column(String, default="Asia/Ho_Chi_Minh")`

### **3.3. Model `Itinerary` & `ItineraryStop` – `itinerary.py`**

**Bảng `itineraries`:**

* itinerary\_id: UUID

* itinerary\_user\_id: FK → users.id

* itinerary\_title: text

* itinerary\_start\_date: date (nullable)

* itinerary\_end\_date: date (nullable)

* itinerary\_total\_days: int

* itinerary\_total\_budget: numeric(12,2), nullable

* itinerary\_currency: text, default `'VND'`

* itinerary\_meta: JSONB (tùy ý: interests, budget level, etc.)

**Bảng `itinerary_stops`:**

* stop\_id: UUID

* stop\_itinerary\_id: FK → itineraries.id

* stop\_day\_index: int (\>=1)

* stop\_order\_index: int (\>=1)

* stop\_place\_id: text (string của Neo4j `Place.id`)

* arrival\_time: timestamptz, nullable

* stay\_minutes: int, nullable

* stop\_notes: text, nullable

* stop\_tags: text\[\] (optional)

* stop\_snapshot: JSONB, nullable (store name, rating…)

Cursor phải tạo model tương ứng.

### **3.4. Alembic**

* `alembic.ini` cấu hình `script_location = app/shared/db/migrations`.

* `env.py` phải import `Base.metadata` từ `app.shared.models.base`.

Cursor phải:

1. Tạo cấu hình Alembic.

2. Tạo migration `init_core_schema` với các bảng:

   * `users`

   * `itineraries`

   * `itinerary_stops`

3. Generate và upgrade.

---

## **4\. Neo4j Integration**

### **4.1. `app/shared/integrations/neo4j_client.py`**

* Class `Neo4jClient` với:

`class Neo4jClient:`  
    `def __init__(self, uri: str, user: str, password: str): ...`  
    `async def run_cypher(self, query: str, params: dict | None = None) -> list[dict]: ...`

* Sử dụng Neo4j Python driver (async nếu có thể, không thì sync \+ `run_in_threadpool`).

* Tạo instance global: `neo4j_client = Neo4jClient(settings.neo4j_uri, ...)`.

---

## **5\. Planner API – Spec chi tiết**

### **5.1. Endpoints**

1. `POST /api/v1/planner/itineraries/plan`

2. `GET /api/v1/planner/itineraries/{itinerary_id}`

### **5.2. Request / Response Models**

**File:** `app/planner_app/schemas/itinerary_schemas.py`

#### **`ItineraryPlanRequest`**

Cursor phải định nghĩa kiểu:

`class ItineraryPlanRequest(BaseModel):`  
    `user_id: uuid.UUID`  
    `duration_days: int = Field(ge=1)`  
    `family_size: int | None = None`  
    `interests: list[str] | None = None   # ["beach", "seafood", "coffee"]`  
    `budget: str | None = None            # "low", "medium", "high"`  
    `start_date: date | None = None`  
    `start_location_lat: float | None = None`  
    `start_location_lng: float | None = None`

#### **`ItineraryStopResponse`**

`class ItineraryStopResponse(BaseModel):`  
    `id: uuid.UUID`  
    `day_index: int`  
    `order_index: int`  
    `place_id: str`  
    `arrival_time: datetime | None = None`  
    `stay_minutes: int | None = None`  
    `snapshot: dict | None = None        # { "name": "...", "category": "...", ... }`

#### **`ItineraryPlanResponse`**

`class ItineraryPlanResponse(BaseModel):`  
    `id: uuid.UUID`  
    `user_id: uuid.UUID`  
    `title: str`  
    `total_days: int`  
    `currency: str`  
    `created_at: datetime`  
    `stops: list[ItineraryStopResponse]`

---

## **6\. Planner Router & Service**

### **6.1. `app/planner_app/api/router.py`**

* Tạo `APIRouter(prefix="/planner", tags=["planner"])`.

* Include `itineraries_router`.

### **6.2. `app/planner_app/api/itineraries_router.py`**

* Tạo 2 endpoint:

`@router.post("/itineraries/plan", response_model=ItineraryPlanResponse)`  
`async def plan_itinerary(`  
    `request: ItineraryPlanRequest,`  
    `db: AsyncSession = Depends(get_db),`  
`):`  
    `...`

`@router.get("/itineraries/{itinerary_id}", response_model=ItineraryPlanResponse)`  
`async def get_itinerary(`  
    `itinerary_id: uuid.UUID,`  
    `db: AsyncSession = Depends(get_db),`  
`):`  
    `...`

### **6.3. `app/api/v1/router.py`**

* Tạo `APIRouter(prefix="/api/v1")` và include:

`api_router.include_router(planner_router, prefix="/planner", tags=["planner"])`  
`api_router.include_router(guide_router, prefix="/guide", tags=["guide"])  # optional`

### **6.4. `app/main.py`**

* Tạo app FastAPI, include `api/v1/router.py`.

---

## **7\. Itinerary Service & Repository**

### **7.1. Repository – `app/shared/repositories/itinerary_repository.py`**

Cursor phải tạo class:

`class ItineraryRepository(BaseRepository):`  
    `async def create_with_stops(`  
        `self,`  
        `db: AsyncSession,`  
        `user_id: uuid.UUID,`  
        `title: str,`  
        `total_days: int,`  
        `currency: str,`  
        `meta: dict | None,`  
        `stops: list[dict],`  
    `) -> Itinerary:`  
        `...`

    `async def get_with_stops(`  
        `self,`  
        `db: AsyncSession,`  
        `itinerary_id: uuid.UUID,`  
    `) -> Itinerary:`  
        `...`

* `stops` là list dict có:

  * `day_index`

  * `order_index`

  * `place_id`

  * optional: `stay_minutes`, `snapshot`.

### **7.2. Service – `app/planner_app/services/itinerary_service.py`**

Tạo class:

`class ItineraryService:`  
    `def __init__(self, itinerary_repo: ItineraryRepository, planner_agent: PlannerAgent):`  
        `...`

    `async def create_itinerary_plan(`  
        `self,`  
        `db: AsyncSession,`  
        `request: ItineraryPlanRequest,`  
    `) -> ItineraryPlanResponse:`  
        `"""`  
        `1. Gọi planner_agent.create_itinerary(...) để nhận PlannerItineraryResult.`  
        `2. Lưu itinerary + stops vào Postgres.`  
        `3. Map sang ItineraryPlanResponse.`  
        `"""`

    `async def get_itinerary(`  
        `self,`  
        `db: AsyncSession,`  
        `itinerary_id: uuid.UUID,`  
    `) -> ItineraryPlanResponse:`  
        `"""`  
        `1. Lấy itinerary + stops từ DB.`  
        `2. (Phase sau) Có thể join với Neo4j để enrich.`  
        `"""`

---

## **8\. Planner Agent & Graph Logic**

### **8.1. TSP Solver – `app/shared/graph/tsp_solver.py`**

Cursor phải implement hàm:

`async def nearest_neighbor_tsp(`  
    `points: list[tuple[float, float]],`  
    `start_index: int = 0,`  
`) -> list[int]:`  
    `"""`  
    `points: list of (lat, lng)`  
    `return: order of indices representing visiting sequence (starting from start_index)`  
    `"""`

* Logic: heuristic Nearest Neighbor:

  * Bắt đầu ở `start_index`.

  * Mỗi lần chọn điểm chưa đi có khoảng cách nhỏ nhất.

### **8.2. Place Graph Service – `app/shared/graph/place_graph_service.py`**

Cursor phải implement class:

`class PlaceGraphService:`  
    `def __init__(self, neo4j_client: Neo4jClient):`  
        `...`

    `async def find_restaurant_and_cafe_for_evening(`  
        `self,`  
        `interests: list[str] | None,`  
        `max_distance_km: float = 3.0,`  
    `) -> dict:`  
        `"""`  
        `MVP example flow:`  
        `1. Tìm 1 nhà hàng hải sản gần biển Mỹ Khê (hardcode region hoặc nhận param).`  
        `2. Tìm 1 quán cafe yên tĩnh gần nhà hàng đó (NEAR relationship).`  
        `3. Return:`  
           `{`  
             `"places": [`  
               `{"place_id": "...", "lat": ..., "lng": ..., "category": "restaurant", ...},`  
               `{"place_id": "...", "lat": ..., "lng": ..., "category": "cafe", ...}`  
           `]`  
           `}`  
        `"""`

Ghi chú: MVP chỉ cần hardcode logic đơn giản:

* Restaurant category chứa "restaurant" & specialty "seafood", rating \>= 4.0.

* Cafe category chứa "cafe", NEAR restaurant \< max\_distance\_km.

### **8.3. PlannerAgent – `app/planner_app/agents/planner_agent.py`**

`@dataclass`  
`class PlannerStop:`  
    `place_id: str`  
    `lat: float`  
    `lng: float`  
    `day_index: int`  
    `order_index: int`  
    `snapshot: dict | None = None`

`@dataclass`  
`class PlannerItineraryResult:`  
    `title: str`  
    `total_days: int`  
    `currency: str`  
    `stops: list[PlannerStop]`

`class PlannerAgent:`  
    `def __init__(self, place_graph_service: PlaceGraphService):`  
        `...`

    `async def create_itinerary(`  
        `self,`  
        `request: ItineraryPlanRequest,`  
    `) -> PlannerItineraryResult:`  
        `"""`  
        `MVP flow:`  
        `1. Ignore LLM. Dùng rule-based qua PlaceGraphService.`  
        `2. Lấy about 2 places: restaurant + cafe.`  
        `3. Dùng tsp_solver.nearest_neighbor_tsp để sắp xếp 2+ điểm (nếu cần).`  
        `4. Đóng gói thành PlannerItineraryResult:`  
           `- title: generate đơn giản, ví dụ "Evening in Da Nang"`  
           `- total_days = request.duration_days`  
           `- currency = "VND"`  
        `"""`

**Phase sau** mới thêm LLM và Graph-RAG nâng cao.

---

## **9\. Testing**

### **9.1. `app/planner_app/tests/test_itinerary_api.py`**

Cursor phải viết các test:

1. Test `POST /api/v1/planner/itineraries/plan`:

* Input: sample `ItineraryPlanRequest`.

* Expect:

  * Status 200\.

  * Response JSON có `id`, `stops` length \>= 1\.

  * Các stops có `place_id` dạng string không rỗng.

2. Test `GET /api/v1/planner/itineraries/{id}`:

* Gọi sau khi tạo.

* Expect trả đúng itinerary vừa tạo.

