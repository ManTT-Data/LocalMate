# 📋 LocalMate Da Nang - Implementation Phases

Thư mục này chứa các file plan chi tiết cho từng phase phát triển.

---

## 🗂 Danh sách Phases

| Phase | File | Mục tiêu | Estimated Time |
|-------|------|----------|----------------|
| **0** | [phase_0_bootstrap.md](./phase_0_bootstrap.md) | FastAPI + Postgres + Neo4j setup | 2-3 hours |
| **1** | [phase_1_planner_api_skeleton.md](./phase_1_planner_api_skeleton.md) | API skeleton với dummy data | 3-4 hours |
| **2** | [phase_2_neo4j_integration.md](./phase_2_neo4j_integration.md) | Real place data từ Neo4j | 2-3 hours |
| **3** | [phase_3_tsp_optimization.md](./phase_3_tsp_optimization.md) | Route optimization (TSP) | 1-2 hours |
| **4** | [phase_4_llm_integration.md](./phase_4_llm_integration.md) | LLM Intent Parser + Graph-RAG | 3-4 hours |
| **5** | [phase_5_mcp_actions.md](./phase_5_mcp_actions.md) | MCP Action Hooks (Grab mock) | 1-2 hours |
| **6** | [phase_6_guide_pack.md](./phase_6_guide_pack.md) | Guide Pack Agent skeleton | 1 hour |

---

## 🔄 Dependency Graph

```
Phase 0 (Bootstrap)
    │
    ▼
Phase 1 (API Skeleton)
    │
    ├───► Phase 2 (Neo4j Integration)
    │         │
    │         ▼
    │     Phase 3 (TSP Optimization)
    │         │
    │         ▼
    │     Phase 4 (LLM Integration)
    │
    └───► Phase 5 (MCP Actions) ──► Optional
                                     
                      Phase 6 (Guide Pack) ──► Future Work
```

---

## ✅ MVP Scope (v0.1)

**Bắt buộc:**
- Phase 0, 1, 2, 3

**Nên có:**
- Phase 4

**Tùy chọn:**
- Phase 5, 6

---

## 📊 Tổng thời gian ước tính

| Scope | Phases | Time |
|-------|--------|------|
| Minimal MVP | 0-3 | ~8-12 hours |
| Full MVP | 0-4 | ~11-16 hours |
| Complete | 0-6 | ~14-20 hours |

---

## 🚀 Quick Start

1. Đọc và hoàn thành **Phase 0** trước
2. Tiếp tục với **Phase 1** khi Phase 0 pass acceptance criteria
3. Lần lượt hoàn thành các phase theo thứ tự
4. Mỗi phase có acceptance criteria riêng để verify

---

## 📝 Notes

- Mỗi file phase chứa:
  - 🎯 Mục tiêu
  - 📦 Deliverables
  - 📋 Tasks chi tiết với code samples
  - ✅ Acceptance criteria
  - ⏰ Estimated time

- Phase 6 (Guide Pack) là skeleton - sẽ phát triển chi tiết ở version sau
