"""Multi-Modal Contextual Agent (MMCA) - ReAct Agent with MCP Tools.

Implements the Agent-Centric Orchestration pattern from phase1.md:
1. Parse user intent
2. Select appropriate MCP tool(s)
3. Execute tool(s)
4. Synthesize final response

Supports multiple LLM providers: Google (Gemini) and MegaLLM (DeepSeek).
"""

import json
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.mcp.tools import mcp_tools
from app.shared.integrations.gemini_client import GeminiClient
from app.shared.integrations.megallm_client import MegaLLMClient


# Default coordinates for Da Nang (if no location specified)
DANANG_CENTER = (16.0544, 108.2022)

# System prompt for the agent - balanced for all 3 tools
SYSTEM_PROMPT = """Bạn là trợ lý du lịch thông minh cho Đà Nẵng. Bạn có 3 công cụ tìm kiếm:

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

**Quy tắc quan trọng:**
1. Phân tích intent để chọn ĐÚNG tool (không chỉ dùng 1 tool)
2. Với câu hỏi tổng quát ("quán cafe ngon") → dùng retrieve_context_text
3. Với câu hỏi vị trí ("gần X", "quanh Y") → dùng find_nearby_places
4. Với ảnh → dùng retrieve_similar_visuals
5. Có thể kết hợp nhiều tools để có kết quả tốt nhất
6. Trả lời tiếng Việt, thân thiện, cung cấp thông tin cụ thể (tên, rating, khoảng cách)
"""


@dataclass
class ChatMessage:
    """Chat message model."""

    role: str  # "user" or "assistant"
    content: str


@dataclass
class ToolCall:
    """Tool call result."""

    tool_name: str
    arguments: dict
    result: list | None = None


class MMCAAgent:
    """
    Multi-Modal Contextual Agent.

    Implements ReAct (Reasoning + Acting) pattern:
    1. Observe: Parse user message and intent
    2. Think: Decide which tool(s) to use
    3. Act: Execute MCP tools
    4. Synthesize: Generate final response

    Supports multiple LLM providers:
    - Google: Gemini models
    - MegaLLM: DeepSeek models (OpenAI-compatible)
    """

    def __init__(self, provider: str = "MegaLLM", model: str | None = None):
        """
        Initialize agent with LLM provider and model.

        Args:
            provider: "Google" or "MegaLLM"
            model: Model name (uses default if None)
        """
        self.provider = provider
        self.model = model
        self.tools = mcp_tools
        self.conversation_history: list[ChatMessage] = []

        # Initialize LLM client based on provider
        if provider == "Google":
            self.llm_client = GeminiClient(model=model)
        else:
            self.llm_client = MegaLLMClient(model=model)

    async def chat(
        self,
        message: str,
        db: AsyncSession,
        image_url: str | None = None,
        history: str | None = None,
    ) -> str:
        """
        Process a chat message and return response.

        Args:
            message: User's natural language message
            db: Database session for pgvector queries
            image_url: Optional image URL for visual search
            history: Optional conversation history string

        Returns:
            Agent's response as string
        """
        # Add user message to internal history
        self.conversation_history.append(ChatMessage(role="user", content=message))

        # Step 1: Analyze intent and decide tool usage
        tool_calls = await self._plan_tool_calls(message, image_url)

        # Step 2: Execute tools
        tool_results = []
        for tool_call in tool_calls:
            result = await self._execute_tool(tool_call, db)
            tool_results.append(result)

        # Step 3: Synthesize response with history context
        response = await self._synthesize_response(message, tool_results, image_url, history)

        # Add assistant response to internal history
        self.conversation_history.append(ChatMessage(role="assistant", content=response))

        return response

    async def _plan_tool_calls(
        self,
        message: str,
        image_url: str | None = None,
    ) -> list[ToolCall]:
        """
        Analyze message and plan which tools to call.

        Returns list of ToolCall objects with tool_name and arguments.
        """
        tool_calls = []

        # If image is provided, always use visual search
        if image_url:
            tool_calls.append(ToolCall(
                tool_name="retrieve_similar_visuals",
                arguments={"image_url": image_url, "limit": 5},
            ))

        # Analyze message for location/proximity queries
        location_keywords = ["gần", "cách", "nearby", "gần đây", "quanh", "xung quanh"]
        if any(kw in message.lower() for kw in location_keywords):
            # Extract location name from message
            location = self._extract_location(message)
            category = self._extract_category(message)

            # Get coordinates for the location
            coords = await self.tools.get_location_coordinates(location) if location else None
            lat, lng = coords if coords else DANANG_CENTER

            tool_calls.append(ToolCall(
                tool_name="find_nearby_places",
                arguments={
                    "lat": lat,
                    "lng": lng,
                    "category": category,
                    "max_distance_km": 3.0,
                    "limit": 5,
                },
            ))

        # For general queries without location keywords, use text search
        # But skip if we already have graph results
        if not tool_calls:
            tool_calls.append(ToolCall(
                tool_name="retrieve_context_text",
                arguments={"query": message, "limit": 5},
            ))

        return tool_calls

    async def _execute_tool(
        self,
        tool_call: ToolCall,
        db: AsyncSession,
    ) -> ToolCall:
        """Execute a single tool and return results."""
        try:
            if tool_call.tool_name == "retrieve_context_text":
                results = await self.tools.retrieve_context_text(
                    db=db,
                    query=tool_call.arguments.get("query", ""),
                    limit=tool_call.arguments.get("limit", 10),
                )
                tool_call.result = [
                    {
                        "place_id": r.place_id,
                        "name": r.name,
                        "category": r.category,
                        "rating": r.rating,
                        "similarity": r.similarity,
                        "description": r.description,
                        "source_text": r.source_text,
                    }
                    for r in results
                ]

            elif tool_call.tool_name == "retrieve_similar_visuals":
                results = await self.tools.retrieve_similar_visuals(
                    db=db,
                    image_url=tool_call.arguments.get("image_url"),
                    limit=tool_call.arguments.get("limit", 10),
                )
                tool_call.result = [
                    {
                        "place_id": r.place_id,
                        "name": r.name,
                        "category": r.category,
                        "rating": r.rating,
                        "similarity": r.similarity,
                        "matched_images": r.matched_images,
                        "image_url": r.image_url,
                    }
                    for r in results
                ]

            elif tool_call.tool_name == "find_nearby_places":
                results = await self.tools.find_nearby_places(
                    lat=tool_call.arguments.get("lat", DANANG_CENTER[0]),
                    lng=tool_call.arguments.get("lng", DANANG_CENTER[1]),
                    max_distance_km=tool_call.arguments.get("max_distance_km", 5.0),
                    category=tool_call.arguments.get("category"),
                    limit=tool_call.arguments.get("limit", 10),
                )
                tool_call.result = [
                    {
                        "place_id": r.place_id,
                        "name": r.name,
                        "category": r.category,
                        "distance_km": r.distance_km,
                        "rating": r.rating,
                        "description": r.description,
                    }
                    for r in results
                ]

        except Exception as e:
            tool_call.result = [{"error": str(e)}]

        return tool_call

    async def _synthesize_response(
        self,
        message: str,
        tool_results: list[ToolCall],
        image_url: str | None = None,
        history: str | None = None,
    ) -> str:
        """Synthesize final response from tool results with conversation history."""
        # Build context from tool results
        context_parts = []
        for tool_call in tool_results:
            if tool_call.result:
                context_parts.append(
                    f"Kết quả từ {tool_call.tool_name}:\n{json.dumps(tool_call.result, ensure_ascii=False, indent=2)}"
                )

        context = "\n\n".join(context_parts) if context_parts else "Không tìm thấy kết quả phù hợp."

        # Build history section if available
        history_section = ""
        if history:
            history_section = f"""Lịch sử hội thoại trước đó:
{history}

---
"""

        # Generate response using LLM
        prompt = f"""{history_section}Dựa trên kết quả tìm kiếm sau, hãy trả lời câu hỏi của người dùng một cách tự nhiên và hữu ích.

Câu hỏi hiện tại: {message}

{context}

Hãy trả lời bằng tiếng Việt, thân thiện. Nếu có nhiều kết quả, hãy giới thiệu top 2-3 địa điểm phù hợp nhất.
Nếu có lịch sử hội thoại, hãy cân nhắc ngữ cảnh trước đó khi trả lời."""

        response = await self.llm_client.generate(
            prompt=prompt,
            temperature=0.7,
            system_instruction=SYSTEM_PROMPT,
        )

        return response

    def _extract_location(self, message: str) -> str | None:
        """Extract location name from message using pattern matching.
        
        Uses a dictionary of known locations in Da Nang for fast matching.
        """
        # Known locations in Da Nang (lowercase for matching)
        known_locations = {
            "mỹ khê": "My Khe Beach",
            "my khe": "My Khe Beach",
            "bãi biển mỹ khê": "My Khe Beach",
            "cầu rồng": "Dragon Bridge",
            "cau rong": "Dragon Bridge",
            "dragon bridge": "Dragon Bridge",
            "bà nà": "Ba Na Hills",
            "ba na": "Ba Na Hills",
            "bà nà hills": "Ba Na Hills",
            "sơn trà": "Son Tra Peninsula",
            "son tra": "Son Tra Peninsula",
            "hội an": "Hoi An",
            "hoi an": "Hoi An",
            "ngũ hành sơn": "Marble Mountains",
            "ngu hanh son": "Marble Mountains",
            "marble mountains": "Marble Mountains",
            "khách sạn rex": "Rex Hotel",
            "rex hotel": "Rex Hotel",
            "rex": "Rex Hotel",
            "intercontinental": "InterContinental Danang",
            "novotel": "Novotel Danang",
            "hilton": "Hilton Danang",
            "hyatt": "Hyatt Regency Danang",
            "pullman": "Pullman Danang",
        }
        
        message_lower = message.lower()
        for pattern, location in known_locations.items():
            if pattern in message_lower:
                return location
        
        return None

    def _extract_category(self, message: str) -> str | None:
        """Extract place category from message."""
        categories = {
            "cafe": ["cafe", "cà phê", "coffee"],
            "restaurant": ["nhà hàng", "quán ăn", "restaurant", "ăn"],
            "beach": ["bãi biển", "beach", "biển"],
            "attraction": ["điểm tham quan", "du lịch", "attraction"],
            "hotel": ["khách sạn", "hotel", "lưu trú"],
            "bar": ["bar", "pub", "quán bar"],
        }

        message_lower = message.lower()
        for category, keywords in categories.items():
            if any(kw in message_lower for kw in keywords):
                return category

        return None

    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history = []


# Default agent instance (using MegaLLM)
mmca_agent = MMCAAgent()
