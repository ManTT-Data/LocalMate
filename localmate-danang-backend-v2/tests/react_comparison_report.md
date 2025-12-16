# LocalMate Agent Test Report

**Generated:** 2025-12-17 05:11:43

## Summary

| Metric | Single Mode | ReAct Mode |
|--------|-------------|------------|
| Total Tests | 1 | 1 |
| Success | 1 | 1 |
| Avg Duration | 10653ms | 13297ms |

---

## Detailed Results

### Test Case 1: Simple text search - no location

**Query:** `Quán cafe view đẹp`

#### Single Mode

- **Status:** ✅ Success
- **Duration:** 10653ms
- **Tools Used:** retrieve_context_text

**Workflow:**
  - Intent Analysis
    Tool: `None` | Results: 0
  - Tool Planning
    Tool: `None` | Results: 0
  - Execute retrieve_context_text
    Tool: `retrieve_context_text` | Results: 5
  - LLM Synthesis
    Tool: `None` | Results: 0

**Response Preview:**
> Chào bạn! Dựa trên yêu cầu "quán cafe view đẹp" của bạn, mình gợi ý một số địa điểm nổi bật ở Đà Nẵng sau đây nhé:

☕ **Top 3 quán cafe view đẹp đáng thử:**

1. **Nhớ Một Người**  
   - Địa chỉ: 06 Tr...

#### ReAct Mode

- **Status:** ✅ Success
- **Duration:** 13297ms
- **Tools Used:** retrieve_context_text
- **Steps:** 3
- **Intent Detected:** react_multi_step

**Workflow Steps:**
  - Step 1: User đang tìm quán cafe có view đẹp ở Đà Nẵng. Đây...
    Tool: `retrieve_context_text` | Results: 10
  - Step 2: User đang tìm quán cafe có view đẹp ở Đà Nẵng. Tôi...
    Tool: `retrieve_context_text` | Results: 10
  - Step 3: Tôi đã có tổng cộng 10 kết quả từ hai lần gọi retr...
    Tool: `None` | Results: 0

**Response Preview:**
> Chào bạn! Dưới đây là một số quán cafe có view đẹp tại Đà Nẵng mà bạn có thể tham khảo:

☕ **Nhớ Một Người**  
- Địa chỉ: 06 Trường Thi 5, Hòa Thuận Tây, Hải Châu  
- Rating: 4.9/5 ⭐  
- Đặc điểm: Khô...

---

## Analysis

### Tool Usage Comparison

| Test | Single Mode Tools | ReAct Mode Tools | ReAct Steps |
|------|-------------------|------------------|-------------|
| 1 | retrieve_context_text | retrieve_context_text | 3 |


### Key Observations

1. **Multi-tool queries**: ReAct mode can chain multiple tools for complex queries
2. **Single-tool queries**: Both modes perform similarly for simple queries
3. **Reasoning steps**: ReAct mode shows explicit reasoning before each tool call

