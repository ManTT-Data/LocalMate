# LocalMate Agent Test Report

**Generated:** 2025-12-18 02:27:42

## Summary

| Metric | Single Mode | ReAct Mode |
|--------|-------------|------------|
| Total Tests | 1 | 1 |
| Success | 1 | 1 |
| Avg Duration | 12627ms | 15080ms |

---

## Detailed Results

### Test Case 2: Location-based search

**Query:** `Nhà hàng gần bãi biển Mỹ Khê`

#### Single Mode

- **Status:** ✅ Success
- **Duration:** 12627ms
- **Tools Used:** find_nearby_places

**Workflow:**
No steps recorded

**Response Preview:**
> Chào bạn! Mình tìm được một số nhà hàng ngon gần bãi biển Mỹ Khê cho bạn đây:

🏆 **Top 3 nhà hàng được đánh giá cao nhất:**

1. **Cabanon Palace** - Nhà hàng Pháp
   * ⭐️ Rating: 4.8/5
   * 📍 Cách biể...

#### ReAct Mode

- **Status:** ✅ Success
- **Duration:** 15080ms
- **Tools Used:** get_location_coordinates, find_nearby_places
- **Steps:** 0
- **Intent Detected:** N/A

**Workflow Steps:**
No steps recorded

**Response Preview:**
> Chào bạn! Mình tìm được những nhà hàng ngon và gần bãi biển Mỹ Khê nhất cho bạn đây:

🏆 **Top 3 nhà hàng được đánh giá cao nhất:**

1. **Cabanon Palace** - Nhà hàng Pháp
   * ⭐️ Rating: 4.8/5
   * 📍 C...

---

## Analysis

### Tool Usage Comparison

| Test | Single Mode Tools | ReAct Mode Tools | ReAct Steps |
|------|-------------------|------------------|-------------|
| 2 | find_nearby_places | get_location_coordinates, find_nearby_places | 0 |


### Key Observations

1. **Multi-tool queries**: ReAct mode can chain multiple tools for complex queries
2. **Single-tool queries**: Both modes perform similarly for simple queries
3. **Reasoning steps**: ReAct mode shows explicit reasoning before each tool call

