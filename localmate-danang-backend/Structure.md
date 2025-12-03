# LocalMate Da Nang Backend - Structure Documentation

> **Mục đích**: Tài liệu này giải thích chi tiết cấu trúc folder và nhiệm vụ của từng thành phần để các developer có thể dễ dàng hiểu và code.

## 📋 Tổng quan kiến trúc

LocalMate backend được thiết kế với **hai agent độc lập** chia sẻ chung **hạ tầng (shared infrastructure)**:

- **✈️ Planner App**: AI Travel Planner cho du khách (tourists)
- **🚕 Guide App**: AI Guide Pack cho tài xế Grab (drivers)

### Nguyên tắc thiết kế

1. **Separation of Concerns**: Mỗi dev team có thể làm việc độc lập trên một app
2. **Shared Infrastructure**: Tránh duplicate code, dùng chung models, DB, integrations
3. **Clean Architecture**: API → Services → Agents → Repositories → Models

---

## 🗂️ Folder Structure Overview

```
localmate-danang-backend/
├─ README.md                    # Project overview
├─ pyproject.toml              # Python dependencies
├─ alembic.ini                 # Database migrations config
├─ .env.example                # Environment variables template
├─ .env                        # Actual env vars (gitignored)
│
└─ app/
   ├─ main.py                  # FastAPI entry point
   ├─ config.py                # Global settings
   │
   ├─ shared/                  # SHARED INFRASTRUCTURE
   │  ├─ core/                 # Core utilities (logging, exceptions, helpers)
   │  ├─ constants/            # Constants and prompts
   │  ├─ db/                   # Database layer
   │  ├─ models/               # SQLAlchemy models
   │  ├─ repositories/         # Database repositories
   │  ├─ integrations/         # External services (LLM, Neo4j, Vector DB, MCP)
   │  ├─ graph/                # Graph-RAG engine (placeholder)
   │  └─ utils/                # Utility functions (placeholder)
   │
   ├─ planner_app/             # PLANNER APP (Tourist Agent)
   │  ├─ api/                  # HTTP endpoints
   │  ├─ schemas/              # Pydantic models
   │  ├─ agents/               # AI agents
   │  ├─ services/             # Business logic
   │  └─ tests/                # Tests
   │
   └─ guide_app/               # GUIDE APP (Driver Agent)
      ├─ api/                  # HTTP endpoints
      ├─ schemas/              # Pydantic models
      ├─ agents/               # AI agents
      ├─ services/             # Business logic
      └─ tests/                # Tests
```

---

## 🏗️ Root Level Files

### README.md
- Project overview và quick start guide
- Tech stack documentation
- Development instructions

### pyproject.toml
- Python package configuration
- Dependencies: FastAPI, SQLAlchemy, Neo4j, OpenAI, etc.
- Dev tools: pytest, black, ruff, mypy

### alembic.ini
- Database migration configuration
- Points to `app/shared/db/migrations/` for migration scripts

### .env.example
- Template cho environment variables
- Copy to `.env` và điền values thật

---

## 📦 app/main.py - Application Entry Point

**Nhiệm vụ**:
- Khởi tạo FastAPI app
- Mount 2 routers:
  - `/api/v1/planner/*` → Planner App
  - `/api/v1/guide/*` → Guide App
- Basic CORS configuration

**Dev workflow**:
- Tech lead chỉnh khi cần thêm routers
- Developers thường không cần động vào file này

> **Note**: Đã đơn giản hóa middleware cho hackathon, chỉ giữ lại CORS cơ bản

---

## ⚙️ app/config.py - Configuration

**Nhiệm vụ**:
- Đọc environment variables từ `.env`
- Provide `settings` object cho toàn bộ app
- Sử dụng Pydantic Settings cho type safety

**Các biến quan trọng**:
- `POSTGRES_URL`: PostgreSQL connection string
- `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`: Neo4j Graph DB
- `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`: LLM providers
- `GRAB_API_KEY`: MCP tool credentials

---

## 🌐 shared/ - Shared Infrastructure

### shared/core/ - Core Utilities

| File | Nhiệm vụ |
|------|----------|
| `logging.py` | Setup logging chuẩn, `get_logger()` function |
| `exceptions.py` | Custom exceptions (`NotFoundException`, `BadRequestException`, etc.) |
| `helpers.py` | Utility functions (normalize_text, safe_dict, etc.) |

**Khi nào dùng**:
- Import `get_logger(__name__)` ở mọi file cần log
- Dùng `raise_not_found()`, `raise_bad_request()` trong services

---

### shared/db/ - Database Layer

| File/Folder | Nhiệm vụ |
|-------------|----------|
| `session.py` | SQLAlchemy async engine, `get_db()` dependency |
| `migrations/` | Alembic migration scripts |
| `migrations/env.py` | Alembic environment config |

**Dev workflow**:
1. Thay đổi models trong `shared/models/`
2. Chạy: `alembic revision --autogenerate -m "description"`
3. Review migration file
4. Chạy: `alembic upgrade head`

---

### shared/models/ - ORM Models

Tất cả các table trong PostgreSQL:

| File | Model | Mô tả |
|------|-------|-------|
| `user.py` | `User` | User accounts (tourist, driver, admin) + preferences |
| `place.py` | `Place` | Địa điểm (restaurant, cafe, attraction) với coordinates |
| `itinerary.py` | `Itinerary`, `ItineraryStop` | Travel plans và stops |
| `booking.py` | `Booking` | Booking records từ MCP tools (Grab, Hotels) |
| `driver.py` | `DriverProfile` | Driver profiles, languages, ratings |
| `affiliate.py` | `AffiliateProgram` | Affiliate venues với commission structure |

**Quan hệ**:
- `User` 1-N `Itinerary` 1-N `ItineraryStop` N-1 `Place`
- `User` 1-N `Booking`
- `User` 1-1 `DriverProfile`
- `Place` 1-N `AffiliateProgram`

---

### shared/repositories/ - Data Access Layer

**Pattern**: Repository pattern để tách biệt DB logic khỏi business logic

| File | Repository | Methods |
|------|-----------|---------|
| `base.py` | `BaseRepository` | Generic CRUD: `get()`, `list()`, `create()`, `update()`, `delete()` |
| `user_repository.py` | `UserRepository` | `get_by_email()`, `get_by_role()` |
| `place_repository.py` | `PlaceRepository` | `get_by_category()`, `search_by_name()`, `get_nearby_simple()` |
| `itinerary_repository.py` | `ItineraryRepository` | `get_with_stops()`, `create_with_stops()` |
| `booking_repository.py` | `BookingRepository` | `get_by_user()`, `get_by_external_id()` |
| `driver_repository.py` | `DriverRepository` | `get_by_grab_id()` |

**Usage trong services**:
```python
from app.shared.repositories.place_repository import PlaceRepository

async def my_service(db: AsyncSession):
    repo = PlaceRepository(db)
    places = await repo.get_by_category("restaurant")
```

---

### shared/integrations/ - External Services

| File/Folder | Service | Nhiệm vụ |
|-------------|---------|----------|
| `neo4j_client.py` | Neo4j | Graph database queries, Cypher execution |
| `llm_client.py` | LLM | Unified API cho OpenAI, Anthropic, Google Gemini |
| `supabase_vector_client.py` | Vector DB | Vector embeddings và semantic search |
| `mcp/grab_transport_tool.py` | Grab API | Price estimate, ride booking |

**Global instances**:
```python
from app.shared.integrations.llm_client import llm_client
from app.shared.integrations.neo4j_client import neo4j_client

response = await llm_client.chat_completion(messages)
results = await neo4j_client.run_cypher(query, params)
```

---

### shared/graph/ - Graph-RAG Engine

**Folder hiện tại trống - placeholder cho future Graph-RAG implementation**

> **Note**: Graph-RAG functionality đã được đơn giản hóa cho hackathon. Các tính năng phức tạp như pathfinding, vector search, và advanced RAG pipeline sẽ được implement sau.

---

### shared/utils/ - Utility Functions

**Folder hiện tại trống - placeholder cho future utility functions**

> **Note**: Các utility functions đã được đơn giản hóa hoặc inline vào các modules cần thiết để giảm complexity cho hackathon.

---

## ✈️ planner_app/ - AI Travel Planner

**Mục đích**: Tạo itinerary cho tourists sử dụng Graph-RAG

### planner_app/api/ - HTTP Endpoints

| File | Endpoints |
|------|-----------|
| `router.py` | Root router, includes all sub-routes |
| `itineraries_router.py` | `POST /itineraries/plan`, `GET /itineraries/{id}`, `GET /itineraries/user/{user_id}` |

**Flow**:
1. Client POST `/api/v1/planner/itineraries/plan` với `ItineraryPlanRequest`
2. Route handler gọi `ItineraryService.create_itinerary_plan()`
3. Return `ItineraryPlanResponse`

### planner_app/schemas/ - Pydantic Models

| File | Schemas |
|------|---------|
| `itinerary_schemas.py` | `ItineraryPlanRequest`, `ItineraryPlanResponse`, `ItineraryStopResponse`, `ItineraryDetail` |

**Request Example**:
```json
{
  "user_id": 1,
  "duration_days": 3,
  "family_size": 4,
  "interests": ["beach", "seafood", "culture"],
  "budget": "medium"
}
```

### planner_app/agents/ - AI Agents

| File | Agent | Nhiệm vụ |
|------|-------|----------|
| `planner_agent.py` | `PlannerAgent` | **Core AI**: Generate itinerary using Graph-RAG + TSP + LLM |

**Agent Flow**:
1. Find candidate places via `rag_pipeline`
2. Optimize route via TSP pathfinding
3. Generate descriptions via LLM
4. Return structured itinerary with stops

### planner_app/services/ - Business Logic

| File | Service | Nhiệm vụ |
|------|---------|----------|
| `itinerary_service.py` | `ItineraryService` | Orchestrate agent + repository, save to DB |

**Responsibilities**:
- Call `planner_agent.create_itinerary()`
- Save itinerary + stops to PostgreSQL via repository
- Convert DB models to response schemas

---

## 🚕 guide_app/ - AI Guide Pack

**Mục đích**: Generate Guide Pack cho Grab drivers với tips, stories, language cards

### guide_app/api/ - HTTP Endpoints

| File | Endpoints |
|------|-----------|
| `router.py` | Root router |
| `driver_guide_router.py` | `POST /guide-pack/generate`, `GET /guide-pack/trip/{trip_id}` |

### guide_app/schemas/ - Pydantic Models

| File | Schemas |
|------|---------|
| `guide_pack_schemas.py` | `GuidePackRequest`, `GuidePackResponse`, `GuidePackCard`, `LanguageCard` |

**Card Types**:
- `place_info`: Thông tin địa điểm
- `fun_fact`: Fun facts về địa điểm
- `local_tip`: Local tips từ AI
- `language_card`: Quick phrases (EN/VI/JA/KO/ZH)
- `affiliate`: Gợi ý venues có hoa hồng

### guide_app/agents/ - AI Agents

| File | Agent | Nhiệm vụ |
|------|-------|----------|
| `guide_agent.py` | `GuideAgent` | Generate guide pack: place info + fun facts + language cards |

**Agent Flow**:
1. Query Graph-RAG for place context
2. Generate fun facts via LLM
3. Generate local tips via LLM
4. Create language phrase cards
5. Return structured guide pack

### guide_app/services/ - Business Logic

| File | Service | Nhiệm vụ |
|------|---------|----------|
| `guide_pack_service.py` | `GuidePackService` | Orchestrate agent, find current place, generate pack |

---

## 👥 Development Workflow

### Dev Team A: Planner App
**Working folder**: `app/planner_app/`

**Tasks**:
1. Implement API routes trong `api/`
2. Define schemas trong `schemas/`
3. Develop agents trong `agents/`
4. Write business logic trong `services/`
5. Write tests trong `tests/`

**Shared dependencies**:
- Dùng `shared/repositories/` để truy vấn DB
- Dùng `shared/graph/rag_pipeline` cho AI recommendations
- Dùng `shared/integrations/llm_client` cho LLM calls

### Dev Team B: Guide App
**Working folder**: `app/guide_app/`

**Tasks**:
1. Implement API routes trong `api/`
2. Define schemas trong `schemas/`
3. Develop agents trong `agents/`
4. Write business logic trong `services/`
5. Write tests trong `tests/`

**Shared dependencies**: Giống như Planner App

---

## 🔄 Data Flow Examples

### Planner App: Create Itinerary
```
Client Request
    ↓
POST /api/v1/planner/itineraries/plan
    ↓
itineraries_router.py → ItineraryService.create_itinerary_plan()
    ↓
PlannerAgent.create_itinerary()
    ├─→ rag_pipeline.find_places_with_context() (Graph-RAG)
    ├─→ nearest_neighbor_tsp() (Route optimization)
    └─→ llm_client.chat_completion() (Generate descriptions)
    ↓
ItineraryRepository.create_with_stops() (Save to DB)
    ↓
ItineraryPlanResponse → Client
```

### Guide App: Generate Guide Pack
```
Client Request (Driver)
    ↓
POST /api/v1/guide/guide-pack/generate
    ↓
driver_guide_router.py → GuidePackService.generate_guide_pack()
    ↓
GuideAgent.generate_guide_pack()
    ├─→ rag_pipeline.find_places_with_context() (Place info)
    ├─→ llm_client.chat_completion() (Fun facts + tips)
    └─→ _generate_language_cards() (Phrases)
    ↓
GuidePackResponse → Client (Driver App)
```

---

## 🧪 Testing

### Folder structure
- `app/planner_app/tests/` - Planner App tests
- `app/guide_app/tests/` - Guide App tests

### Run tests
```bash
# All tests
pytest

# Specific app
pytest app/planner_app/tests/
pytest app/guide_app/tests/

# With coverage
pytest --cov=app
```

---

## 🚀 Getting Started

### 1. Setup Environment
```bash
# Clone repo
git clone <repo-url>
cd localmate-danang-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env với credentials thật
```

### 3. Run Migrations
```bash
alembic upgrade head
```

### 4. Start Server
```bash
uvicorn app.main:app --reload
```

### 5. Access API Docs
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 📝 Code Conventions

### Import Order
1. Standard library
2. Third-party packages
3. Local imports (shared)
4. Local imports (app-specific)

### Naming
- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions/variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`

### Type Hints
- Always use type hints for function arguments and return values
- Use `Optional[T]` for nullable values

---

## 🎯 Key Takeaways

1. **Separation**: Planner App và Guide App hoàn toàn tách biệt
2. **Shared Infrastructure**: Tất cả common logic ở `shared/`
3. **Repository Pattern**: Services gọi repositories, không trực tiếp ORM
4. **Graph-RAG**: Core của AI recommendations
5. **Async Everything**: Use async/await throughout
6. **Type Safety**: Pydantic schemas cho validation

---

## 📚 Additional Resources

- FastAPI Docs: https://fastapi.tiangolo.com/
- SQLAlchemy Async: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- Neo4j Python Driver: https://neo4j.com/docs/api/python-driver/current/
- Alembic Migrations: https://alembic.sqlalchemy.org/

---

**Happy Coding! 🚀**
