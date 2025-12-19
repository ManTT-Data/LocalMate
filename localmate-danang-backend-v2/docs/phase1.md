# ĐỀ XUẤT GIẢI PHÁP: HỆ THỐNG MULTI-MODAL CONTEXTUAL AGENT (MMCA)

## 1. Tổng quan (Executive Summary)
Dự án nhằm mục tiêu xây dựng một **Intelligent Agent (Tác nhân thông minh)** có khả năng xử lý đa phương thức (văn bản, hình ảnh) và dữ liệu không gian (địa điểm).

Giải pháp sử dụng kiến trúc **Model Context Protocol (MCP)** để tiêu chuẩn hóa kết nối giữa Agent và các công cụ dữ liệu. Hệ thống kết hợp sức mạnh của **Vector Database (Supabase/pgvector)** cho việc tìm kiếm ngữ nghĩa/hình ảnh và **Graph Database (Neo4j)** cho việc truy vấn các mối quan hệ địa lý phức tạp.

## 2. Kiến trúc Hệ thống (Architecture)



Hệ thống hoạt động theo mô hình **Agent-Centric Orchestration**, trong đó Agent chính đóng vai trò là nhạc trưởng, phân tích intent (ý định) của người dùng để gọi đúng công cụ (Tool) thông qua giao thức MCP.

### Các thành phần chính (Tech Stack):
1.  **Orchestrator (Agent):** LLM (Large Language Model) có khả năng Function Calling.
2.  **MCP Server:** Middleware chứa logic của 3 tools.
3.  **Vector Store:** **Supabase** với extension **pgvector**.
4.  **Knowledge Graph:** **Neo4j** (hỗ trợ Spatial & Graph algorithms).

---

## 3. Chi tiết các Công cụ MCP (MCP Tools Definition)

Agent sẽ được kết nối với một MCP Server expose ra 3 tools chính sau đây:

### Tool 1: `retrieve_context_text` (RAG Text)
* **Mục đích:** Tìm kiếm thông tin chi tiết, mô tả, đánh giá hoặc menu từ kho dữ liệu văn bản.
* **Công nghệ:** **Supabase + pgvector**.
* **Cơ chế:**
    1.  Input query được chuyển đổi thành vector (embedding).
    2.  Thực hiện Similarity Search (Cosine Similarity) trên bảng `text_embeddings` trong Supabase.
    3.  Trả về các đoạn text (chunks) có độ tương đồng cao nhất.
* **Use-case:** "Tìm các quán có món Phở được review là nước dùng đậm đà."

### Tool 2: `retrieve_similar_visuals` (RAG Image)
* **Mục đích:** Tìm kiếm các địa điểm hoặc vật thể có đặc điểm hình ảnh tương đồng với ảnh đầu vào (Vibe search/Visual search).
* **Công nghệ:** **Supabase + pgvector** (Lưu trữ Image Embeddings - ví dụ dùng model CLIP).
* **Cơ chế:**
    1.  Ảnh input được đưa qua model embedding để lấy vector.
    2.  Truy vấn pgvector để tìm các ảnh đã lưu trữ có vector gần nhất.
    3.  Map từ ID ảnh sang thông tin thực thể (ví dụ: tìm quán cafe có phong cách decor giống ảnh này).
* **Use-case:** "Tìm chỗ nào có không gian giống trong bức ảnh này."

### Tool 3: `find_nearby_places` (Graph Spatial)
* **Mục đích:** Tìm kiếm địa điểm dựa trên vị trí địa lý và loại hình dịch vụ (POIs).
* **Công nghệ:** **Neo4j** (Spatial capabilities & Relationship traversal).
* **Cơ chế:**
    1.  Sử dụng Point data type trong Neo4j để lưu tọa độ.
    2.  Query Cypher để tìm các node `Place` có quan hệ `NEAR` hoặc tính khoảng cách Euclidean/Haversine từ điểm input.
    3.  Filter theo Label/Property (ví dụ: `Type: 'Cafe'`, `Type: 'Restaurant'`).
* **Use-case:** "Tìm quán cafe gần khách sạn Hilton nhất."

---

## 4. Luồng xử lý của Agent (Agent Prompting & Workflow)

Agent sẽ được cấu hình với **System Prompt** đặc thù để có khả năng "ReAct" (Reasoning + Acting):

> **System Prompt Strategy:**
> *"Bạn là một trợ lý du lịch thông minh. Bạn có quyền truy cập vào 3 công cụ qua MCP.
> - Khi người dùng hỏi về vị trí, khoảng cách, hoặc 'gần đây', hãy ưu tiên dùng `find_nearby_places`.
> - Khi người dùng đưa ra một bức ảnh hoặc mô tả về màu sắc, phong cách hình ảnh, hãy dùng `retrieve_similar_visuals`.
> - Khi người dùng hỏi chi tiết về nội dung, menu, đánh giá, hãy dùng `retrieve_context_text`.
> Lưu ý: Bạn có thể cần gọi nhiều tools tuần tự hoặc song song để tổng hợp câu trả lời cuối cùng."*

### Kịch bản ví dụ (User Journey):
**User Input:** *"Tìm cho tôi quán cafe nào gần khách sạn Rex, có không gian xanh mát giống như bức ảnh tôi gửi này và xem menu có bán Bạc Xỉu không?"*

**Agent Execution Plan:**
1.  **Step 1 (Graph):** Gọi `find_nearby_places(location="Rex Hotel", type="Cafe", radius=500m)`.
    * *Result:* List [Cafe A, Cafe B, Cafe C].
2.  **Step 2 (RAG Image):** Với danh sách trên, gọi `retrieve_similar_visuals(image=input_img, filter_ids=[A, B, C])`.
    * *Result:* Cafe B có điểm tương đồng cao nhất (về không gian xanh).
3.  **Step 3 (RAG Text):** Gọi `retrieve_context_text(query="menu Bạc Xỉu", entity_id="Cafe B")`.
    * *Result:* Tìm thấy text "Cafe B nổi tiếng với món Bạc Xỉu cốt dừa".
4.  **Final Response:** "Tôi tìm thấy **Cafe B** cách khách sạn Rex 200m. Quán có không gian vườn xanh rất giống ảnh bạn gửi và trong menu có món Bạc Xỉu được đánh giá cao."

---

## 5. Tại sao chọn Tech Stack này? (Justification)

| Công nghệ | Vai trò | Tại sao chọn? |
| :--- | :--- | :--- |
| **MCP (Model Context Protocol)** | Giao tiếp | Chuẩn hóa việc kết nối LLM với các nguồn dữ liệu rời rạc, dễ dàng mở rộng thêm tool sau này mà không cần sửa code Agent quá nhiều. |
| **Neo4j** | Graph DB | Xử lý truy vấn không gian (Spatial) và các mối quan hệ (ví dụ: "quán cafe gần rạp phim") tốt hơn và trực quan hơn nhiều so với SQL truyền thống. |
| **Supabase + pgvector** | Vector DB | Giải pháp Open-source mạnh mẽ, tích hợp sẵn PostgreSQL, chi phí thấp và hiệu năng cao cho việc lưu trữ embeddings văn bản và hình ảnh. |
