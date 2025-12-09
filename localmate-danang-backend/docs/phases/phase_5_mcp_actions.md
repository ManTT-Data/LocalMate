# **PHASE 5 – MCP Action Hooks (Optional for MVP)**

## 🎯 Mục tiêu
Chuẩn bị để sau này có thể "Book Grab".

---

## 📦 Deliverables

| Item | Path | Description |
|------|------|-------------|
| Base Tool | `app/shared/integrations/mcp/base_tool.py` | MCP base class |
| Grab Tool | `app/shared/integrations/mcp/grab_transport_tool.py` | Grab booking mock |
| Action Schema | `app/planner_app/schemas/action_schemas.py` | Suggested actions |

---

## 📋 Tasks Chi tiết

### Task 5.1: MCP Base Tool

**File:** `app/shared/integrations/mcp/base_tool.py`

```python
from abc import ABC, abstractmethod

class MCPBaseTool(ABC):
    @abstractmethod
    async def execute(self, params: dict) -> dict: ...
    
    @abstractmethod
    def get_tool_spec(self) -> dict: ...
```

---

### Task 5.2: Grab Transport Tool (Mock)

**File:** `app/shared/integrations/mcp/grab_transport_tool.py`

```python
class GrabTransportTool(MCPBaseTool):
    async def estimate_ride(
        from_lat: float, from_lng: float,
        to_lat: float, to_lng: float
    ) -> dict:
        # Mock response
        return {
            "provider": "grab",
            "type": "GrabCar",
            "estimate_price": "45,000₫ - 55,000₫",
            "duration_minutes": 15,
        }
```

---

### Task 5.3: Suggested Action in Response

Thêm `suggested_action` vào ItineraryPlanResponse:

```json
{
  "stops": [...],
  "suggested_actions": [
    {
      "type": "book_grab",
      "from_stop": 0,
      "to_stop": 1,
      "estimate_price": "45,000₫"
    }
  ]
}
```

---

## ✅ Acceptance Criteria

| Criteria | Test |
|----------|------|
| Grab mock hoạt động | `estimate_ride()` trả về price |
| Actions trong response | Client render được nút "Book Ride" |

---

## ⏰ Estimated Time: 1-2 hours
