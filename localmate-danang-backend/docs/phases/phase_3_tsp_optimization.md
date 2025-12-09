# **PHASE 3 – Route Optimization (TSP)**

## 🎯 Mục tiêu
Sắp xếp thứ tự ghé thăm các địa điểm sao cho **đi ít nhất**.

---

## ❓ What is TSP?

**TSP = Traveling Salesman Problem**  
→ Bài toán sắp xếp thứ tự ghé thăm sao cho tổng quãng đường ngắn nhất.

**Heuristic sử dụng:** Nearest Neighbor  
→ Đủ nhanh + chất lượng tốt cho hành trình du lịch.

---

## 📦 Deliverables

| Item | Path | Description |
|------|------|-------------|
| TSP Solver | `app/shared/graph/tsp_solver.py` | Nearest Neighbor algorithm |
| Updated PlannerAgent | `app/planner_app/agents/planner_agent.py` | Integrate TSP |

---

## 📋 Tasks Chi tiết

### Task 3.1: TSP Solver

**File:** `app/shared/graph/tsp_solver.py`

```python
from app.shared.utils.geo_utils import haversine_distance

async def nearest_neighbor_tsp(
    points: list[tuple[float, float]],
    start_index: int = 0,
) -> list[int]:
    """
    Nearest Neighbor TSP heuristic.
    
    Args:
        points: List of (lat, lng) tuples
        start_index: Index to start from
    
    Returns:
        List of indices representing visiting order
    """
    n = len(points)
    if n <= 2:
        return list(range(n))
    
    visited = [False] * n
    order = [start_index]
    visited[start_index] = True
    current = start_index
    
    for _ in range(n - 1):
        nearest = None
        min_dist = float('inf')
        
        for j in range(n):
            if not visited[j]:
                dist = haversine_distance(points[current], points[j])
                if dist < min_dist:
                    min_dist = dist
                    nearest = j
        
        if nearest is not None:
            visited[nearest] = True
            order.append(nearest)
            current = nearest
    
    return order
```

---

### Task 3.2: Integrate vào PlannerAgent

**Flow:**
```
Neo4j → Places → TSP solver → Ordered Stops → DB
```

**Update PlannerAgent:**
1. Sau khi lấy places từ Neo4j
2. Extract coordinates: `[(lat, lng), ...]`
3. Gọi `nearest_neighbor_tsp(coordinates)`
4. Reorder stops theo kết quả TSP

---

## ✅ Acceptance Criteria

| Criteria | Test |
|----------|------|
| TSP trả về order hợp lệ | Input 5 points → output [0,2,4,1,3] |
| Hành trình hợp lý hơn | Địa điểm gần nhau nằm liên tiếp |
| Tổng distance giảm | So sánh với random order |

---

## ⏰ Estimated Time: 1-2 hours
