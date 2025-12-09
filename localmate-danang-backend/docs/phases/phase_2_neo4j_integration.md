# **PHASE 2 – Neo4j Integration (Real Place Data)**

## 🎯 Mục tiêu
Planner Agent lấy **dữ liệu thật** từ Neo4j Graph DB.

---

## 📦 Deliverables

| Item | Path | Description |
|------|------|-------------|
| Place Graph Service | `app/shared/graph/place_graph_service.py` | Query Neo4j places |
| Geo Utils | `app/shared/utils/geo_utils.py` | Distance calculation |
| Updated PlannerAgent | `app/planner_app/agents/planner_agent.py` | Sử dụng PlaceGraphService |

---

## 📋 Tasks Chi tiết

### Task 2.1: Geo Utilities

**File:** `app/shared/utils/geo_utils.py`

- `haversine_distance(point1, point2)`: Tính khoảng cách km giữa 2 điểm
- `bounding_box(lat, lng, radius_km)`: Tính bounding box

---

### Task 2.2: Place Graph Service

**File:** `app/shared/graph/place_graph_service.py`

```python
class PlaceGraphService:
    async def find_places_by_category(category, limit, min_rating)
    async def find_places_by_interests(interests, limit, min_rating)
    async def find_nearby_places(lat, lng, max_distance_km, category)
    async def find_restaurant_and_cafe_for_evening(interests, max_distance_km)
```

**Key Neo4j Queries:**

```cypher
# Find by category
MATCH (p:Place) WHERE p.category CONTAINS $category
RETURN p ORDER BY p.rating DESC LIMIT $limit

# Find nearby
MATCH (p:Place)
WITH p, point.distance(
    point({latitude: p.lat, longitude: p.lng}),
    point({latitude: $lat, longitude: $lng})
) / 1000 as distance_km
WHERE distance_km <= $max_distance
RETURN p ORDER BY distance_km
```

---

### Task 2.3: Update Planner Agent

**Flow:**
1. Parse interests từ request
2. Query Neo4j để lấy places phù hợp
3. Phân bổ places theo ngày
4. Trả về PlannerItineraryResult

---

## ✅ Acceptance Criteria

| Criteria | Test |
|----------|------|
| Query Neo4j hoạt động | `find_places_by_category("restaurant")` trả về data |
| Nearby search hoạt động | Query với lat/lng → places gần đó |
| Itinerary chứa real places | POST /plan → stops có place_id thật |

---

## ⏰ Estimated Time: 2-3 hours
