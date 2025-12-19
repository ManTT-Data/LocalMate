"""
Centralized Prompts for LocalMate Agent.

This file contains all system prompts and prompt templates used across the agent.
Import prompts from this file to ensure consistency and easy maintenance.

Usage:
    from app.shared.prompts.prompts import (
        MMCA_SYSTEM_PROMPT,
        REACT_SYSTEM_PROMPT,
        build_synthesis_prompt,
        build_greeting_prompt,
        build_reasoning_prompt,
    )
"""

# =============================================================================
# TOOL DEFINITIONS
# =============================================================================

TOOL_DEFINITIONS = """
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
"""

TOOL_PURPOSES = {
    "get_location_coordinates": "Lấy tọa độ địa điểm",
    "find_nearby_places": "Tìm địa điểm gần vị trí",
    "retrieve_context_text": "Tìm theo văn bản (reviews, mô tả)",
    "retrieve_similar_visuals": "Tìm theo hình ảnh tương tự",
    "search_social_media": "Tìm kiếm mạng xã hội và tin tức",
    "finish": "Hoàn thành và tổng hợp kết quả",
}


# =============================================================================
# SYSTEM PROMPTS
# =============================================================================

MMCA_SYSTEM_PROMPT = """Bạn là trợ lý du lịch thông minh cho Đà Nẵng. Bạn có 3 công cụ tìm kiếm:

**1. retrieve_context_text** - Tìm kiếm văn bản thông minh
   - Khi nào: Hỏi về menu, review, mô tả, đặc điểm, phong cách
   - Ví dụ: "Phở ngon giá rẻ", "Quán cafe view đẹp", "Nơi lãng mạn hẹn hò"
   - Đặc biệt: Tự động phát hiện category (cafe, pho, seafood...) và boost kết quả

**2. retrieve_similar_visuals** - Tìm theo hình ảnh
   - Khi nào: Người dùng gửi ảnh hoặc mô tả về không gian, decor
   - Scene filter: food, interior, exterior, view
   - Ví dụ: "Quán có không gian giống ảnh này"

**3. find_nearby_places** - Tìm theo vị trí
   - Khi nào: Hỏi về khoảng cách, "gần đây", "gần X", "quanh Y"
   - Ví dụ: "Quán cafe gần Cầu Rồng", "Nhà hàng gần bãi biển Mỹ Khê"
   - Đặc biệt: Có thể lấy chi tiết đầy đủ với photos, reviews

**4. search_social_media** - Tìm kiếm mạng xã hội và tin tức
   - Khi nào: Hỏi về "review", "tin hot", "trend", "tiktok", "facebook", "tin mới"
   - Ví dụ: "Review quán ăn ngon Đà Nẵng trên TikTok", "Tin hot tuần qua"
   - Tham số: query, freshness ("pw": tuần, "pm": tháng), platforms (["tiktok", "facebook", "reddit"])

**Quy tắc quan trọng:**
1. Phân tích intent để chọn ĐÚNG tool (không chỉ dùng 1 tool)
2. Với câu hỏi tổng quát ("quán cafe ngon") → dùng retrieve_context_text
3. Với câu hỏi vị trí ("gần X", "quanh Y") → dùng find_nearby_places
4. Với câu hỏi trend/review từ MXH -> dùng search_social_media
5. Với ảnh → dùng retrieve_similar_visuals
6. Trả lời tiếng Việt, thân thiện, cung cấp thông tin cụ thể (tên, rating, khoảng cách)
"""


REACT_SYSTEM_PROMPT = f"""Bạn là agent du lịch thông minh cho Đà Nẵng với khả năng suy luận multi-step.

{TOOL_DEFINITIONS}

**Quy trình:**
Với mỗi bước, bạn phải:
1. **Thought**: Suy nghĩ về bước tiếp theo cần làm
2. **Action**: Chọn tool hoặc "finish" nếu đủ thông tin
3. **Action Input**: JSON parameters cho tool

**Trả lời CHÍNH XÁC theo format JSON:**
```json
{{
  "thought": "Suy nghĩ của bạn...",
  "action": "tool_name hoặc finish",
  "action_input": {{"param1": "value1"}}
}}
```

**Quan trọng:**
- Nếu cần biết vị trí → dùng get_location_coordinates trước
- Nếu tìm theo khoảng cách → dùng find_nearby_places
- Nếu tìm review/trend MXH → dùng search_social_media
- Nếu cần lọc theo đặc điểm (view, không gian, giá) → dùng retrieve_context_text
- Khi đủ thông tin → action = "finish"
"""


GREETING_SYSTEM_PROMPT = "Bạn là LocalMate - trợ lý du lịch thân thiện cho Đà Nẵng. Trả lời ngắn gọn, thân thiện."


SYNTHESIS_SYSTEM_PROMPT = "Bạn là trợ lý du lịch thông minh cho Đà Nẵng. Trả lời format JSON."


# =============================================================================
# PROMPT TEMPLATES
# =============================================================================

def build_greeting_prompt(message: str, history: str | None = None) -> str:
    """
    Build prompt for greeting/simple message response.
    
    Args:
        message: User's message
        history: Optional conversation history
        
    Returns:
        Formatted prompt string
    """
    history_section = ""
    if history:
        history_section = f"Lịch sử hội thoại:\n{history}\n\n---\n"
    
    return f"""{history_section}User nói: "{message}"

Hãy trả lời thân thiện bằng tiếng Việt. Đây là lời chào hoặc tin nhắn đơn giản, không cần tìm kiếm địa điểm."""


def build_synthesis_prompt(
    message: str,
    context: str,
    history: str | None = None,
    include_steps: str | None = None,
) -> str:
    """
    Build prompt for synthesizing response from tool results.
    
    Args:
        message: User's query
        context: Tool results as formatted string
        history: Optional conversation history
        include_steps: Optional steps summary (for ReAct mode)
        
    Returns:
        Formatted prompt string
    """
    history_section = ""
    if history:
        history_section = f"""Lịch sử hội thoại trước đó:
{history}

---
"""

    steps_section = ""
    if include_steps:
        steps_section = f"""Dựa trên các bước suy luận và tìm kiếm sau:

{include_steps}

Và kết quả thu thập được:
"""

    return f"""{history_section}{steps_section}Dựa trên kết quả tìm kiếm sau, hãy trả lời câu hỏi của người dùng.

Câu hỏi hiện tại: {message}

{context}

**QUAN TRỌNG:** Trả lời theo format JSON:
```json
{{
  "response": "Câu trả lời tiếng Việt, thân thiện. Giới thiệu top 2-3 địa điểm phù hợp nhất.",
  "selected_place_ids": ["place_id_1", "place_id_2", "place_id_3"]
}}
```

Chỉ chọn những place_id xuất hiện trong kết quả tìm kiếm ở trên. Nếu không có địa điểm phù hợp, để mảng rỗng.
Nếu có lịch sử hội thoại, hãy cân nhắc ngữ cảnh trước đó khi trả lời."""


def build_reasoning_prompt(
    query: str,
    context_summary: str | None = None,
    previous_steps: list[dict] | None = None,
    image_url: str | None = None,
) -> str:
    """
    Build prompt for ReAct reasoning step.
    
    Args:
        query: User's query
        context_summary: Summary of context gathered so far
        previous_steps: List of previous reasoning steps
        image_url: Optional image URL if user provided image
        
    Returns:
        Formatted prompt string
    """
    # Context section
    context_text = ""
    if context_summary:
        context_text = f"\n{context_summary}\n"
    
    # Previous steps section
    steps_text = ""
    if previous_steps:
        steps_text = "\nKết quả từ các bước trước:\n"
        for step in previous_steps:
            tool = step.get("action", "N/A")
            observation = step.get("observation", None)
            steps_text += f"- {TOOL_PURPOSES.get(tool, tool)}: "
            if observation:
                result_count = len(observation) if isinstance(observation, list) else 1
                steps_text += f"✅ {result_count} items\n"
            else:
                steps_text += "❌ Không có kết quả\n"
        
        steps_text += "\n**⚠️ QUAN TRỌNG:** Nếu đã có đủ thông tin từ các bước trên → action = 'finish'\n"
    else:
        steps_text = "\nChưa có kết quả từ các tools trước đó.\n"
    
    # Image context
    image_text = ""
    if image_url:
        image_text = "\n**Lưu ý:** User đã gửi kèm ảnh. Có thể dùng retrieve_similar_visuals nếu cần.\n"
    
    return f"""**Câu hỏi của user:** {query}
{image_text}
{context_text}
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



# =============================================================================
# TOOL DEFINITIONS FOR MCP TOOLS
# =============================================================================

FIND_NEARBY_PLACES_TOOL = {
    "name": "find_nearby_places",
    "description": """Tìm địa điểm gần một vị trí hoặc lấy chi tiết địa điểm.

Dùng khi:
- Người dùng hỏi về vị trí, khoảng cách, "gần đây", "gần X"
- Cần tìm quán xung quanh một landmark (Cầu Rồng, Mỹ Khê, Bà Nà)
- Lấy chi tiết đầy đủ về một địa điểm cụ thể

Categories: Restaurant, Coffee shop, Cafe, Bar, Hotel, Seafood restaurant, 
Japanese restaurant, Korean restaurant, Gym, Fitness center, v.v.""",
    "parameters": {
        "location": "Tên địa điểm trung tâm (VD: 'Bãi biển Mỹ Khê', 'Cầu Rồng')",
        "category": "Loại địa điểm: restaurant, coffee, hotel, bar, seafood, gym, etc.",
        "max_distance_km": "Khoảng cách tối đa tính theo km (mặc định 5)",
        "limit": "Số kết quả tối đa (mặc định 10)",
    },
}


RETRIEVE_CONTEXT_TEXT_TOOL = {
    "name": "retrieve_context_text",
    "description": """Tìm kiếm thông tin địa điểm dựa trên văn bản, mô tả, đánh giá.

Dùng khi:
- Người dùng hỏi về menu, review, mô tả địa điểm
- Tìm kiếm theo đặc điểm: "quán cafe view đẹp", "phở ngon giá rẻ"
- Tìm theo không khí: "nơi lãng mạn", "chỗ yên tĩnh làm việc"

Hỗ trợ: Vietnamese + English""",
    "parameters": {
        "query": "Câu query tìm kiếm tự nhiên (VD: 'quán phở nước dùng đậm đà')",
        "limit": "Số kết quả tối đa (mặc định 10)",
    },
}


RETRIEVE_SIMILAR_VISUALS_TOOL = {
    "name": "retrieve_similar_visuals",
    "description": """Tìm địa điểm có hình ảnh tương tự.

Dùng khi:
- Người dùng gửi ảnh và muốn tìm nơi tương tự
- Mô tả về không gian, decor, view
- "Tìm quán có view như này", "Nơi nào có không gian giống ảnh này"
""",
    "parameters": {
        "image_url": "URL của ảnh cần tìm kiếm tương tự",
        "limit": "Số kết quả tối đa (mặc định 10)",
    },
}


SEARCH_SOCIAL_MEDIA_TOOL = {
    "name": "search_social_media",
    "description": """Tìm kiếm review, tin tức, trend trên mạng xã hội.

Dùng khi:
- Hỏi về "review", "tin hot", "trend", "viral"
- Tìm thông tin từ TikTok, Facebook, Reddit
- "Review quán ăn ngon Đà Nẵng trên TikTok"
""",
    "parameters": {
        "query": "Câu query tìm kiếm",
        "freshness": "pw: tuần qua, pm: tháng qua (mặc định: pw)",
        "platforms": "Danh sách platform: tiktok, facebook, reddit",
    },
}


# =============================================================================
# DATABASE CONSTANTS (Categories, Keywords mapping)
# =============================================================================

# Available categories in Neo4j database
AVAILABLE_CATEGORIES = [
    "Asian restaurant", "Athletic club", "Badminton court", "Bakery", "Bar",
    "Bistro", "Board game club", "Breakfast restaurant", "Cafe",
    "Cantonese restaurant", "Chicken restaurant", "Chinese restaurant",
    "Cocktail bar", "Coffee shop", "Country food restaurant", "Deli",
    "Dessert shop", "Disco club", "Dumpling restaurant", "Espresso bar",
    "Family restaurant", "Fine dining restaurant", "Fitness center",
    "Food court", "French restaurant", "Game store", "Gym",
    "Hamburger restaurant", "Holiday apartment rental", "Hot pot restaurant",
    "Hotel", "Ice cream shop", "Indian restaurant", "Irish pub",
    "Italian restaurant", "Izakaya restaurant", "Japanese restaurant",
    "Korean barbecue restaurant", "Korean restaurant", "Live music bar",
    "Malaysian restaurant", "Mexican restaurant", "Movie theater",
    "Musical club", "Noodle shop", "Pho restaurant", "Pickleball court",
    "Pizza restaurant", "Ramen restaurant", "Restaurant", "Restaurant or cafe",
    "Rice cake shop", "Sandwich shop", "Seafood restaurant", "Soccer field",
    "Soup shop", "Sports bar", "Sports club", "Sports complex", "Steak house",
    "Sushi restaurant", "Takeout Restaurant", "Tennis court", "Tiffin center",
    "Udon noodle restaurant", "Vegan restaurant", "Vegetarian restaurant",
    "Vietnamese restaurant",
]

# Category keywords for intent detection (user query -> category)
CATEGORY_KEYWORDS = {
    'cafe': ['cafe', 'cà phê', 'coffee', 'caphe', 'caphê'],
    'pho': ['phở', 'pho'],
    'banh_mi': ['bánh mì', 'banh mi', 'bread'],
    'seafood': ['hải sản', 'hai san', 'seafood', 'cá', 'tôm', 'cua'],
    'restaurant': ['nhà hàng', 'restaurant', 'quán ăn', 'ăn'],
    'bar': ['bar', 'pub', 'cocktail', 'beer', 'bia'],
    'hotel': ['hotel', 'khách sạn', 'resort', 'villa'],
    'japanese': ['nhật', 'japan', 'sushi', 'ramen'],
    'korean': ['hàn', 'korea', 'bbq'],
}

# Category keyword -> Database category name mapping
CATEGORY_TO_DB = {
    'cafe': ['Coffee shop', 'Cafe', 'Coffee house', 'Espresso bar'],
    'pho': ['Pho restaurant', 'Bistro', 'Restaurant', 'Vietnamese restaurant'],
    'banh_mi': ['Bakery', 'Tiffin center', 'Restaurant'],
    'seafood': ['Seafood restaurant', 'Restaurant', 'Asian restaurant'],
    'restaurant': ['Restaurant', 'Vietnamese restaurant', 'Asian restaurant'],
    'bar': ['Bar', 'Cocktail bar', 'Pub', 'Night club', 'Live music bar'],
    'hotel': ['Hotel', 'Resort', 'Apartment', 'Villa', 'Holiday apartment rental'],
    'japanese': ['Japanese restaurant', 'Sushi restaurant', 'Ramen restaurant'],
    'korean': ['Korean restaurant', 'Korean barbecue restaurant'],
}


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # System prompts
    "MMCA_SYSTEM_PROMPT",
    "REACT_SYSTEM_PROMPT",
    "GREETING_SYSTEM_PROMPT",
    "SYNTHESIS_SYSTEM_PROMPT",
    # Tool definitions
    "TOOL_DEFINITIONS",
    "TOOL_PURPOSES",
    # Tool-specific definitions
    "FIND_NEARBY_PLACES_TOOL",
    "RETRIEVE_CONTEXT_TEXT_TOOL",
    "RETRIEVE_SIMILAR_VISUALS_TOOL",
    "SEARCH_SOCIAL_MEDIA_TOOL",
    # Database constants
    "AVAILABLE_CATEGORIES",
    "CATEGORY_KEYWORDS",
    "CATEGORY_TO_DB",
    # Prompt builders
    "build_greeting_prompt",
    "build_synthesis_prompt",
    "build_reasoning_prompt",
]
