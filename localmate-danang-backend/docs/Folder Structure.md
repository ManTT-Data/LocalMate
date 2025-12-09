# Folder Structure

```
localmate-danang-backend/
├── README.md
├── pyproject.toml
├── alembic.ini
├── .env.example
├── .env                      # gitignore
├── docs/                     # Documentation
│   ├── Overview.md
│   ├── Database.md
│   ├── Folder Structure.md
│   ├── Plan.md
│   ├── CONVENTIONS.md        # Coding standards
│   ├── QUICK_REF.md          # Quick reference
│   └── phases/
│
├── migrations/               # Alembic scripts
│
└── app/
   ├── main.py               # FastAPI entry point
   │
   ├── core/
   │   ├── config.py         # Settings (Pydantic BaseSettings)
   │   ├── logging.py        # setup_logging(), get_logger()
   │   └── security.py       # JWT verification, get_current_user()
   │
   ├── api/
   │   └── v1/
   │       └── router.py     # include_router(planner, guide)
   │
   ├── shared/
   │   ├── db/
   │   │   ├── session.py    # AsyncSession, engine, get_db()
   │   │   └── migrations/   # Alembic
   │   │
   │   ├── models/           # SQLAlchemy models
   │   │   ├── base.py       # Base = declarative_base()
   │   │   ├── profile.py    # Profile model
   │   │   ├── itinerary.py  # Itinerary + ItineraryStop
   │   │   └── embedding.py  # PlaceEmbedding (pgvector)
   │   │
   │   ├── repositories/
   │   │   ├── base_repository.py
   │   │   └── itinerary_repository.py
   │   │
   │   ├── integrations/
   │   │   ├── supabase_client.py   # Supabase client
   │   │   ├── neo4j_client.py      # Neo4j driver
   │   │   ├── gemini_client.py     # Gemini 2.5 Flash
   │   │   └── embedding_client.py  # text-embedding-004 + CLIP
   │   │
   │   ├── graph/
   │   │   ├── tsp_solver.py
   │   │   └── place_graph_service.py
   │   │
   │   ├── utils/
   │   │   └── geo_utils.py
   │   │
   │   └── constants/
   │       └── prompts/
   │           ├── planner_prompts.py
   │           └── guide_prompts.py
   │
   ├── planner_app/
   │   ├── api/
   │   │   ├── router.py
   │   │   └── itineraries_router.py
   │   │
   │   ├── schemas/
   │   │   └── itinerary_schemas.py
   │   │
   │   ├── agents/
   │   │   └── planner_agent.py
   │   │
   │   ├── services/
   │   │   └── itinerary_service.py
   │   │
   │   └── tests/
   │       └── test_itinerary_api.py
   │
   ├── guide_app/
   │   ├── api/
   │   │   ├── router.py
   │   │   └── driver_guide_router.py
   │   │
   │   ├── schemas/
   │   │   └── guide_pack_schemas.py
   │   │
   │   ├── agents/
   │   │   └── guide_agent.py
   │   │
   │   ├── services/
   │   │   └── guide_pack_service.py
   │   │
   │   └── tests/
   │
   └── supervisor/
       ├── agents/
       │   └── supervisor_agent.py
       └── services/
           └── routing_service.py
```

## Key Integration Files

| File | Purpose |
|------|---------|
| `supabase_client.py` | Supabase Auth + DB client |
| `gemini_client.py` | Gemini 2.5 Flash LLM |
| `embedding_client.py` | text-embedding-004 + CLIP |
| `neo4j_client.py` | Graph DB queries |
| `security.py` | JWT verification with Supabase |
