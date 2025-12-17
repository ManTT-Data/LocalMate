"""ReAct Reasoning Module - Prompts and parsing for multi-step reasoning."""

import json
import re
from dataclasses import dataclass
from typing import Any

from app.shared.logger import agent_logger


# System prompt for ReAct mode
REACT_SYSTEM_PROMPT = """Bạn là agent du lịch thông minh cho Đà Nẵng với khả năng suy luận multi-step.

**Tools có sẵn:**
1. `get_location_coordinates` - Lấy tọa độ từ tên địa điểm
   - Input: {"location_name": "Dragon Bridge"}
   - Output: {"lat": 16.06, "lng": 108.22}

2. `find_nearby_places` - Tìm địa điểm gần vị trí
   - Input: {"lat": 16.06, "lng": 108.22, "category": "cafe", "max_distance_km": 3}
   - Output: [{name, category, distance_km, rating}]

3. `retrieve_context_text` - Tìm semantic trong reviews/descriptions
   - Input: {"query": "cafe view đẹp", "limit": 5}
   - Output: [{name, category, rating, source_text}]

4. `retrieve_similar_visuals` - Tìm địa điểm có hình ảnh tương tự
   - Input: {"image_url": "..."}
   - Output: [{name, similarity, image_url}]

5. `search_social_media` - Tìm kiếm mạng xã hội và tin tức
   - Input: {"query": "review quán ăn", "freshness": "pw", "platforms": ["tiktok"]}
   - Output: [{title, url, age, platform}]

**Quy trình:**
Với mỗi bước, bạn phải:
1. **Thought**: Suy nghĩ về bước tiếp theo cần làm
2. **Action**: Chọn tool hoặc "finish" nếu đủ thông tin
3. **Action Input**: JSON parameters cho tool

**Trả lời CHÍNH XÁC theo format JSON:**
```json
{
  "thought": "Suy nghĩ của bạn...",
  "action": "tool_name hoặc finish",
  "action_input": {"param1": "value1"}
}
```

**Quan trọng:**
- Nếu cần biết vị trí → dùng get_location_coordinates trước
- Nếu tìm theo khoảng cách → dùng find_nearby_places
- Nếu tìm review/trend MXH → dùng search_social_media
- Nếu cần lọc theo đặc điểm (view, không gian, giá) → dùng retrieve_context_text
- Khi đủ thông tin → action = "finish"
"""



@dataclass
class ReasoningResult:
    """Result from LLM reasoning step."""
    
    thought: str
    action: str
    action_input: dict
    raw_response: str
    parse_error: str | None = None


def parse_reasoning_response(response: str) -> ReasoningResult:
    """
    Parse LLM response into thought/action/action_input.
    
    Handles various formats:
    - Clean JSON
    - JSON in markdown code blocks
    - Partial/malformed JSON
    """
    raw = response.strip()
    
    # Try to extract JSON from code blocks
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw, re.DOTALL)
    if json_match:
        raw = json_match.group(1)
    
    # Try to find JSON object
    json_start = raw.find('{')
    json_end = raw.rfind('}')
    if json_start != -1 and json_end != -1:
        raw = raw[json_start:json_end + 1]
    
    try:
        data = json.loads(raw)
        return ReasoningResult(
            thought=data.get("thought", ""),
            action=data.get("action", "finish"),
            action_input=data.get("action_input", {}),
            raw_response=response,
        )
    except json.JSONDecodeError as e:
        agent_logger.error(f"Failed to parse reasoning response", e)
        
        # Fallback: try to extract key fields with regex
        thought_match = re.search(r'"thought"\s*:\s*"([^"]*)"', raw)
        action_match = re.search(r'"action"\s*:\s*"([^"]*)"', raw)
        
        thought = thought_match.group(1) if thought_match else "Parse error"
        action = action_match.group(1) if action_match else "finish"
        
        return ReasoningResult(
            thought=thought,
            action=action,
            action_input={},
            raw_response=response,
            parse_error=str(e),
        )


def build_reasoning_prompt(
    query: str,
    context_summary: str,
    previous_steps: list[dict],
    image_url: str | None = None,
) -> str:
    """Build the prompt for the next reasoning step."""
    
    # Previous steps summary
    steps_text = ""
    if previous_steps:
        steps_text = "\n**Các bước đã thực hiện:**\n"
        for step in previous_steps:
            steps_text += f"- Step {step['step']}: {step['thought'][:80]}...\n"
            steps_text += f"  Action: {step['action']} → {len(step.get('observation', [])) if isinstance(step.get('observation'), list) else 'done'} kết quả\n"
    
    # Image context
    image_text = ""
    if image_url:
        image_text = "\n**Lưu ý:** User đã gửi kèm ảnh. Có thể dùng retrieve_similar_visuals nếu cần.\n"
    
    prompt = f"""**Câu hỏi của user:** {query}
{image_text}
{context_summary}
{steps_text}
**Bước tiếp theo là gì?**

Trả lời theo format JSON:
```json
{{
  "thought": "...",
  "action": "tool_name hoặc finish",
  "action_input": {{...}}
}}
```"""
    
    return prompt


def get_tool_purpose(action: str) -> str:
    """Get human-readable purpose for a tool."""
    purposes = {
        "get_location_coordinates": "Lấy tọa độ địa điểm",
        "find_nearby_places": "Tìm địa điểm gần vị trí",
        "retrieve_context_text": "Tìm theo văn bản (reviews, mô tả)",
        "retrieve_similar_visuals": "Tìm theo hình ảnh tương tự",
        "search_social_media": "Tìm kiếm mạng xã hội và tin tức",
        "finish": "Hoàn thành và tổng hợp kết quả",
    }

    return purposes.get(action, action)
