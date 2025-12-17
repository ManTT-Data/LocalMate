# LocalMate API Documentation

> **Base URL:** `https://cuong2004-localmate.hf.space/api/v1`  
> **Swagger UI:** `/docs` | **ReDoc:** `/redoc`

---

## 📋 Table of Contents

1. [Chat API](#chat-api)
2. [Trip Planner API](#trip-planner-api)
3. [Utility Endpoints](#utility-endpoints)
4. [Request/Response Models](#models)

---

## Chat API

### POST `/chat`

Main endpoint for interacting with the AI assistant.

**Request:**
```json
{
  "message": "Quán cafe view đẹp gần Mỹ Khê",
  "user_id": "user_123",
  "session_id": "default",
  "provider": "MegaLLM",
  "model": "deepseek-ai/deepseek-v3.1-terminus",
  "image_url": null,
  "react_mode": false,
  "max_steps": 5
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `message` | string | ✅ | User's question in Vietnamese |
| `user_id` | string | ❌ | User ID for session (default: "anonymous") |
| `session_id` | string | ❌ | Session ID (default: "default") |
| `provider` | string | ❌ | "Google" or "MegaLLM" (default: "MegaLLM") |
| `model` | string | ❌ | LLM model name |
| `image_url` | string | ❌ | Base64 image for visual search |
| `react_mode` | boolean | ❌ | Enable multi-step reasoning (default: false) |
| `max_steps` | integer | ❌ | Max reasoning steps 1-10 (default: 5) |

**Response:**
```json
{
  "response": "Dựa trên yêu cầu của bạn, tôi tìm thấy...",
  "status": "success",
  "provider": "MegaLLM",
  "model": "deepseek-ai/deepseek-v3.1-terminus",
  "user_id": "user_123",
  "session_id": "default",
  "workflow": {
    "query": "Quán cafe view đẹp gần Mỹ Khê",
    "intent_detected": "location_search",
    "tools_used": ["find_nearby_places"],
    "steps": [
      {
        "step": "Execute find_nearby_places",
        "tool": "find_nearby_places",
        "purpose": "Tìm địa điểm gần vị trí được nhắc đến",
        "results": 5
      }
    ],
    "total_duration_ms": 5748.23
  },
  "tools_used": ["find_nearby_places"],
  "duration_ms": 5748.23
}
```

---

### POST `/chat/clear`

Clear conversation history.

**Request:**
```json
{
  "user_id": "user_123",
  "session_id": "default"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Cleared session 'default' for user_123"
}
```

---

### GET `/chat/history`

Get chat history info.

**Query Params:** `?user_id=user_123`

**Response:**
```json
{
  "user_id": "user_123",
  "sessions": ["default", "trip_planning"],
  "current_session": "default",
  "message_count": 12
}
```

---

### POST `/image-search`

Search places by uploaded image.

**Request:** `multipart/form-data`  
- `image`: File (required)
- `limit`: integer (default: 10)

**Response:**
```json
{
  "results": [
    {
      "place_id": "cafe_123",
      "name": "Nhớ Một Người",
      "category": "Cafe",
      "rating": 4.9,
      "similarity": 0.85,
      "image_url": "https://..."
    }
  ],
  "total": 5
}
```

---

## Trip Planner API

Base path: `/planner`

### POST `/planner/create`

Create a new trip plan.

**Query:** `?user_id=user_123`

**Request:**
```json
{
  "name": "My Da Nang Trip"
}
```

**Response:**
```json
{
  "plan_id": "plan_abc123",
  "name": "My Da Nang Trip",
  "message": "Created plan 'My Da Nang Trip'"
}
```

---

### GET `/planner/{plan_id}`

Get a plan by ID.

**Query:** `?user_id=user_123`

**Response:**
```json
{
  "plan": {
    "plan_id": "plan_abc123",
    "name": "My Da Nang Trip",
    "items": [
      {
        "item_id": "item_1",
        "order": 0,
        "name": "FIRGUN CORNER COFFEE",
        "category": "Cafe",
        "lat": 16.06,
        "lng": 108.22,
        "rating": 4.5,
        "distance_from_prev_km": null
      }
    ],
    "total_distance_km": 0,
    "estimated_duration_min": 0
  },
  "message": "Plan retrieved"
}
```

---

### POST `/planner/{plan_id}/add`

Add a place to the plan.

**Query:** `?user_id=user_123`

**Request:**
```json
{
  "place": {
    "place_id": "cafe_123",
    "name": "FIRGUN CORNER COFFEE",
    "category": "Cafe",
    "lat": 16.06,
    "lng": 108.22,
    "rating": 4.5
  },
  "notes": "Morning coffee"
}
```

**Response:** `PlanItem` object

---

### DELETE `/planner/{plan_id}/remove/{item_id}`

Remove a place from the plan.

**Query:** `?user_id=user_123`

**Response:**
```json
{
  "status": "success",
  "message": "Removed item item_1"
}
```

---

### PUT `/planner/{plan_id}/reorder`

Reorder places manually.

**Query:** `?user_id=user_123`

**Request:**
```json
{
  "new_order": ["item_3", "item_1", "item_2"]
}
```

---

### POST `/planner/{plan_id}/optimize`

Optimize route using TSP algorithm.

**Query:** `?user_id=user_123&start_index=0`

**Response:**
```json
{
  "plan_id": "plan_abc123",
  "items": [...],
  "total_distance_km": 12.5,
  "estimated_duration_min": 45,
  "distance_saved_km": 3.2,
  "message": "Route optimized! Total: 12.5km, ~45min"
}
```

---

### DELETE `/planner/{plan_id}`

Delete a plan.

**Query:** `?user_id=user_123`

---

## Utility Endpoints

### GET `/health`

Health check. Returns `{"status": "ok"}`

### POST `/nearby`

Find nearby places (direct Neo4j query).

**Request:**
```json
{
  "lat": 16.0626442,
  "lng": 108.2462143,
  "max_distance_km": 3.0,
  "category": "cafe",
  "limit": 10
}
```

---

## Models

### Place Object
```typescript
interface Place {
  place_id: string;
  name: string;
  category?: string;
  lat?: number;
  lng?: number;
  rating?: number;
  description?: string;
}
```

### PlanItem
```typescript
interface PlanItem {
  item_id: string;
  order: number;
  name: string;
  category?: string;
  lat: number;
  lng: number;
  rating?: number;
  notes?: string;
  distance_from_prev_km?: number;
}
```

### WorkflowStep
```typescript
interface WorkflowStep {
  step: string;
  tool?: string;
  purpose: string;
  results: number;
}
```

---

## Usage Examples

### JavaScript/Fetch

```javascript
// Chat
const response = await fetch('https://cuong2004-localmate.hf.space/api/v1/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'Quán cafe view đẹp gần Mỹ Khê',
    user_id: 'my_user',
    react_mode: false
  })
});
const data = await response.json();
console.log(data.response);
```

### cURL

```bash
curl -X POST "https://cuong2004-localmate.hf.space/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Nhà hàng hải sản ngon", "user_id": "test"}'
```

---

## Error Responses

| Status | Description |
|--------|-------------|
| 400 | Bad Request - Invalid parameters |
| 404 | Not Found - Resource doesn't exist |
| 422 | Validation Error - Check request body |
| 500 | Server Error - Check logs |

```json
{
  "detail": "Plan not found"
}
```
