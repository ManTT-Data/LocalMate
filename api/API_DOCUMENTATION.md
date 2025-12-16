# 🏖️ Da Nang Tourism RAG API Documentation

API tìm kiếm và gợi ý địa điểm du lịch Đà Nẵng sử dụng AI.

## Overview

API kết hợp 2 nguồn dữ liệu:
- **Vector Search (Supabase)**: Tìm kiếm ngữ nghĩa bằng AI embeddings
- **Graph Database (Neo4j)**: Quan hệ không gian, địa điểm lân cận, categories

## Base URL

```
http://localhost:8000
```


---

## 📚 API Endpoints

### 1. Search Endpoints

#### 1.1 Semantic Search (POST)

```http
POST /search
Content-Type: application/json
```

**Request Body:**
```json
{
  "query": "quán cafe view đẹp",
  "max_results": 10,
  "rating_min": 4.0
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | string | ✅ | Câu query tự nhiên (VN/EN) |
| `max_results` | int | ❌ | Số kết quả tối đa (1-50, default: 10) |
| `rating_min` | float | ❌ | Rating tối thiểu (0-5) |

**Response:**
```json
{
  "query": "quán cafe view đẹp",
  "results": [
    {
      "place_id": "43-factory-coffee",
      "name": "43 Factory Coffee",
      "category": "Coffee shop",
      "rating": 4.7,
      "score": 0.8924,
      "description": "Quán cafe với view biển tuyệt đẹp...",
      "llm_summary": "Không gian chill, view biển Mỹ Khê...",
      "source_types": ["llm_enhanced", "ambiance"]
    }
  ],
  "total": 10
}
```

**Example - curl:**
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "quán cafe view đẹp", "max_results": 5}'
```

**Example - Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/search",
    json={"query": "phở ngon giá rẻ", "max_results": 5}
)
results = response.json()["results"]
```

---

#### 1.2 Simple Search (GET)

```http
GET /search?q={query}&limit={limit}&rating_min={rating}
```

**Query Parameters:**
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `q` | string | ✅ | Từ khóa tìm kiếm |
| `limit` | int | ❌ | Số kết quả (default: 10) |
| `rating_min` | float | ❌ | Rating tối thiểu |

**Example:**
```bash
curl "http://localhost:8000/search?q=cafe+view+đẹp&limit=5"
```

---

#### 1.3 Category Search

```http
GET /search/category/{category}?context={context}&limit={limit}
```

**Path Parameters:**
| Param | Values |
|-------|--------|
| `category` | `cafe`, `pho`, `banh_mi`, `seafood`, `restaurant`, `bar`, `hotel` |

**Query Parameters:**
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `context` | string | ❌ | Context bổ sung (vd: "view đẹp") |
| `limit` | int | ❌ | Số kết quả (default: 10) |

**Example:**
```bash
curl "http://localhost:8000/search/category/cafe?context=view%20đẹp&limit=5"
```

---

#### 1.4 Location Search

```http
POST /search/location
Content-Type: application/json
```

**Request Body:**
```json
{
  "lat": 16.048,
  "lng": 108.247,
  "radius_km": 2.0,
  "limit": 10
}
```

**Response:**
```json
{
  "location": {"lat": 16.048, "lng": 108.247},
  "radius_km": 2.0,
  "results": [
    {
      "place_id": "beach-bar",
      "name": "Beach Bar",
      "category": "Bar",
      "rating": 4.5,
      "distance_km": 0.3
    }
  ],
  "total": 10
}
```

---

#### 1.5 Image Search

```http
POST /search/image
Content-Type: multipart/form-data
```

**Form Data:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `image` | file | ✅ | Image file (JPG, PNG, WebP, max 10MB) |

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `max_results` | int | `10` | Số kết quả tối đa |
| `scene_filter` | string | `null` | Filter: `food`, `interior`, `exterior`, `view` |

**Response:**
```json
{
  "results": [
    {
      "place_id": "43-factory-coffee",
      "name": "43 Factory Coffee",
      "category": "Coffee shop",
      "rating": 4.7,
      "similarity": 0.8234,
      "matched_images": 5,
      "scene_type": "interior"
    }
  ],
  "total": 10,
  "scene_filter": null
}
```

**Example - curl:**
```bash
curl -X POST "http://localhost:8000/search/image?max_results=5" \
  -F "image=@my_photo.jpg"
```

**Example - Python:**
```python
import requests

with open("my_photo.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/search/image",
        files={"image": f},
        params={"max_results": 5, "scene_filter": "food"}
    )
results = response.json()["results"]
```

---

### 2. Place Details Endpoints

#### 2.1 Get Place Details

```http
GET /places/{place_id}?include_nearby=true&include_related=true&nearby_limit=5
```

**Path Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `place_id` | string | ID của địa điểm (lấy từ search) |

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `include_nearby` | bool | `true` | Bao gồm địa điểm lân cận |
| `include_related` | bool | `true` | Bao gồm địa điểm cùng category |
| `nearby_limit` | int | `5` | Số địa điểm lân cận tối đa |

**Response:**
```json
{
  "place_id": "43-factory-coffee",
  "name": "43 Factory Coffee",
  "category": "Coffee shop",
  "rating": 4.7,
  "address": "123 Võ Nguyên Giáp, Đà Nẵng",
  "phone": "0236 123 456",
  "website": "https://43factory.com",
  "google_maps_url": "https://maps.google.com/...",
  "description": "Quán cafe view biển...",
  "specialty": "Cà phê đặc sản, bánh ngọt",
  "price_range": "40,000 - 80,000 VND",
  "coordinates": {"lat": 16.048, "lng": 108.247},
  "photos_count": 50,
  "reviews_count": 120,
  "photos": ["photo1.jpg", "photo2.jpg"],
  "reviews": [
    {"text": "Quán rất đẹp...", "rating": 5, "reviewer": "Nguyen Van A"}
  ],
  "nearby_places": [
    {"place_id": "beach-bar", "name": "Beach Bar", "category": "Bar", "rating": 4.5, "distance_km": 0.3}
  ],
  "same_category": [
    {"place_id": "coffee-house", "name": "Coffee House", "rating": 4.3}
  ]
}
```

**Example:**
```bash
curl "http://localhost:8000/places/43-factory-coffee"
```

---

#### 2.2 Get Nearby Places

```http
GET /places/{place_id}/nearby?limit=5&max_distance=2.0
```

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `limit` | int | `5` | Số kết quả tối đa |
| `max_distance` | float | `2.0` | Khoảng cách tối đa (km) |

**Response:**
```json
{
  "place_id": "43-factory-coffee",
  "nearby_places": [
    {"place_id": "beach-bar", "name": "Beach Bar", "category": "Bar", "rating": 4.5, "distance_km": 0.3}
  ],
  "total": 5
}
```

---

### 3. System Endpoints

#### 3.1 API Info

```http
GET /
```

Trả về thông tin API và danh sách endpoints.

---

#### 3.2 Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "da-nang-rag-api",
  "version": "2.0.0",
  "components": {
    "rag_service": "connected",
    "neo4j_service": "connected"
  }
}
```

---

## 🔄 Recommended Flow

```
┌─────────────────────────────────────────────────────────────┐
│  1. User nhập query                                         │
│     "quán cafe view đẹp gần biển"                          │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  2. POST /search                                            │
│     → Trả về top 10 results với place_id                   │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  3. Hiển thị danh sách kết quả cho user                    │
│     (name, category, rating, score, description)           │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  4. User click vào một địa điểm                            │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  5. GET /places/{place_id}                                  │
│     → Trả về full details + nearby + related               │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  6. Hiển thị trang chi tiết địa điểm                       │
│     - Photos, reviews, maps                                 │
│     - "Nearby" section với các địa điểm lân cận            │
│     - "Similar places" section                              │
└─────────────────────────────────────────────────────────────┘
```

---

## ⚠️ Error Responses

### 400 Bad Request
```json
{"detail": "Invalid query parameters"}
```

### 404 Not Found
```json
{"detail": "Place not found: invalid-id"}
```

### 500 Internal Server Error
```json
{"detail": "Neo4j error: Connection failed"}
```

---

## 🛠️ Running the API

### Prerequisites

```bash
# Install dependencies
pip install fastapi uvicorn psycopg2-binary neo4j python-dotenv google-generativeai

# Set environment variables in .env
NEO4J_URI=neo4j+s://xxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password
```

### Start Server

```bash
cd api
python main.py
```

API will be available at:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📊 Data Sources

| Source | Data | Usage |
|--------|------|-------|
| **Supabase** | Text embeddings, metadata | Vector search |
| **Neo4j** | Full place data, photos, reviews, spatial relationships | Details & enrichment |

---

## 📝 Notes

- Tất cả endpoint đều support Vietnamese và English queries
- `place_id` từ search result có thể dùng trực tiếp cho `/places/{place_id}`
- `nearby_places` sử dụng precomputed NEAR relationships trong Neo4j (nhanh)
- `search/location` tính distance realtime bằng point.distance() của Neo4j
