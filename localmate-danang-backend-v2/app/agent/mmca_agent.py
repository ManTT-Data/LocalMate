"""Multi-Modal Contextual Agent (MMCA) - ReAct Agent with MCP Tools.

Implements the Agent-Centric Orchestration pattern:
1. Parse user intent
2. Select appropriate MCP tool(s)
3. Execute tool(s) with logging
4. Synthesize final response with workflow trace

Supports multiple LLM providers: Google (Gemini) and MegaLLM (DeepSeek).
"""

import json
import re
import time
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.mcp.tools import mcp_tools
from app.shared.integrations.gemini_client import GeminiClient
from app.shared.integrations.megallm_client import MegaLLMClient
from app.shared.logger import agent_logger, AgentWorkflow, WorkflowStep
from app.shared.prompts import (
    MMCA_SYSTEM_PROMPT as SYSTEM_PROMPT,
    GREETING_SYSTEM_PROMPT,
    INTENT_SYSTEM_PROMPT,
    build_greeting_prompt,
    build_intent_prompt,
    build_synthesis_prompt,
)


# Default coordinates for Da Nang (if no location specified)
DANANG_CENTER = (16.0544, 108.2022)

# SYSTEM_PROMPT is imported from app.shared.prompts



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
    selected_place_ids: list[str] = field(default_factory=list)  # LLM-selected place IDs


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

        # Step 1: Analyze intent and plan tools (LLM-based)
        workflow.add_step(WorkflowStep(
            step_name="Intent Analysis",
            purpose="Phân tích câu hỏi để chọn tool phù hợp"
        ))
        
        agent_logger.workflow_step("Step 1: Intent Analysis", message[:80])
        
        tool_calls = await self._plan_tool_calls(message, image_url)
        
        # Set intent based on selected tools (from LLM)
        if not tool_calls:
            intent = "greeting"
        else:
            intent = " + ".join([tc.tool_name for tc in tool_calls])
        workflow.intent_detected = intent
        agent_logger.workflow_step("Intent detected", intent)
        
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
        response, selected_place_ids = await self._synthesize_response(message, tool_results, image_url, history)
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
        agent_logger.api_response("/chat", 200, {"response_len": len(response), "places": len(selected_place_ids)}, total_duration)
        
        return ChatResult(
            response=response,
            workflow=workflow,
            tools_used=workflow.tools_used,
            total_duration_ms=total_duration,
            tool_results=tool_results,
            selected_place_ids=selected_place_ids,
        )

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
        Use LLM to analyze message and plan which tools to call.

        Returns list of ToolCall objects with tool_name and arguments.
        Returns empty list for greetings/small-talk (LLM detects via is_greeting).
        """
        # If image is provided, always use visual search (fast path)
        if image_url:
            return [ToolCall(
                tool_name="retrieve_similar_visuals",
                arguments={"image_url": image_url, "limit": 5},
            )]
        
        # Use LLM to detect intent and select tools
        intent_prompt = build_intent_prompt(message, has_image=bool(image_url))
        
        try:
            intent_response = await self.llm_client.generate(
                prompt=intent_prompt,
                temperature=0.2,  # Low temperature for consistent JSON
                system_instruction=INTENT_SYSTEM_PROMPT,
            )
            
            agent_logger.workflow_step("LLM Intent Detection", intent_response[:200])
            
            # Parse JSON response
            tool_calls = self._parse_intent_response(intent_response, message)
            return tool_calls
            
        except Exception as e:
            agent_logger.error(f"Intent detection failed: {e}", None)
            # Fallback to text search
            return [ToolCall(
                tool_name="retrieve_context_text",
                arguments={"query": message, "limit": 5},
            )]
    
    def _parse_intent_response(self, response: str, original_message: str) -> list[ToolCall]:
        """Parse LLM intent detection response into ToolCall list."""
        try:
            # Extract JSON from response
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                response = json_match.group(1)
            
            # Find JSON object
            json_start = response.find('{')
            json_end = response.rfind('}')
            if json_start != -1 and json_end != -1:
                response = response[json_start:json_end + 1]
            
            data = json.loads(response)
            
            # Check if greeting
            if data.get("is_greeting", False):
                return []
            
            # Parse tools
            tools = data.get("tools", [])
            tool_calls = []
            
            for tool in tools:
                name = tool.get("name")
                arguments = tool.get("arguments", {})
                
                # Validate tool name
                valid_tools = ["retrieve_context_text", "find_nearby_places", 
                              "search_social_media", "retrieve_similar_visuals"]
                if name not in valid_tools:
                    continue
                
                # Ensure required arguments
                if name == "retrieve_context_text":
                    arguments.setdefault("query", original_message)
                    arguments.setdefault("limit", 5)
                elif name == "find_nearby_places":
                    # Need to geocode location if provided
                    location = arguments.get("location", "")
                    arguments.setdefault("max_distance_km", 3.0)
                    arguments.setdefault("limit", 5)
                    # Will handle geocoding in execute step
                elif name == "search_social_media":
                    arguments.setdefault("query", original_message)
                    arguments.setdefault("limit", 5)
                    arguments.setdefault("freshness", "pw")
                
                tool_calls.append(ToolCall(tool_name=name, arguments=arguments))
            
            # If no tools selected, default to text search
            if not tool_calls:
                tool_calls.append(ToolCall(
                    tool_name="retrieve_context_text",
                    arguments={"query": original_message, "limit": 5},
                ))
            
            return tool_calls
            
        except (json.JSONDecodeError, KeyError) as e:
            agent_logger.error(f"Failed to parse intent JSON: {e}", None)
            # Fallback to text search
            return [ToolCall(
                tool_name="retrieve_context_text",
                arguments={"query": original_message, "limit": 5},
            )]


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
                # Handle geocoding if location name provided instead of lat/lng
                lat = tool_call.arguments.get("lat")
                lng = tool_call.arguments.get("lng")
                
                if lat is None or lng is None:
                    # Try to geocode from location name
                    location = tool_call.arguments.get("location", "")
                    if location:
                        coords = await self.tools.get_location_coordinates(location)
                        if coords:
                            lat, lng = coords
                        else:
                            lat, lng = DANANG_CENTER
                    else:
                        lat, lng = DANANG_CENTER
                
                results = await self.tools.find_nearby_places(
                    lat=lat,
                    lng=lng,
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
    ) -> tuple[str, list[str]]:
        """
        Synthesize final response from tool results with conversation history.
        
        Returns:
            Tuple of (response_text, selected_place_ids)
        """
        # Collect all available place_ids from tool results
        all_place_ids = []
        for tool_call in tool_results:
            if tool_call.result:
                for item in tool_call.result:
                    if isinstance(item, dict) and 'place_id' in item:
                        all_place_ids.append(item['place_id'])
        
        # If no tool results (greeting case), return simple response
        if not tool_results:
            prompt = build_greeting_prompt(message, history)
            
            response = await self.llm_client.generate(
                prompt=prompt,
                temperature=0.7,
                system_instruction=GREETING_SYSTEM_PROMPT,
            )
            return response, []
        
        # Build context from tool results
        context_parts = []
        for tool_call in tool_results:
            if tool_call.result:
                context_parts.append(
                    f"Kết quả từ {tool_call.tool_name}:\n{json.dumps(tool_call.result, ensure_ascii=False, indent=2)}"
                )

        context = "\n\n".join(context_parts)

        # Generate response using LLM with JSON format for place selection
        prompt = build_synthesis_prompt(message, context, history)

        agent_logger.llm_call(self.provider, self.model or "default", prompt[:100])

        raw_response = await self.llm_client.generate(
            prompt=prompt,
            temperature=0.7,
            system_instruction=SYSTEM_PROMPT,
        )

        # Parse JSON response
        try:
            # Extract JSON from code blocks
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find raw JSON
                json_start = raw_response.find('{')
                json_end = raw_response.rfind('}')
                if json_start != -1 and json_end != -1:
                    json_str = raw_response[json_start:json_end + 1]
                else:
                    # No JSON found, return raw response
                    return raw_response, []
            
            data = json.loads(json_str)
            text_response = data.get("response", raw_response)
            selected_ids = data.get("selected_place_ids", [])
            
            # Validate selected_ids are in available places
            valid_ids = [pid for pid in selected_ids if pid in all_place_ids]
            
            return text_response, valid_ids
            
        except (json.JSONDecodeError, KeyError) as e:
            agent_logger.error("Failed to parse synthesis JSON", e)
            # Fallback: return raw response with no places
            return raw_response, []

    def _extract_location(self, message: str) -> str | None:
        """Extract location name from message using pattern matching."""
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
