# Quick Reference

Commands và snippets thường dùng cho LocalMate development.

---

## 🚀 Commands

```bash
# Install dependencies
pip install -e ".[dev]"

# Run dev server
uvicorn app.main:app --reload --port 8000

# Run tests
pytest app/ -v

# Run specific test
pytest app/planner_app/tests/test_itinerary_api.py -v

# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

---

## 🔗 API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/health` | No | Health check |
| POST | `/api/v1/planner/itineraries/plan` | Yes | Create itinerary |
| GET | `/api/v1/planner/itineraries/{id}` | Yes | Get itinerary |

**Test with curl:**
```bash
# Health check
curl http://localhost:8000/health

# Create itinerary (requires JWT)
curl -X POST http://localhost:8000/api/v1/planner/itineraries/plan \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"duration_days": 2, "interests": ["beach", "seafood"]}'
```

---

## 🗄️ Supabase

```python
# Get Supabase client
from app.shared.integrations.supabase_client import supabase

# Query
data = supabase.table("profiles").select("*").eq("id", user_id).execute()

# Insert
supabase.table("profiles").insert({"id": user_id, "full_name": "Test"}).execute()

# Auth - verify token
user = supabase.auth.get_user(token)
```

---

## 🧠 Gemini

```python
from app.shared.integrations.gemini_client import gemini_client

# Chat completion
response = await gemini_client.chat([
    {"role": "user", "parts": ["Hello!"]}
])

# Parse intent
intent = await gemini_client.parse_intent("seafood restaurant near beach")
```

---

## 📊 Embeddings

```python
from app.shared.integrations.embedding_client import embedding_client

# Text embedding (768-dim)
embedding = await embedding_client.embed_text("Bãi biển Mỹ Khê")

# Batch embeddings
embeddings = await embedding_client.embed_batch(["text1", "text2"])

# Semantic search
from app.shared.graph.semantic_search import search_places_semantic
places = await search_places_semantic(db, "seafood restaurant", limit=5)
```

---

## 🕸️ Neo4j

```python
from app.shared.integrations.neo4j_client import neo4j_client

# Run Cypher query
places = await neo4j_client.run_cypher(
    "MATCH (p:Place) WHERE p.category = $cat RETURN p LIMIT 10",
    {"cat": "restaurant"}
)

# Find nearby
nearby = await neo4j_client.run_cypher("""
    MATCH (p:Place)
    WITH p, point.distance(
        point({latitude: p.lat, longitude: p.lng}),
        point({latitude: $lat, longitude: $lng})
    ) / 1000 as dist
    WHERE dist <= $max_km
    RETURN p ORDER BY dist
""", {"lat": 16.05, "lng": 108.24, "max_km": 3})
```

---

## 🔐 Auth Patterns

```python
# Protected route
from app.core.security import get_current_user

@router.post("/plan")
async def plan(
    current_user: dict = Depends(get_current_user)
):
    user_id = uuid.UUID(current_user.id)
    ...

# Get user from Supabase
from app.shared.integrations.supabase_client import supabase
user = supabase.auth.get_user(token)
```

---

## 📝 Common Patterns

```python
# Repository pattern
from app.shared.repositories.itinerary_repository import itinerary_repository

itinerary = await itinerary_repository.get_with_stops(db, id)
itinerary = await itinerary_repository.create_with_stops(db, user_id, title, ...)

# Service pattern
from app.planner_app.services.itinerary_service import itinerary_service

response = await itinerary_service.create_itinerary_plan(db, user_id, request)
```
