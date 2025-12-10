# PR #1 Review Comments Report

> **Pull Request**: [feat: Establish initial backend architecture for LocalMate Danang](https://github.com/ManTT-Data/LocalMate/pull/1)  
> **Reviewer**: ManTT-Data (Owner)  
> **Date Extracted**: 2025-12-10  
> **Status**: ✅ ALL COMMENTS RESOLVED

---

## 📋 Summary

| # | File | Action Required | Status |
|---|------|-----------------|--------|
| 1 | `app/core/security.py` | Bỏ/tắt JWT verification | ✅ Done |
| 2-3 | `app/guide_app/agents/guide_agent.py` | Prompt → constants | ✅ Done |
| 4 | `app/guide_app/agents/guide_agent.py` | Bỏ `generate_language_card` | ✅ Done |
| 5 | `app/guide_app/agents/guide_agent.py` | Thêm thông tin địa điểm từ DB | ✅ Done |
| 6 | `app/guide_app/agents/guide_agent.py` | Sửa input cho `generate_guide_content` | ✅ Done |
| 7 | `app/guide_app/api/router.py` | Giữ lại 1 route content | ✅ Done |
| 8 | `app/planner_app/agents/planner_agent.py` | Bỏ phần 2 và 5 | ✅ Done |
| 9 | `app/planner_app/api/mcp_router.py` | Bỏ route `/ride/estimate` | ✅ Done |
| 10 | `app/planner_app/schemas/itinerary_schemas.py` | Set budget default = "medium" | ✅ Done |
| 11 | `app/shared/constants/prompts/planner_prompts.py` | Kiểm tra `INTENT_PARSER_PROMPT` | ✅ Removed |
| 12 | `app/shared/constants/prompts/planner_prompts.py` | Dùng prompts từ constant | ✅ Done |
| 13 | `app/shared/graph/place_graph_service.py` | Giữ mỗi hàm `find_nearby_places` | ✅ Done |
| 14 | `app/shared/graph/rag_pipeline.py` | Định nghĩa rõ search flow | ✅ Done |
| 15 | `app/shared/integrations/mcp/grab_transport_tool.py` | Bỏ phần không cần | ✅ Done |
| 16 | `app/shared/integrations/mcp/grab_transport_tool.py` | Thêm booking support | ✅ Done |
| 17 | `TEST_REPORT.md` | Sửa test còn lại | ✅ Done |

---

## ✅ Changes Made

### 1. `app/core/security.py` - JWT Disabled for Demo
- Added demo mode that returns demo user when `APP_DEBUG=true`
- No authentication required for testing

### 2-6. `app/guide_app/` - Complete Refactor
- Created `guide_prompts.py` in constants
- Removed `generate_language_card` function
- Added `get_place_info()` to fetch from Neo4j
- Single `generate_guide_content(place_id, place_name)` function
- Router reduced to single `/content` endpoint

### 7. `app/guide_app/api/router.py` - Single Route
- Removed `/fun-fact`, `/tips`, `/language-card`
- Only `/content` endpoint remains

### 8. `app/planner_app/agents/planner_agent.py` - Simplified Flow
- Removed flow steps 2 and 5
- Uses prompts from constants
- Flow: Semantic Search → TSP → LLM title

### 9. `app/planner_app/api/mcp_router.py` - Removed `/ride/estimate`
- Only `/tools`, `/execute`, `/itineraries/{id}/actions` remain

### 10. `itinerary_schemas.py` - Budget Default
- Changed `budget` default from `None` to `"medium"`

### 11-12. `planner_prompts.py` - Cleaned Up
- Removed unused `INTENT_PARSER_PROMPT`
- All prompts now used correctly from constants

### 13. `place_graph_service.py` - Simplified
- Only `find_nearby_places()` function kept
- Removed `find_places_by_category`, `find_places_by_interests`

### 14. `rag_pipeline.py` - Clear Search Flow
- `search_by_preferences()` - Semantic Search for user interests
- `optimize_with_graph()` - Neo4j for nearby places
- `search()` - Combined flow

### 15-16. `grab_transport_tool.py` - Booking Support
- Added `book_ride()` function
- Added `action` parameter: `"book"` or `"estimate"`
- Returns booking_id, deep_link, etc.

### 17. Tests Updated
- All tests updated for new API
- **24/28 tests passing** (4 require DB access)

---

## 📊 Test Results

```
=================== 24 passed, 4 skipped ===================

✅ test_core.py: 6/6 passed
✅ test_services.py: 16/16 passed  
⚠️ test_guide_api.py: 0/2 (require DB)
⚠️ test_planner_api.py: 2/4 (require DB)
```

---

## 📎 Reference

- **PR URL**: https://github.com/ManTT-Data/LocalMate/pull/1
- **Branch**: `feat/initial-backend-architecture`
