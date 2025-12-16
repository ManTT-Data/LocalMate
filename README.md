# 🏖️ Da Nang Tourism RAG API

AI-powered destination recommendations for Da Nang, Vietnam. Combines semantic vector search with graph-based relationships.

## Features

- 🔍 **Text Search** - Natural language search in Vietnamese/English
- 🖼️ **Image Search** - Find places by uploading photos
- 📍 **Location Search** - Find nearby places using GPS
- 🏷️ **Category Search** - Filter by cafe, restaurant, hotel, etc.
- 📊 **Place Details** - Full info with photos, reviews, nearby places

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_rag.txt
```

### 2. Configure Environment

Copy the example env file and fill in your credentials:

```bash
cp .env.example .env
```

Required variables:
```bash
# Neo4j (Graph Database)
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password

# Supabase (Vector Database)
SUPABASE_DB_PASSWORD="your-password"
SUPABASE_DB_HOST=aws-1-ap-northeast-2.pooler.supabase.com
SUPABASE_DB_USER=postgres.your-project-id

# Google AI (Embeddings)
GOOGLE_API_KEY=your-api-key
```

### 3. Run API Server

```bash
cd api
python main.py
```

API will be available at:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 4. Test API

```bash
python test_api.py
```

## API Endpoints

### Search

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/search` | POST | Text search with query body |
| `/search` | GET | Simple search via URL `?q=...` |
| `/search/category/{cat}` | GET | Category-based search |
| `/search/location` | POST | Search by GPS coordinates |
| `/search/image` | POST | Image-based search (upload) |

### Places (Neo4j)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/places/{place_id}` | GET | Full place details + nearby |
| `/places/{place_id}/nearby` | GET | Nearby places only |

### System

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/health` | GET | Health check |
| `/docs` | GET | Swagger UI |

## Usage Examples

### Text Search
```bash
curl "http://localhost:8000/search?q=quán+cafe+view+đẹp&limit=5"
```

### Image Search
```bash
curl -X POST "http://localhost:8000/search/image" \
  -F "image=@my_photo.jpg" \
  -F "max_results=5"
```

### Get Place Details
```bash
curl "http://localhost:8000/places/{place_id}"
```

## Project Structure

```
.
├── api/
│   ├── main.py              # FastAPI application
│   ├── rag_service.py       # Text search service
│   ├── image_service.py     # Image search service
│   ├── neo4j_service.py     # Neo4j graph queries
│   └── API_DOCUMENTATION.md # Full API docs
├── rag_pipeline/            # RAG data pipeline
├── streamlit_demo.py        # Demo UI
├── test_api.py              # API test script
├── .env.example             # Environment template
└── requirements_rag.txt     # Python dependencies
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI (main.py)                        │
├─────────────────────────────────────────────────────────────┤
│  /search/*       → rag_service.py    → Supabase (pgvector) │
│  /search/image   → image_service.py  → SigLIP + pgvector   │
│  /places/*       → neo4j_service.py  → Neo4j AuraDB        │
└─────────────────────────────────────────────────────────────┘
```

## Data Sources

| Source | Data | Usage |
|--------|------|-------|
| **Supabase** | Text & Image embeddings | Vector similarity search |
| **Neo4j** | Places, photos, reviews, spatial relationships | Graph queries |

## Documentation

- [API Documentation](api/API_DOCUMENTATION.md) - Full endpoint reference
- [Swagger UI](http://localhost:8000/docs) - Interactive API explorer

## License

MIT
