# Tech Stack Backend - LocalMate Da Nang

> **Version**: 0.2.0  
> **Python**: ≥3.11

---

## 🚀 Core Framework

| Công nghệ | Phiên bản | Mô tả |
|-----------|-----------|-------|
| **FastAPI** | ≥0.115.0 | Web framework chính, async API |
| **Uvicorn** | ≥0.32.0 | ASGI server |
| **Pydantic** | ≥2.10.0 | Data validation & settings management |
| **pydantic-settings** | ≥2.6.0 | Configuration management |

---

## 🗄️ Databases

| Công nghệ | Phiên bản | Mục đích |
|-----------|-----------|----------|
| **PostgreSQL** (asyncpg) | ≥0.30.0 | Primary database (async driver) |
| **SQLAlchemy** | ≥2.0.0 | ORM & database toolkit |
| **Supabase** | ≥2.10.0 | Backend-as-a-Service (Auth, Storage, Realtime) |
| **Neo4j** | ≥5.26.0 | Graph database cho knowledge graph |
| **pgvector** | ≥0.3.0 | Vector embeddings cho semantic search |
| **greenlet** | ≥3.0.0 | Concurrency support cho SQLAlchemy |

---

## 🤖 AI/ML

| Công nghệ | Phiên bản | Mục đích |
|-----------|-----------|----------|
| **Google GenAI** | ≥1.0.0 | LLM integration (Gemini models) |
| **PyTorch** | ≥2.0.0 | Deep learning framework |
| **OpenCLIP** | ≥2.24.0 | Image embedding (SigLIP local model) |
| **Pillow** | ≥10.0.0 | Image processing & manipulation |

---

## 🔐 Authentication & Security

| Công nghệ | Phiên bản | Mục đích |
|-----------|-----------|----------|
| **PyJWT** | ≥2.9.0 | JWT token encoding/decoding |
| **Supabase Auth** | - | User authentication & authorization |

---

## 🔧 Utilities

| Công nghệ | Phiên bản | Mục đích |
|-----------|-----------|----------|
| **httpx** | ≥0.28.0 | Async HTTP client |
| **python-dotenv** | ≥1.0.0 | Environment variables management |
| **python-multipart** | ≥0.0.9 | Multipart form data (file uploads) |

---

## 🏗️ Architecture Patterns

### Agent Architecture
- **ReAct Agent**: Reasoning + Acting pattern cho AI agent
- **MCP (Model Context Protocol)**: Standardized protocol cho tool calling

### Project Structure
```
app/
├── agent/          # ReAct Agent implementation
├── api/            # API routes & endpoints
├── auth/           # Authentication logic
├── core/           # Core configurations
├── itineraries/    # Itinerary management
├── mcp/            # MCP tools & handlers
├── planner/        # Trip planning logic
├── shared/         # Shared utilities & models
├── upload/         # File upload handling
├── users/          # User management
└── main.py         # Application entry point
```

---

## 🐳 DevOps & Deployment

| Công nghệ | Mục đích |
|-----------|----------|
| **Docker** | Containerization |
| **Dockerfile** | Container build configuration |

---

## 🧪 Development & Testing

| Công nghệ | Phiên bản | Mục đích |
|-----------|-----------|----------|
| **pytest** | ≥8.0.0 | Testing framework |
| **pytest-asyncio** | ≥0.24.0 | Async test support |
| **httpx** | ≥0.28.0 | HTTP testing client |
| **Hatchling** | - | Build system |

---

## 📊 Key Features

1. **Multi-Modal AI**: Text + Image understanding via Google Gemini & SigLIP
2. **Semantic Search**: Vector similarity search với pgvector
3. **Knowledge Graph**: Neo4j cho entity relationships
4. **Real-time**: Supabase realtime capabilities
5. **Async-first**: Full async/await support throughout the stack
