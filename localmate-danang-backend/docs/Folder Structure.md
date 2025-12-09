localmate-danang-backend/  
├─ README.md  
├─ requirements.txt  
├─ .env.example  
├─ .env                  \# gitignore  
├─ docs/  
└─ migrations/             \# Alembic scripts  
│  
└─ app/  
   ├─ main.py            \# FastAPI entry point  
   ├─ core/  
   │  ├─ config.py       \# Settings (Pydantic BaseSettings)  
   │  ├─ logging.py      \# setup\_logging(), get\_logger()  
   │  
   ├─ api/  
   │     ├─ router.py               \# include\_router(planner, guide, supervisor)  
   │  
   ├─ shared/  
   │  ├─ db/  
   │  │  ├─ session.py              \# AsyncSession, engine, get\_db()  
   │  │  
   │  ├─ models/                    \# Chỉ cho Postgres (Option A)  
   │  │  ├─ base.py                 \# Base \= declarative\_base()  
   │  │  
   │  ├─ repositories/  
   │  │  
   │  ├─ integrations/  
   │  │  
   │  ├─ graph/  
   │  │  
   │  ├─ utils/  
   │  │  
   │  └─ constants/  
   │     └─ prompts/  
   │        ├─ planner\_prompts.py  
   │        └─ guide\_prompts.py  
   │  
   ├─ planner\_app/  
   │  ├─ api/  
   │  │  ├─ router.py               \# /planner root router  
   │  │  └─ itineraries\_router.py   \# POST /itineraries/plan, GET /itineraries/{id}  
   │  │  
   │  ├─ schemas/  
   │  │  └─ itinerary\_schemas.py    \# ItineraryPlanRequest/Response...  
   │  │  
   │  ├─ agents/  
   │  │  └─ planner\_agent.py        \# dùng rag\_pipeline \+ tsp\_solver  
   │  │  
   │  ├─ services/  
   │  │  └─ itinerary\_service.py    \# orchestration \+ save DB  
   │  │  
   │  └─ tests/  
   │     └─ test\_itinerary\_api.py  
   │  
   ├─ guide\_app/  
   │  ├─ api/  
   │  │  ├─ router.py  
   │  │  └─ driver\_guide\_router.py  \# POST /guide-pack/generate...  
   │  │  
   │  ├─ schemas/  
   │  │  └─ guide\_pack\_schemas.py  
   │  │  
   │  ├─ agents/  
   │  │  └─ guide\_agent.py          \# query Neo4j \+ LLM fun facts \+ language cards  
   │  │  
   │  ├─ services/  
   │  │  └─ guide\_pack\_service.py  
   │  │  
   │  └─ tests/  
   │     └─ test\_guide\_pack\_api.py  
   │  
   └─ supervisor/  
      ├─ agents/  
      │  └─ supervisor\_agent.py     \# intent routing: Researcher/Planner/Action/Guide  
      └─ services/  
         └─ routing\_service.py      \# high-level "decide which agent \+ tools"  
