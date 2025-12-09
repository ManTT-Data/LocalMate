# LocalMate Da Nang

Danang Tourism Super Agent API - AI Travel Planner for Da Nang.

## Tech Stack

- **Framework**: FastAPI
- **Database**: Supabase (PostgreSQL + Auth + pgvector)
- **Graph DB**: Neo4j Aura
- **LLM**: Google Gemini 2.5 Flash
- **Embeddings**: text-embedding-004 + CLIP

## Quick Start

```bash
# Install dependencies
pip install -e ".[dev]"

# Copy env file
cp .env.example .env
# Edit .env with your credentials

# Run dev server
uvicorn app.main:app --reload

# Run tests
pytest app/ -v
```

## Documentation

See [docs/](docs/) for detailed documentation.
