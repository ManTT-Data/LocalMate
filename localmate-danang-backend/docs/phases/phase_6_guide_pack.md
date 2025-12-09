# **PHASE 6 – Guide Pack Agent (Future Work)**

## 🎯 Mục tiêu
Tạo skeleton cho Guide Pack Agent - tính năng nâng cao cho tài xế.

---

## 📦 Deliverables

| Item | Path | Description |
|------|------|-------------|
| Guide Router | `app/guide_app/api/router.py` | Placeholder router |
| Guide Schemas | `app/guide_app/schemas/guide_pack_schemas.py` | Placeholder schemas |
| Guide Agent | `app/guide_app/agents/guide_agent.py` | Placeholder agent |
| Guide Service | `app/guide_app/services/guide_pack_service.py` | Placeholder service |
| Guide Prompts | `app/shared/constants/prompts/guide_prompts.py` | Placeholder prompts |

---

## 📋 Tasks Chi tiết

### Task 6.1: Guide Pack Schemas

**File:** `app/guide_app/schemas/guide_pack_schemas.py`

```python
class GuidePackRequest(BaseModel):
    itinerary_id: uuid.UUID
    driver_id: uuid.UUID
    language: str = "vi"

class FunFact(BaseModel):
    place_id: str
    title: str
    content: str
    source: str | None = None

class LanguageCard(BaseModel):
    phrase: str
    pronunciation: str
    translation: str
    context: str

class GuidePackResponse(BaseModel):
    itinerary_id: uuid.UUID
    fun_facts: list[FunFact]
    language_cards: list[LanguageCard]
    tips: list[str]
```

---

### Task 6.2: Placeholder Router

**File:** `app/guide_app/api/router.py`

```python
router = APIRouter()

@router.post("/guide-pack/generate")
async def generate_guide_pack(request: GuidePackRequest):
    # Placeholder - return mock data
    return {"status": "not_implemented"}
```

---

### Task 6.3: Guide Agent Skeleton

**File:** `app/guide_app/agents/guide_agent.py`

```python
class GuideAgent:
    async def generate_fun_facts(places: list[str]) -> list[FunFact]:
        # TODO: Query Neo4j + LLM
        pass
    
    async def generate_language_cards(locale: str) -> list[LanguageCard]:
        # TODO: Generate Vietnamese phrases
        pass
```

---

## 🎯 Mục tiêu Phase sau

1. **Fun Facts**: Thông tin thú vị về địa điểm
2. **Local Tips**: Mẹo du lịch từ người địa phương
3. **Language Cards**: Câu nói tiếng Việt hữu ích
4. **Driver-side UI**: Giao diện cho tài xế

---

## ✅ Acceptance Criteria

| Criteria | Test |
|----------|------|
| Router hoạt động | GET /guide → không lỗi |
| Schemas defined | Import không lỗi |
| Placeholder response | Return mock data |

---

## 📂 Folder Structure

```
app/guide_app/
├─ __init__.py
├─ api/
│  ├─ __init__.py
│  ├─ router.py
│  └─ driver_guide_router.py
├─ schemas/
│  ├─ __init__.py
│  └─ guide_pack_schemas.py
├─ agents/
│  ├─ __init__.py
│  └─ guide_agent.py
├─ services/
│  ├─ __init__.py
│  └─ guide_pack_service.py
└─ tests/
   ├─ __init__.py
   └─ test_dummy.py
```

---

## ⏰ Estimated Time: 1 hour (skeleton only)
