"""
Prompts and Constants for LocalMate Agent.

This module centralizes all prompts, keywords, and mappings used by the agent.
Allows for easier modification and localization.
"""

# =============================================================================
# DEFAULT VALUES
# =============================================================================

# Default coordinates for Da Nang center (if no location specified)
DANANG_CENTER = (16.0544, 108.2022)


# =============================================================================
# SYSTEM PROMPTS
# =============================================================================

SYSTEM_PROMPT = """Bạn là trợ lý du lịch thông minh cho Đà Nẵng. Bạn có 4 công cụ tìm kiếm:

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


REACT_SYSTEM_PROMPT = """Bạn là agent du lịch thông minh cho Đà Nẵng với khả năng suy luận multi-step.

**Tools có sẵn:**
1. `get_location_coordinates` - Lấy tọa độ từ tên địa điểm
   - Input: {"location_name": "Dragon Bridge"}
   - Output: {"lat": 16.06, "lng": 108.22}

2. `find_nearby_places` - Tìm địa điểm gần vị trí
   - Input: {"lat": 16.06, "lng": 108.22, "category": "cafe", "max_distance_km": 2}
   - Output: [{name, category, distance_km, rating}]

3. `retrieve_context_text` - Tìm kiếm semantic trong text
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
2. **Action**: Chọn tool để gọi
3. **Action Input**: JSON arguments cho tool
4. **Observation**: Kết quả trả về (system sẽ điền)

Khi đã có đủ thông tin, output:
**Final Answer**: [Câu trả lời cuối cùng cho user]

**Ví dụ:**
User: "Tìm quán cafe gần Cầu Rồng"

Thought: Cần lấy tọa độ Cầu Rồng trước, sau đó tìm cafe gần đó.
Action: get_location_coordinates
Action Input: {"location_name": "Cầu Rồng"}

[Observation: {"lat": 16.0614, "lng": 108.2279}]

Thought: Đã có tọa độ, giờ tìm cafe trong bán kính 2km.
Action: find_nearby_places
Action Input: {"lat": 16.0614, "lng": 108.2279, "category": "cafe", "max_distance_km": 2}

[Observation: [...]]

Thought: Đã có danh sách cafe. Tổng hợp và trả lời.
Final Answer: Dưới đây là những quán cafe gần Cầu Rồng...
"""


SYNTHESIS_PROMPT_TEMPLATE = """{history_section}Dựa trên kết quả tìm kiếm sau, hãy trả lời câu hỏi của người dùng một cách tự nhiên và hữu ích.

Câu hỏi hiện tại: {message}

{context}

Hãy trả lời bằng tiếng Việt, thân thiện. Nếu có nhiều kết quả, hãy giới thiệu top 2-3 địa điểm phù hợp nhất.
Nếu có lịch sử hội thoại, hãy cân nhắc ngữ cảnh trước đó khi trả lời."""


# =============================================================================
# LOCATION MAPPINGS
# =============================================================================

# Known locations with their English names for geocoding
KNOWN_LOCATIONS: dict[str, str] = {
    # My Khe Beach
    "mỹ khê": "My Khe Beach",
    "my khe": "My Khe Beach",
    "bãi biển mỹ khê": "My Khe Beach",
    
    # Dragon Bridge
    "cầu rồng": "Dragon Bridge",
    "cau rong": "Dragon Bridge",
    "dragon bridge": "Dragon Bridge",
    
    # Ba Na Hills
    "bà nà": "Ba Na Hills",
    "ba na": "Ba Na Hills",
    "bà nà hills": "Ba Na Hills",
    
    # Son Tra Peninsula
    "sơn trà": "Son Tra Peninsula",
    "son tra": "Son Tra Peninsula",
    
    # Hoi An
    "hội an": "Hoi An",
    "hoi an": "Hoi An",
    
    # Marble Mountains
    "ngũ hành sơn": "Marble Mountains",
    "ngu hanh son": "Marble Mountains",
    "marble mountains": "Marble Mountains",
    
    # Han River Bridge
    "cầu sông hàn": "Han River Bridge",
    "cau song han": "Han River Bridge",
    
    # Asia Park
    "asia park": "Asia Park",
    "công viên châu á": "Asia Park",
}


# =============================================================================
# CATEGORY MAPPINGS
# =============================================================================

# Category keywords for intent detection
CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "cafe": ["cafe", "cà phê", "coffee", "caphe"],
    "restaurant": ["nhà hàng", "quán ăn", "restaurant", "ăn", "ăn uống"],
    "beach": ["bãi biển", "beach", "biển"],
    "attraction": ["điểm tham quan", "du lịch", "attraction", "tham quan"],
    "hotel": ["khách sạn", "hotel", "lưu trú", "homestay", "resort"],
    "bar": ["bar", "pub", "quán bar", "club"],
    "gym": ["gym", "fitness", "tập gym", "phòng tập"],
    "seafood": ["hải sản", "seafood", "cua", "tôm", "cá"],
    "pho": ["phở", "pho"],
    "banh mi": ["bánh mì", "banh mi"],
}


# =============================================================================
# INTENT DETECTION KEYWORDS
# =============================================================================

# Keywords indicating location-based queries
LOCATION_KEYWORDS: list[str] = [
    "gần", "cách", "nearby", "gần đây", "quanh", "xung quanh",
    "khoảng cách", "bên cạnh", "cạnh", "kế bên"
]

# Keywords indicating social media search
SOCIAL_KEYWORDS: list[str] = [
    "review", "tin hot", "trend", "tin mới", "tiktok", "facebook", 
    "reddit", "youtube", "mạng xã hội", "đánh giá", "bình luận",
    "trending", "viral", "hot"
]
