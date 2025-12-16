---
title: LocalMate API
emoji: 🌴
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# LocalMate Da Nang V2

Multi-Modal Contextual Agent (MMCA) API for Da Nang Tourism.

## Architecture

Based on **Model Context Protocol (MCP)** with 3 tools:
- **retrieve_context_text** - RAG Text search (pgvector)
- **retrieve_similar_visuals** - RAG Image search (CLIP)
- **find_nearby_places** - Graph Spatial (Neo4j)

## Quick Start

```bash
# Install dependencies
pip install -e ".[dev]"

# Copy env file
cp .env.example .env
# Edit .env with your credentials

# Run dev server
pkill -f "uvicorn app.main:app"
uvicorn app.main:app --reload --port 8000

# Open Swagger UI
open http://localhost:8000/docs
```

## Testing

Use the `/api/v1/chat` endpoint in Swagger to test:

```json
{
  "message": "Tìm quán cafe gần bãi biển Mỹ Khê"
}
```

## Tech Stack

- **Framework**: FastAPI
- **Database**: Supabase (PostgreSQL + pgvector)
- **Graph DB**: Neo4j Aura
- **LLM**: Google Gemini 2.5 Flash or deepseek-ai/deepseek-v3.1-terminus
- **Embeddings**: text-embedding-004 + CLIP
