# LocalMate API Documentation

> **Base URL:** `https://cuong2004-localmate.hf.space/api/v1`  
> **Swagger UI:** `/docs` | **ReDoc:** `/redoc`  
> **Version:** 0.3.0

---

## 📋 Table of Contents

1. [Chat API](#chat-api)
2. [User Profile API](#user-profile-api)
3. [Itineraries API](#itineraries-api)
4. [Trip Planner API](#trip-planner-api)
5. [Utility Endpoints](#utility-endpoints)
6. [Models](#models)

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
  "response": "Mình gợi ý 3 quán cafe rất đẹp gần Mỹ Khê...",
  "status": "success",
  "provider": "MegaLLM",
  "model": "deepseek-ai/deepseek-v3.1-terminus",
  "user_id": "user_123",
  "session_id": "default",
  "places": [
    {
      "place_id": "cafe_001",
      "name": "Cabanon Palace",
      "category": "restaurant",
      "lat": 16.06,
      "lng": 108.24,
      "rating": 4.8,
      "address": "123 Võ Nguyên Giáp"
    },
    {
      "place_id": "cafe_002",
      "name": "Be Man Restaurant",
      "category": "restaurant",
      "lat": 16.07,
      "lng": 108.25,
      "rating": 4.5,
      "address": "456 Phạm Văn Đồng"
    }
  ],
  "tools_used": ["find_nearby_places"],
  "duration_ms": 5748.23
}
```

> **Note:** `places` array contains LLM-selected places with full details. FE can render these as cards separately from text response.

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

### GET `/chat/history/{user_id}`

Get chat session metadata (list of sessions, counts).

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

### GET `/chat/messages/{user_id}`

Get actual chat messages from a session.

**Query Params:** `?session_id=default`

**Response:**
```json
{
  "user_id": "user_123",
  "session_id": "default",
  "messages": [
    {
      "role": "user",
      "content": "Tìm quán cafe gần Mỹ Khê",
      "timestamp": "2025-01-01T10:00:00"
    },
    {
      "role": "assistant",
      "content": "Dựa trên yêu cầu của bạn...",
      "timestamp": "2025-01-01T10:00:05"
    }
  ],
  "count": 2
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

## Upload API

Base path: `/upload`

### POST `/upload/image`

Upload image to Supabase Storage and get public URL.

> Use this to get an image URL for the `/chat` endpoint's `image_url` parameter.

**Request:** `multipart/form-data`
- `file`: Image file (required)
- `user_id`: string (optional, for organizing uploads)

**Supported formats:** JPEG, PNG, WebP, GIF  
**Max size:** 10MB

**Response:**
```json
{
  "url": "https://xxx.supabase.co/storage/v1/object/public/image/user123/20250101_120000_abc123.jpg",
  "path": "user123/20250101_120000_abc123.jpg",
  "size": 245678,
  "content_type": "image/jpeg"
}
```

**Usage Flow:**
```
1. POST /upload/image → get URL
2. POST /chat { image_url: URL } → visual search
```

---

## User Profile API

Base path: `/users`

### GET `/users/me`

Get current user's profile.

**Query:** `?user_id=uuid-here`

**Response:**
```json
{
  "profile": {
    "id": "uuid-here",
    "full_name": "Nguyen Van A",
    "phone": "0901234567",
    "role": "tourist",
    "locale": "vi_VN",
    "avatar_url": "https://...",
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
  },
  "message": "Profile retrieved"
}
```

---

### PUT `/users/me`

Update current user's profile.

**Query:** `?user_id=uuid-here`

**Request:**
```json
{
  "full_name": "Nguyen Van B",
  "phone": "0909876543",
  "locale": "en_US",
  "avatar_url": "https://..."
}
```

---

### GET `/users/{user_id}`

Get user profile by ID (admin only).

---

## Itineraries API

Base path: `/itineraries`

> Multi-day trip planning with persistent storage (Supabase)

### POST `/itineraries`

Create new itinerary.

**Query:** `?user_id=uuid-here`

**Request:**
```json
{
  "title": "Da Nang 3 Days Trip",
  "start_date": "2025-02-01",
  "end_date": "2025-02-03",
  "total_days": 3,
  "total_budget": 5000000,
  "currency": "VND"
}
```

**Response:**
```json
{
  "itinerary": {
    "id": "itinerary-uuid",
    "user_id": "user-uuid",
    "title": "Da Nang 3 Days Trip",
    "start_date": "2025-02-01",
    "end_date": "2025-02-03",
    "total_days": 3,
    "total_budget": 5000000,
    "currency": "VND",
    "stops": [],
    "created_at": "...",
    "updated_at": "..."
  },
  "message": "Itinerary created"
}
```

---

### GET `/itineraries`

List user's itineraries.

**Query:** `?user_id=uuid-here`

**Response:**
```json
[
  {
    "id": "itinerary-uuid",
    "title": "Da Nang 3 Days Trip",
    "start_date": "2025-02-01",
    "end_date": "2025-02-03",
    "total_days": 3,
    "stop_count": 8,
    "created_at": "..."
  }
]
```

---

### GET `/itineraries/{itinerary_id}`

Get itinerary with all stops.

**Query:** `?user_id=uuid-here`

---

### PUT `/itineraries/{itinerary_id}`

Update itinerary details.

**Request:**
```json
{
  "title": "Updated Title",
  "total_budget": 6000000
}
```

---

### DELETE `/itineraries/{itinerary_id}`

Delete itinerary and all stops.

---

### POST `/itineraries/{itinerary_id}/stops`

Add stop to itinerary.

**Request:**
```json
{
  "place_id": "cafe_123",
  "day_index": 1,
  "order_index": 1,
  "arrival_time": "2025-02-01T09:00:00Z",
  "stay_minutes": 60,
  "notes": "Morning coffee",
  "tags": ["cafe", "breakfast"]
}
```

---

### PUT `/itineraries/{itinerary_id}/stops/{stop_id}`

Update stop.

---

### DELETE `/itineraries/{itinerary_id}/stops/{stop_id}`

Remove stop.

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
