"""Multi-Modal Contextual Agent (MMCA) - ReAct Agent with MCP Tools.

Implements the Agent-Centric Orchestration pattern:
1. Parse user intent
2. Select appropriate MCP tool(s)
3. Execute tool(s) with logging
4. Synthesize final response with workflow trace

Supports multiple LLM providers: Google (Gemini) and MegaLLM (DeepSeek).
"""

import json
import time
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.mcp.tools import mcp_tools
from app.shared.integrations.gemini_client import GeminiClient
from app.shared.integrations.megallm_client import MegaLLMClient
from app.shared.logger import agent_logger, AgentWorkflow, WorkflowStep
from app.shared.constants import (
    DANANG_CENTER,
    SYSTEM_PROMPT,
    SYNTHESIS_PROMPT_TEMPLATE,
    KNOWN_LOCATIONS,
    CATEGORY_KEYWORDS,
    LOCATION_KEYWORDS,
    SOCIAL_KEYWORDS,
)



@dataclass
class ChatMessage:
    """Chat message model."""
    role: str  # "user" or "assistant"
    content: str


@dataclass
class ToolCall:
    """Tool call with arguments and results."""
    tool_name: str
    arguments: dict
    result: list | None = None
    duration_ms: float = 0


@dataclass
class ChatResult:
    """Complete chat result with response and workflow."""
    response: str
    workflow: AgentWorkflow
    tools_used: list[str] = field(default_factory=list)
    total_duration_ms: float = 0
    tool_results: list = field(default_factory=list)  # List of ToolCall with results


class MMCAAgent:
    """
    Multi-Modal Contextual Agent with Logging and Workflow Tracing.

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
        
        agent_logger.workflow_step("Agent initialized", f"Provider: {provider}, Model: {model}")

    async def chat(
        self,
        message: str,
        db: AsyncSession,
        image_url: str | None = None,
        history: str | None = None,
    ) -> ChatResult:
        """
        Process a chat message and return response with workflow trace.

        Args:
            message: User's natural language message
            db: Database session for pgvector queries
            image_url: Optional image URL for visual search
            history: Optional conversation history string

        Returns:
            ChatResult with response, workflow, and metadata
        """
        start_time = time.time()
        
        # Initialize workflow tracking
        workflow = AgentWorkflow(query=message)
        
        # Log incoming request
        agent_logger.api_request(
            endpoint="/chat",
            method="POST",
            body={"message": message[:100], "has_image": bool(image_url), "has_history": bool(history)}
        )
        
        # Add user message to internal history
        self.conversation_history.append(ChatMessage(role="user", content=message))

        # Step 1: Analyze intent and decide tool usage
        workflow.add_step(WorkflowStep(
            step_name="Intent Analysis",
            purpose="Phân tích câu hỏi để chọn tool phù hợp"
        ))
        
        agent_logger.workflow_step("Step 1: Intent Analysis", message[:80])
        intent = self._detect_intent(message, image_url)
        workflow.intent_detected = intent
        agent_logger.workflow_step("Intent detected", intent)
        
        tool_calls = await self._plan_tool_calls(message, image_url)
        
        workflow.add_step(WorkflowStep(
            step_name="Tool Planning",
            purpose=f"Chọn {len(tool_calls)} tool(s) để thực thi",
            output_summary=", ".join([tc.tool_name for tc in tool_calls])
        ))

        # Step 2: Execute tools
        agent_logger.workflow_step("Step 2: Execute Tools", f"{len(tool_calls)} tool(s)")
        tool_results = []
        
        for tool_call in tool_calls:
            tool_start = time.time()
            
            agent_logger.tool_call(tool_call.tool_name, tool_call.arguments)
            
            result = await self._execute_tool(tool_call, db)
            result.duration_ms = (time.time() - tool_start) * 1000
            
            result_count = len(result.result) if result.result else 0
            agent_logger.tool_result(
                tool_call.tool_name,
                result_count,
                result.result[0] if result.result else None
            )
            
            # Add to workflow
            workflow.add_step(WorkflowStep(
                step_name=f"Execute {tool_call.tool_name}",
                tool_name=tool_call.tool_name,
                purpose=self._get_tool_purpose(tool_call.tool_name),
                input_summary=json.dumps(tool_call.arguments, ensure_ascii=False)[:100],
                result_count=result_count,
                duration_ms=result.duration_ms
            ))
            
            tool_results.append(result)

        # Step 3: Synthesize response with history context
        agent_logger.workflow_step("Step 3: Synthesize Response")
        
        llm_start = time.time()
        response = await self._synthesize_response(message, tool_results, image_url, history)
        llm_duration = (time.time() - llm_start) * 1000
        
        agent_logger.llm_response(self.provider, response[:100], tokens=None)
        
        workflow.add_step(WorkflowStep(
            step_name="LLM Synthesis",
            purpose="Tổng hợp kết quả và tạo phản hồi",
            duration_ms=llm_duration
        ))

        # Add assistant response to internal history
        self.conversation_history.append(ChatMessage(role="assistant", content=response))
        
        # Calculate total duration
        total_duration = (time.time() - start_time) * 1000
        workflow.total_duration_ms = total_duration
        
        # Log complete
        agent_logger.api_response("/chat", 200, {"response_len": len(response)}, total_duration)
        
        return ChatResult(
            response=response,
            workflow=workflow,
            tools_used=workflow.tools_used,
            total_duration_ms=total_duration,
            tool_results=tool_results,  # Include tool results for place extraction
        )

    def _detect_intent(self, message: str, image_url: str | None) -> str:
        """Detect user intent for logging."""
        intents = []
        
        if image_url:
            intents.append("visual_search")
        
        if any(kw in message.lower() for kw in LOCATION_KEYWORDS):
            intents.append("location_search")
        
        if not intents:
            intents.append("text_search")
        
        # Social intent detection
        if any(kw in message.lower() for kw in SOCIAL_KEYWORDS):
            intents.append("social_search")
            
        return " + ".join(intents)

    def _get_tool_purpose(self, tool_name: str) -> str:
        """Get human-readable purpose for tool."""
        purposes = {
            "retrieve_context_text": "Tìm kiếm semantic trong văn bản (review, mô tả)",
            "retrieve_similar_visuals": "Tìm địa điểm có hình ảnh tương tự",
            "find_nearby_places": "Tìm địa điểm gần vị trí được nhắc đến",
            "search_social_media": "Tìm kiếm thông tin từ mạng xã hội (news, trends)",
        }
        return purposes.get(tool_name, tool_name)

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

        # Check for social media intent FIRST
        if any(kw in message.lower() for kw in SOCIAL_KEYWORDS):
            # Determine freshness
            freshness = "pw"  # Default past week
            if "tháng" in message.lower() or "month" in message.lower():
                freshness = "pm"
            
            # Determine platforms
            platforms = []
            for p in ["tiktok", "facebook", "reddit", "youtube", "twitter", "instagram"]:
                if p in message.lower():
                    platforms.append(p)
            
            tool_calls.append(ToolCall(
                tool_name="search_social_media",
                arguments={
                    "query": message,
                    "limit": 5,
                    "freshness": freshness,
                    "platforms": platforms if platforms else None
                }
            ))

        # Analyze message for location/proximity queries
        if any(kw in message.lower() for kw in LOCATION_KEYWORDS):
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

        # For general queries without location keywords AND NO SOCIAL INTENT, use text search
        # If social search is already triggered, we might skip text search to avoid noise, 
        # or keep it if query is mixed. For now, let's keep text search only if no other tools used.
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

            elif tool_call.tool_name == "search_social_media":
                results = await self.tools.search_social_media(
                    query=tool_call.arguments.get("query", ""),
                    limit=tool_call.arguments.get("limit", 10),
                    freshness=tool_call.arguments.get("freshness", "pw"),
                    platforms=tool_call.arguments.get("platforms"),
                )
                tool_call.result = [
                    {
                        "title": r.title,
                        "url": r.url,
                        "description": r.description,
                        "age": r.age,
                        "platform": r.platform,
                    }
                    for r in results
                ]


        except Exception as e:
            agent_logger.error(f"Tool execution failed: {tool_call.tool_name}", e)
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

        agent_logger.llm_call(self.provider, self.model or "default", prompt[:100])

        response = await self.llm_client.generate(
            prompt=prompt,
            temperature=0.7,
            system_instruction=SYSTEM_PROMPT,
        )

        return response

    def _extract_location(self, message: str) -> str | None:
        """Extract location name from message using pattern matching."""
        message_lower = message.lower()
        for pattern, location in KNOWN_LOCATIONS.items():
            if pattern in message_lower:
                return location
        
        return None

    def _extract_category(self, message: str) -> str | None:
        """Extract place category from message."""
        message_lower = message.lower()
        for category, keywords in CATEGORY_KEYWORDS.items():
            if any(kw in message_lower for kw in keywords):
                return category

        return None

    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history = []


# Default agent instance (using MegaLLM)
mmca_agent = MMCAAgent()
