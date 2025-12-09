# **PHASE 4 – LLM Integration & Graph-RAG Lite**

## 🎯 Mục tiêu
Planner thực sự "thông minh" – hiểu intent và tạo mô tả đẹp.

---

## 📦 Deliverables

| Item | Path | Description |
|------|------|-------------|
| LLM Client | `app/shared/integrations/llm_client.py` | OpenAI/Anthropic wrapper |
| Planner Prompts | `app/shared/constants/prompts/planner_prompts.py` | System prompts |
| RAG Pipeline | `app/shared/graph/rag_pipeline.py` | LLM + Neo4j integration |
| Updated PlannerAgent | `app/planner_app/agents/planner_agent.py` | Use LLM |

---

## 📋 Tasks Chi tiết

### Task 4.1: LLM Client

**File:** `app/shared/integrations/llm_client.py`

```python
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

class LLMClient:
    async def chat_completion(
        messages: list[dict],
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
    ) -> str: ...
    
    async def parse_intent(user_query: str) -> dict:
        """Parse natural language to structured intent"""
        # Returns: {
        #   "categories": ["restaurant"],
        #   "specialty": ["seafood"],
        #   "near": "My Khe",
        #   "min_rating": 4.0
        # }
```

---

### Task 4.2: Intent Parser

**Input:** `"beachfront seafood near My Khe"`

**Output:**
```json
{
  "categories": ["restaurant"],
  "specialty": ["seafood"],
  "near": "My Khe",
  "min_rating": 4.0
}
```

---

### Task 4.3: Description Generator

Tạo mô tả ngắn cho mỗi stop bằng LLM:

```python
async def generate_stop_description(place: PlaceResult) -> str:
    prompt = f"Write a 1-2 sentence description for {place.name}..."
    return await llm_client.chat_completion([...])
```

---

### Task 4.4: Graph-RAG Pipeline

**Flow:**
```
User Query → LLM Intent Parse → Neo4j Find Candidates → TSP Order → LLM Description
```

---

## ✅ Acceptance Criteria

| Criteria | Test |
|----------|------|
| Intent parsing hoạt động | "seafood near beach" → correct JSON |
| LLM descriptions đẹp | Each stop có description |
| Graph-RAG flow complete | End-to-end từ query → itinerary |

---

## ⏰ Estimated Time: 3-4 hours
