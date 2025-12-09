# **LocalMate Da Nang – Project Implementation Plan**

## ***(plan.docs – Focus on Planning Agent)***

---

# **🧭 0\. Overview**

LocalMate nhằm xây dựng **Danang Tourism Super Agent**, trong đó **Planning Agent** đóng vai trò trung tâm: hiểu nhu cầu du khách → chọn địa điểm → tối ưu hóa lộ trình → tạo itinerary → lưu trữ → phục vụ UI.

**Guide Pack Agent** là tính năng nâng cao, sẽ phát triển ở phase sau.  
 Mục tiêu của tài liệu này là định nghĩa rõ **lộ trình triển khai**, **database flow**, và **cấu trúc kỹ thuật** cho **Planning Agent trước tiên**.

---

# **🎯 1\. Project Scope (v0.1 – MVP)**

### **✔ What we must implement**

* Planner API:

  * `POST /itineraries/plan`

  * `GET /itineraries/{id}`

* Planner Agent:

  * Hiểu nhu cầu user (LLM hoặc rule-based).

  * Tìm địa điểm phù hợp bằng Neo4j.

  * Sắp xếp trình tự hợp lý (TSP heuristic).

  * Tạo itinerary có nhiều stops, lưu vào Postgres.

* Database:

  * Lưu itinerary & stops.

  * Neo4j là source-of-truth cho Places.

* Docs:

  * Kiến trúc

  * Schema Postgres

  * Flow đồ thị (Graph-RAG)

### **❌ Not required in v0.1**

* Guide Pack Agent (fun facts, tips, language cards).

* Driver app.

* Affiliate engine.

* Real MCP booking.

* Vector search.

---

# **🧱 2\. Architecture Summary**

## **🔹 Core Architecture Components**

| Component | Description |
| ----- | ----- |
| **FastAPI Backend** | API gateway \+ service layer |
| **Planner Agent** | Logic tạo itinerary (LLM \+ Neo4j \+ TSP) |
| **Neo4j** | Graph database chứa Place \+ NEAR relationships |
| **Postgres** | Chứa itinerary, stops, user, booking… |
| **LLM Providers** | OpenAI / Anthropic / Gemini |
| **Shared Layer** | DB session, Neo4j client, repositories, graph services |

---

# **🗂 3\. Development Phases**

---

# **PHASE 0 – Project Bootstrap**

### **🎯 Goal**

Có hệ thống FastAPI \+ Postgres \+ Neo4j chạy ổn định.  
 Chưa cần logic AI.

### **📌 Tasks**

* Setup repo structure.

* Configure FastAPI app.

* Implement config (`Settings`).

* Setup Postgres:

  * SQLAlchemy models

  * Alembic migrations

* Setup Neo4j Client.

* Document:

  * `ARCHITECTURE.md`

  * `DATABASE_SCHEMA.md`

  * `plan.docs`

### **✅ Acceptance Criteria**

* Chạy được: `uvicorn app.main:app --reload`

* Chạy được Alembic migration.

* Test được 1 query tới Neo4j.

---

# **PHASE 1 – Planner API Skeleton (No AI, No Graph Yet)**

### **🎯 Goal**

API hoạt động end-to-end với dữ liệu dummy.

### **📌 Tasks**

#### **1\. Planner API**

* `POST /api/v1/planner/itineraries/plan`

* `GET /api/v1/planner/itineraries/{id}`

#### **2\. Schemas**

* `ItineraryPlanRequest`

* `ItineraryPlanResponse`

* `ItineraryStopResponse`

#### **3\. Service Flow**

`Router → ItineraryService → PlannerAgent (dummy) → Repository → Postgres`

#### **4\. Test**

* Unit tests cho API.

### **✅ Acceptance Criteria**

* Gửi request tạo itinerary → lưu vào DB → lấy lại đúng.

---

# **PHASE 2 – Neo4j Integration (Real Place Data)**

### **🎯 Goal**

Planner Agent lấy dữ liệu thật từ Graph DB.

### **📌 Tasks**

#### **1\. place\_graph\_service**

* Tìm places theo:

  * category

  * specialties

  * rating

  * NEAR relationships

* Query mẫu Neo4j:

`MATCH (p:Place)`  
`WHERE p.category CONTAINS $category`  
`RETURN p`  
`ORDER BY p.rating DESC`  
`LIMIT 10`

#### **2\. PlannerAgent v0.2**

* Xuất place list từ Neo4j.

* Chọn top N phù hợp với request.

* Trả về danh sách stops.

#### **3\. Repository**

* Lưu itinerary \+ stops vào PostgreSQL (place\_id trỏ sang Neo4j).

### **✅ Acceptance Criteria**

* Itinerary của user chứa địa điểm thật của Đà Nẵng từ Neo4j.

---

# **PHASE 3 – Route Optimization (TSP)**

---

# **❓ What is TSP?**

**TSP \= Traveling Salesman Problem**  
 → Bài toán sắp xếp thứ tự ghé thăm sao cho **đi ít nhất**.

**Trong dự án:**  
 Chúng ta đưa vào TSP list các địa điểm đã chọn → nhận về thứ tự tối ưu.

### **Heuristic sử dụng:**

* **Nearest Neighbor**  
   → Đủ nhanh \+ chất lượng tốt cho hành trình du lịch.

---

### **📌 Tasks**

#### **1\. Implement `tsp_solver.py`**

* Input: list toạ độ

* Output: thứ tự ghé tối ưu

#### **2\. Integrate vào PlannerAgent**

Flow:

`Neo4j → Places → TSP solver → Ordered Stops → DB`

### **✅ Acceptance Criteria**

* Hành trình hợp lý hơn (địa điểm gần nhau nằm liên tiếp).

---

# **PHASE 4 – LLM Integration & Graph-RAG Lite**

### **🎯 Goal**

Planner thực sự “thông minh” – hiểu intent và mô tả đẹp.

### **📌 Tasks**

#### **1\. LLM Intent Parser**

* Input: "beachfront seafood near My Khe"

* Output JSON:

`{`  
  `"categories": ["restaurant"],`  
  `"specialty": ["seafood"],`  
  `"near": "My Khe",`  
  `"min_rating": 4.0`  
`}`

#### **2\. Description generator**

* Tạo mô tả ngắn cho mỗi stop.

#### **3\. Graph-RAG Pipeline**

`LLM intent → Neo4j find candidates → TSP → LLM description`

### **✅ Acceptance Criteria**

* Planner hiểu ý người dùng.

* Trả về itineraries đẹp và hợp lý.

---

# **PHASE 5 – MCP Action Hooks (Optional for MVP)**

### **🎯 Goal**

Chuẩn bị để sau này có thể “Book Grab”.

### **📌 Tasks**

* Tạo `grab_transport_tool` (mock).

* Thêm `suggested_action` vào response.

### **Example:**

`{`  
  `"action": {`  
    `"type": "book_grab",`  
    `"estimate_price": "45,000₫"`  
  `}`  
`}`

### **✅ Acceptance Criteria**

* Client render được nút “Book Ride (mock)”.

---

# **PHASE 6 – Guide Pack Agent (Future Work)**

Chỉ tạo skeleton:

* Placeholder router

* Placeholder service

* Placeholder agent

Mục tiêu phase sau:

* Fun facts

* Local tips

* Language cards

* Driver-side UI

