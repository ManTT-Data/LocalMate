# 📋 LocalMate Da Nang - Implementation Phases

## 🗂 Phases

| Phase | File | Mục tiêu | Time |
|-------|------|----------|------|
| **0** | [phase_0_bootstrap.md](./phase_0_bootstrap.md) | Supabase + Neo4j + Gemini setup | 2-3h |
| **1** | [phase_1_planner_api_skeleton.md](./phase_1_planner_api_skeleton.md) | API skeleton với dummy data | 3-4h |
| **2** | [phase_2_neo4j_integration.md](./phase_2_neo4j_integration.md) | Real place data từ Neo4j | 2-3h |
| **3** | [phase_3_tsp_optimization.md](./phase_3_tsp_optimization.md) | Route optimization (TSP) | 1-2h |
| **4** | [phase_4_llm_integration.md](./phase_4_llm_integration.md) | Gemini + Embeddings + RAG | 3-4h |
| **5** | [phase_5_mcp_actions.md](./phase_5_mcp_actions.md) | MCP Action Hooks | 1-2h |
| **6** | [phase_6_guide_pack.md](./phase_6_guide_pack.md) | Guide Pack skeleton | 1h |

---

## 🔄 Dependency Graph

```
Phase 0 (Bootstrap: Supabase + Gemini)
    │
    ▼
Phase 1 (API Skeleton)
    │
    ├───► Phase 2 (Neo4j) ──► Phase 3 (TSP) ──► Phase 4 (LLM + Embeddings)
    │
    └───► Phase 5 (MCP) ──► Optional
                     
          Phase 6 (Guide Pack) ──► Future
```

---

## ✅ MVP Scope

**Bắt buộc:** Phase 0-3  
**Nên có:** Phase 4  
**Tùy chọn:** Phase 5-6

| Scope | Time |
|-------|------|
| Minimal MVP (0-3) | 8-12h |
| Full MVP (0-4) | 11-16h |
| Complete (0-6) | 14-20h |
