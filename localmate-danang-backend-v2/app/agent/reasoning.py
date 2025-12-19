"""ReAct Reasoning Module - Prompts and parsing for multi-step reasoning."""

import json
import re
from dataclasses import dataclass
from typing import Any

from app.shared.logger import agent_logger
from app.shared.prompts import (
    REACT_SYSTEM_PROMPT,
    TOOL_PURPOSES,
)

# Re-export for backward compatibility
__all__ = ["REACT_SYSTEM_PROMPT", "ReasoningResult", "parse_reasoning_response", "build_reasoning_prompt", "get_tool_purpose"]



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
    
    # Previous steps summary with FULL observations
    steps_text = ""
    if previous_steps:
        steps_text = "\n**Các bước đã thực hiện và KẾT QUẢ:**\n"
        for step in previous_steps:
            action = step.get('action', 'unknown')
            thought = step.get('thought', '')[:100]
            observation = step.get('observation', [])
            
            steps_text += f"\n📍 **Step {step['step']}**: {thought}...\n"
            steps_text += f"   Action: `{action}`\n"
            
            # Show detailed observation data
            if action == "get_location_coordinates" and observation:
                if isinstance(observation, dict):
                    lat = observation.get('lat', 'N/A')
                    lng = observation.get('lng', 'N/A')
                    steps_text += f"   ✅ Kết quả: lat={lat}, lng={lng}\n"
                    steps_text += f"   ⚠️ ĐÃ CÓ TỌA ĐỘ - KHÔNG CẦN GỌI LẠI get_location_coordinates\n"
            
            elif action == "find_nearby_places" and observation:
                if isinstance(observation, list) and len(observation) > 0:
                    steps_text += f"   ✅ Tìm được {len(observation)} địa điểm:\n"
                    for i, place in enumerate(observation[:5], 1):
                        if isinstance(place, dict):
                            name = place.get('name', 'Unknown')
                            dist = place.get('distance_km', 'N/A')
                            rating = place.get('rating', 'N/A')
                            steps_text += f"      {i}. {name} ({dist}km, ⭐{rating})\n"
                        else:
                            steps_text += f"      {i}. {place}\n"
                    if len(observation) > 5:
                        steps_text += f"      ... và {len(observation) - 5} địa điểm khác\n"
                    steps_text += f"   ⚠️ ĐÃ CÓ DANH SÁCH - KHÔNG CẦN GỌI LẠI find_nearby_places\n"
            
            elif action == "retrieve_context_text" and observation:
                if isinstance(observation, list) and len(observation) > 0:
                    steps_text += f"   ✅ Tìm được {len(observation)} kết quả text:\n"
                    for i, item in enumerate(observation[:3], 1):
                        if isinstance(item, dict):
                            name = item.get('name', 'Unknown')
                            steps_text += f"      {i}. {name}\n"
                        else:
                            steps_text += f"      {i}. {item}\n"
                    steps_text += f"   ⚠️ ĐÃ CÓ KẾT QUẢ TEXT - KHÔNG CẦN GỌI LẠI retrieve_context_text\n"
            
            elif observation:
                result_count = len(observation) if isinstance(observation, list) else 1
                steps_text += f"   ✅ Kết quả: {result_count} items\n"
        
        steps_text += "\n**⚠️ QUAN TRỌNG:** Nếu đã có đủ thông tin từ các bước trên → action = 'finish'\n"
    
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
    return TOOL_PURPOSES.get(action, action)
