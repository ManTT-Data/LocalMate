"""ReAct Agent - Multi-step reasoning and tool execution.

Implements the ReAct (Reasoning + Acting) pattern:
1. Reason about what to do next
2. Execute a tool
3. Observe the result
4. Repeat until done or max steps reached
"""

import time
import json
import re
from typing import Any

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.state import AgentState, ReActStep
from app.agent.reasoning import (
    REACT_SYSTEM_PROMPT,
    parse_reasoning_response,
    build_reasoning_prompt,
    get_tool_purpose,
)
from app.mcp.tools import mcp_tools
from app.shared.integrations.gemini_client import GeminiClient
from app.shared.integrations.megallm_client import MegaLLMClient
from app.shared.logger import agent_logger, AgentWorkflow, WorkflowStep


# Default coordinates for Da Nang
DANANG_CENTER = (16.0544, 108.2022)


class ReActAgent:
    """
    ReAct Agent with multi-step tool chaining.
    
    Allows LLM to reason about each step and decide which tool to call next,
    using previous results to inform subsequent actions.
    """
    
    def __init__(self, provider: str = "MegaLLM", model: str | None = None, max_steps: int = 5):
        """
        Initialize ReAct agent.
        
        Args:
            provider: "Google" or "MegaLLM"
            model: Model name
            max_steps: Maximum reasoning steps (default 5)
        """
        self.provider = provider
        self.model = model
        self.max_steps = max_steps
        self.tools = mcp_tools
        
        # Initialize LLM client
        if provider == "Google":
            self.llm_client = GeminiClient(model=model)
        else:
            self.llm_client = MegaLLMClient(model=model)
        
        agent_logger.workflow_step(
            "ReAct Agent initialized",
            f"Provider: {provider}, Model: {model}, MaxSteps: {max_steps}"
        )
    
    async def run(
        self,
        query: str,
        db: AsyncSession,
        image_url: str | None = None,
        history: str | None = None,
    ) -> tuple[str, AgentState]:
        """
        Run the ReAct loop.
        
        Args:
            query: User's query
            db: Database session
            image_url: Optional image for visual search
            history: Conversation history
            
        Returns:
            Tuple of (final_response, agent_state)
        """
        start_time = time.time()
        
        # Initialize state
        state = AgentState(query=query, max_steps=self.max_steps)
        
        agent_logger.api_request(
            endpoint="/chat (ReAct)",
            method="POST",
            body={"query": query[:100], "max_steps": self.max_steps}
        )
        
        # ReAct loop
        while state.can_continue():
            step_start = time.time()
            step_number = state.current_step + 1
            
            agent_logger.workflow_step(f"ReAct Step {step_number}", "Reasoning...")
            
            try:
                # Step 1: Reason about what to do next
                reasoning = await self._reason(state, image_url)
                
                agent_logger.workflow_step(
                    f"Step {step_number} Thought",
                    reasoning.thought[:100]
                )
                agent_logger.workflow_step(
                    f"Step {step_number} Action",
                    f"{reasoning.action} → {json.dumps(reasoning.action_input, ensure_ascii=False)[:80]}"
                )
                
                # Step 2: Check if done
                if reasoning.action == "finish":
                    state.is_complete = True
                    state.steps.append(ReActStep(
                        step_number=step_number,
                        thought=reasoning.thought,
                        action="finish",
                        action_input={},
                        duration_ms=(time.time() - step_start) * 1000,
                    ))
                    break
                
                # Step 3: Execute tool
                observation = await self._execute_tool(
                    reasoning.action,
                    reasoning.action_input,
                    db,
                    image_url,
                )
                
                result_count = len(observation) if isinstance(observation, list) else 1
                agent_logger.tool_result(reasoning.action, result_count)
                
                # Step 4: Add step to state
                step = ReActStep(
                    step_number=step_number,
                    thought=reasoning.thought,
                    action=reasoning.action,
                    action_input=reasoning.action_input,
                    observation=observation,
                    duration_ms=(time.time() - step_start) * 1000,
                )
                state.add_step(step)
                
            except Exception as e:
                agent_logger.error(f"ReAct step {step_number} failed", e)
                state.error = str(e)
                break
        
        # Final synthesis
        state.total_duration_ms = (time.time() - start_time) * 1000
        
        if state.error:
            final_response = f"Xin lỗi, đã xảy ra lỗi: {state.error}"
            selected_place_ids = []
        else:
            try:
                final_response, selected_place_ids = await self._synthesize(state, history)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    agent_logger.error("ReAct synthesis failed due to rate limit", e)
                    final_response = "Xin lỗi, hệ thống đang quá tải. Vui lòng thử lại sau ít phút."
                    selected_place_ids = []
                else:
                    raise
        
        state.final_answer = final_response
        state.selected_place_ids = selected_place_ids  # Store for later enrichment
        
        agent_logger.api_response(
            "/chat (ReAct)",
            200,
            {"steps": len(state.steps), "tools": list(state.context.keys()), "places": len(selected_place_ids)},
            state.total_duration_ms,
        )
        
        return final_response, state
    
    async def _reason(self, state: AgentState, image_url: str | None = None) -> Any:
        """Get LLM reasoning for next step."""
        prompt = build_reasoning_prompt(
            query=state.query,
            context_summary=state.get_context_summary(),
            previous_steps=[s.to_dict() for s in state.steps],
            image_url=image_url,
        )
        
        agent_logger.llm_call(self.provider, self.model or "default", prompt[:100])
        
        response = await self.llm_client.generate(
            prompt=prompt,
            temperature=0.3,  # Lower temp for more deterministic reasoning
            system_instruction=REACT_SYSTEM_PROMPT,
        )
        
        return parse_reasoning_response(response)
    
    async def _execute_tool(
        self,
        action: str,
        action_input: dict,
        db: AsyncSession,
        image_url: str | None = None,
    ) -> Any:
        """Execute a tool and return observation."""
        agent_logger.tool_call(action, action_input)
        
        if action == "get_location_coordinates":
            location_name = action_input.get("location_name", "")
            coords = await self.tools.get_location_coordinates(location_name)
            if coords:
                return {"lat": coords[0], "lng": coords[1], "location": location_name}
            return {"error": f"Location not found: {location_name}"}
        
        elif action == "find_nearby_places":
            lat = action_input.get("lat", DANANG_CENTER[0])
            lng = action_input.get("lng", DANANG_CENTER[1])
            
            # If lat/lng are from previous step context
            if isinstance(lat, str) or isinstance(lng, str):
                lat, lng = DANANG_CENTER
            
            results = await self.tools.find_nearby_places(
                lat=lat,
                lng=lng,
                max_distance_km=action_input.get("max_distance_km", 3.0),
                category=action_input.get("category"),
                limit=action_input.get("limit", 5),
            )
            return [
                {
                    "place_id": r.place_id,
                    "name": r.name,
                    "category": r.category,
                    "distance_km": r.distance_km,
                    "rating": r.rating,
                }
                for r in results
            ]
        
        elif action == "retrieve_context_text":
            results = await self.tools.retrieve_context_text(
                db=db,
                query=action_input.get("query", ""),
                limit=action_input.get("limit", 5),
            )
            return [
                {
                    "place_id": r.place_id,
                    "name": r.name,
                    "category": r.category,
                    "rating": r.rating,
                    "source_text": r.source_text[:100] if r.source_text else "",
                }
                for r in results
            ]
        
        elif action == "retrieve_similar_visuals":
            url = action_input.get("image_url") or image_url
            if not url:
                return {"error": "No image URL provided"}
            
            results = await self.tools.retrieve_similar_visuals(
                db=db,
                image_url=url,
                limit=action_input.get("limit", 5),
            )
            return [
                {
                    "place_id": r.place_id,
                    "name": r.name,
                    "category": r.category,
                    "similarity": r.similarity,
                }
                for r in results
            ]
        
        elif action == "search_social_media":
            results = await self.tools.search_social_media(
                query=action_input.get("query", ""),
                limit=action_input.get("limit", 5),
                freshness=action_input.get("freshness", "pw"),
                platforms=action_input.get("platforms"),
            )
            return [
                {
                    "title": r.title,
                    "url": r.url,
                    "age": r.age,
                    "platform": r.platform,
                }
                for r in results
            ]

        
        else:
            return {"error": f"Unknown tool: {action}"}
    
    async def _synthesize(self, state: AgentState, history: str | None = None) -> tuple[str, list[str]]:
        """
        Synthesize final response from all collected information.
        
        Returns:
            Tuple of (response_text, selected_place_ids)
        """
        # Build context from all steps
        context_parts = []
        all_place_ids = []  # Collect all available place_ids
        
        for step in state.steps:
            if step.observation and step.action != "finish":
                context_parts.append(
                    f"Kết quả từ {step.action}:\n{json.dumps(step.observation, ensure_ascii=False, indent=2)}"
                )
                # Collect place_ids from observations
                if isinstance(step.observation, list):
                    for item in step.observation:
                        if isinstance(item, dict) and 'place_id' in item:
                            all_place_ids.append(item['place_id'])
        
        context = "\n\n".join(context_parts) if context_parts else "Không có kết quả."
        
        # Build history section
        history_section = ""
        if history:
            history_section = f"Lịch sử hội thoại:\n{history}\n\n---\n"
        
        # Build steps summary
        steps_summary = "\n".join([
            f"- Bước {s.step_number}: {s.thought[:60]}... → {get_tool_purpose(s.action)}"
            for s in state.steps
        ])
        
        prompt = f"""{history_section}Dựa trên các bước suy luận và tìm kiếm sau:

{steps_summary}

Và kết quả thu thập được:
{context}

Hãy trả lời câu hỏi của user một cách tự nhiên và hữu ích:
"{state.query}"

**QUAN TRỌNG:** Trả lời theo format JSON:
```json
{{
  "response": "Câu trả lời tiếng Việt, thân thiện. Giới thiệu top 2-3 địa điểm phù hợp nhất.",
  "selected_place_ids": ["place_id_1", "place_id_2", "place_id_3"]
}}
```

Chỉ chọn những place_id xuất hiện trong kết quả tìm kiếm ở trên. Nếu không có địa điểm, để mảng rỗng."""

        response = await self.llm_client.generate(
            prompt=prompt,
            temperature=0.7,
            system_instruction="Bạn là trợ lý du lịch thông minh cho Đà Nẵng. Trả lời format JSON.",
        )
        
        # Parse JSON response
        try:
            # Extract JSON from response
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                response = json_match.group(1)
            
            json_start = response.find('{')
            json_end = response.rfind('}')
            if json_start != -1 and json_end != -1:
                response = response[json_start:json_end + 1]
            
            data = json.loads(response)
            text_response = data.get("response", response)
            selected_ids = data.get("selected_place_ids", [])
            
            # Validate selected_ids are in available places
            valid_ids = [pid for pid in selected_ids if pid in all_place_ids]
            
            return text_response, valid_ids
            
        except (json.JSONDecodeError, KeyError):
            # Fallback: return raw response with no places
            agent_logger.error("Failed to parse synthesis JSON", None)
            return response, []
    
    def to_workflow(self, state: AgentState) -> AgentWorkflow:
        """Convert AgentState to AgentWorkflow for response."""
        workflow = AgentWorkflow(query=state.query)
        workflow.intent_detected = "react_multi_step"
        workflow.total_duration_ms = state.total_duration_ms
        workflow.tools_used = list(state.context.keys())
        
        for step in state.steps:
            workflow.add_step(WorkflowStep(
                step_name=f"Step {step.step_number}: {step.thought[:50]}...",
                tool_name=step.action if step.action != "finish" else None,
                purpose=get_tool_purpose(step.action),
                result_count=len(step.observation) if isinstance(step.observation, list) else 0,
                duration_ms=step.duration_ms,
            ))
        
        return workflow
