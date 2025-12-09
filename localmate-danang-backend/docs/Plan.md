# LocalMate Da Nang – Master Plan

Plan master tổng hợp toàn bộ thông tin dự án, database, cấu trúc thư mục và lộ trình triển khai chi tiết cho **LocalMate Da Nang**.

---

## 1. Overview
**LocalMate** là một "Danang Tourism Super Agent" hoạt động theo mô hình **Dual-Agent**:
1.  **AI Travel Planner (Planner App):** Dành cho khách du lịch. Giúp lên kế hoạch, tìm địa điểm qua Graph-RAG (Neo4j), tối ưu lộ trình (TSP), và đặt dịch vụ (MCP).
2.  **AI Guide Pack (Guide App):** Dành cho tài xế Grab. Cung cấp nội dung hướng dẫn (fun facts, tips) để tài xế trở thành "local buddy".

**Mục tiêu v0.1 (MVP):** Tập trung hoàn thiện **Planning Agent** (FastAPI + Postgres + Neo4j).

*Chi tiết xem tại:* [Overview.md](Overview.md)

---

## 2. Database Structure
Hệ thống sử dụng mô hình lai (Hybrid Database):

### PostgreSQL (Main Data)
Lưu trữ dữ liệu structured, user, booking và itinerary.
*   **users:** Tài khoản (tourist, driver).
*   **driver_profiles:** Thông tin tài xế.
*   **itineraries:** Chuyến đi của user.
*   **itinerary_stops:** Điểm dừng (liên kết với Neo4j qua `place_id`).
*   **bookings:** Giao dịch MCP.

### Neo4j (Graph Data)
Lưu trữ địa điểm (Places) và quan hệ không gian.
*   **Node:** `Place` (id, name, lat, lng, category, rating).
*   **Relation:** `NEAR` (khoảng cách), semantic relationships.

*Chi tiết xem tại:* [Database.md](Database.md)

---

## 3. Folder Structure
Dự án được tổ chức theo cấu trúc Modular Monolith:

```text
localmate-danang-backend/
├── app/
│   ├── core/           # Config, logging
│   ├── shared/         # DB session, Models, Neo4jClient, Graph Algos (TSP)
│   ├── planner_app/    # Logic chính: Agent, Service, API cho Planner
│   ├── guide_app/      # Logic cho Guide Pack (Future)
│   └── supervisor/     # Orchesration (Future)
└── docs/               # Tài liệu dự án
```

*Chi tiết xem tại:* [Folder Structure.md](Folder%20Structure.md)

---

## 4. Phases (Lộ trình triển khai)

Dự án được chia thành 7 phases, từ bootstrap đến hoàn thiện AI Agent.

| Phase | Tên Phase | Mô tả ngắn | Chi tiết |
| :--- | :--- | :--- | :--- |
| **0** | **Bootstrap** | Setup FastAPI, Poetry, Postgres (Alembic), Neo4j connection. | [Xem chi tiết](phases/phase_0_bootstrap.md) |
| **1** | **Planner API Skeleton** | Xây dựng API CRUD cho Itinerary (Dummy Agent, Data giả). | [Xem chi tiết](phases/phase_1_planner_api_skeleton.md) |
| **2** | **Neo4j Integration** | Kết nối Planner Agent với database thật (Neo4j) để tìm địa điểm. | [Xem chi tiết](phases/phase_2_neo4j_integration.md) |
| **3** | **Route Optimization (TSP)** | Tích hợp thuật toán TSP (Nearest Neighbor) để sắp xếp lộ trình đi lại tối ưu. | [Xem chi tiết](phases/phase_3_tsp_optimization.md) |
| **4** | **LLM Integration** | Tích hợp LLM để hiểu intent người dùng và tạo mô tả hấp dẫn (Graph-RAG Lite). | [Xem chi tiết](phases/phase_4_llm_integration.md) |
| **5** | **MCP Hooks** | Chuẩn bị action hooks cho việc booking (Grab, Ticket) trong tương lai. | [Xem chi tiết](phases/phase_5_mcp_actions.md) |
| **6** | **Guide Pack Agent** | (Future) Xây dựng tính năng hỗ trợ nội dung cho tài xế. | [Xem chi tiết](phases/phase_6_guide_pack.md) |
