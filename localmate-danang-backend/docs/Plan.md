# LocalMate Da Nang – Master Plan

## 1. Overview

**LocalMate** là "Danang Tourism Super Agent" với mô hình **Dual-Agent**:

1. **AI Travel Planner**: Lên kế hoạch, tìm địa điểm (Neo4j), tối ưu lộ trình (TSP), đặt dịch vụ.
2. **AI Guide Pack**: Nội dung hướng dẫn cho tài xế (fun facts, tips).

**MVP v0.1:** Tập trung **Planning Agent** (FastAPI + Supabase + Neo4j + Gemini).

---

## 2. Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.11+ |
| Framework | FastAPI |
| Database | **Supabase** (PostgreSQL + Auth + pgvector) |
| Auth | **Supabase Auth** (JWT) |
| Graph DB | Neo4j Aura |
| LLM | **Google Gemini 2.5 Flash** |
| Text Embedding | **text-embedding-004** |
| Image Embedding | **CLIP** (via API) |

*Chi tiết:* [Overview.md](Overview.md)

---

## 3. Database Structure

### Supabase PostgreSQL
- `profiles` – User profile (linked to `auth.users`)
- `itineraries` – Trip plans
- `itinerary_stops` – Stops (linked to Neo4j `place_id`)
- `bookings` – MCP transactions
- `place_embeddings` – Vector embeddings (pgvector)

### Neo4j
- `Place` nodes với `NEAR` relationships

*Chi tiết:* [Database.md](Database.md)

---

## 4. Folder Structure

```
app/
├── core/           # Config, logging, security
├── shared/         # DB, Models, Integrations, Graph
├── planner_app/    # Planner Agent + API
├── guide_app/      # Guide Pack (Future)
└── supervisor/     # Orchestration (Future)
```

*Chi tiết:* [Folder Structure.md](Folder%20Structure.md)

---

## 5. Phases

| Phase | Tên | Mô tả | Chi tiết |
|-------|-----|-------|----------|
| **0** | Bootstrap | Supabase + Neo4j + Gemini setup | [phase_0](phases/phase_0_bootstrap.md) |
| **1** | Planner API | API skeleton với dummy data | [phase_1](phases/phase_1_planner_api_skeleton.md) |
| **2** | Neo4j Integration | Real place data | [phase_2](phases/phase_2_neo4j_integration.md) |
| **3** | TSP Optimization | Route optimization | [phase_3](phases/phase_3_tsp_optimization.md) |
| **4** | LLM + Embeddings | Gemini + semantic search | [phase_4](phases/phase_4_llm_integration.md) |
| **5** | MCP Hooks | Booking actions | [phase_5](phases/phase_5_mcp_actions.md) |
| **6** | Guide Pack | Driver features | [phase_6](phases/phase_6_guide_pack.md) |

**MVP Scope:** Phase 0-3 (bắt buộc), Phase 4 (nên có)
