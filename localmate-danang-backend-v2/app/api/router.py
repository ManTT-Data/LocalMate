"""API Router with /chat endpoint for Swagger testing."""

from enum import Enum
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, UploadFile, File, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.mmca_agent import MMCAAgent
from app.agent.react_agent import ReActAgent
from app.shared.db.session import get_db
from app.core.config import settings
from app.mcp.tools import mcp_tools
from app.shared.chat_history import chat_history


router = APIRouter()


class LLMProvider(str, Enum):
    """Available LLM providers."""

    GOOGLE = "Google"
    MEGALLM = "MegaLLM"


class ChatRequest(BaseModel):
    """Chat request model."""

    message: str = Field(
        ...,
        description="User message in natural language",
        examples=["Tìm quán cafe gần bãi biển Mỹ Khê"],
    )
    user_id: str = Field(
        default="anonymous",
        description="User ID for session management",
        examples=["user_123", "anonymous"],
    )
    session_id: str | None = Field(
        None,
        description="Session ID (optional, uses 'default' if not provided)",
        examples=["session_abc", "default"],
    )
    image_url: str | None = Field(
        None,
        description="Optional image URL for visual similarity search",
        examples=["https://example.com/cafe.jpg"],
    )
    provider: LLMProvider = Field(
        default=LLMProvider.MEGALLM,
        description="LLM provider to use: Google or MegaLLM",
    )
    model: str | None = Field(
        None,
        description=f"Model name. Defaults: Google={settings.default_gemini_model}, MegaLLM={settings.default_megallm_model}",
        examples=["gemini-2.0-flash", "deepseek-r1-distill-llama-70b"],
    )
    react_mode: bool = Field(
        default=False,
        description="Enable ReAct multi-step reasoning mode",
    )
    max_steps: int = Field(
        default=5,
        description="Maximum reasoning steps for ReAct mode",
        ge=1,
        le=10,
    )


class WorkflowStepResponse(BaseModel):
    """Workflow step info."""

    step: str = Field(..., description="Step name")
    tool: str | None = Field(None, description="Tool used")
    purpose: str = Field(default="", description="Purpose of this step")
    results: int = Field(default=0, description="Number of results")


class WorkflowResponse(BaseModel):
    """Workflow trace for debugging."""

    query: str = Field(..., description="Original query")
    intent_detected: str = Field(..., description="Detected intent")
    tools_used: list[str] = Field(default_factory=list, description="Tools used")
    steps: list[WorkflowStepResponse] = Field(default_factory=list, description="Workflow steps")
    total_duration_ms: float = Field(..., description="Total processing time")


class ChatResponse(BaseModel):
    """Chat response model with workflow trace."""

    response: str = Field(..., description="Agent's response")
    status: str = Field(default="success", description="Response status")
    provider: str = Field(..., description="LLM provider used")
    model: str = Field(..., description="Model used")
    user_id: str = Field(..., description="User ID")
    session_id: str = Field(..., description="Session ID used")
    workflow: WorkflowResponse | None = Field(None, description="Workflow trace for debugging")
    tools_used: list[str] = Field(default_factory=list, description="MCP tools used")
    duration_ms: float = Field(default=0, description="Total processing time in ms")


class NearbyRequest(BaseModel):
    """Nearby places request model."""

    lat: float = Field(..., description="Latitude", examples=[16.0626442])
    lng: float = Field(..., description="Longitude", examples=[108.2462143])
    max_distance_km: float = Field(
        default=5.0,
        description="Maximum distance in kilometers",
        examples=[5.0, 18.72],
    )
    category: str | None = Field(
        None,
        description="Category filter (cafe, restaurant, attraction, etc.)",
        examples=["cafe", "restaurant"],
    )
    limit: int = Field(default=10, description="Maximum results", examples=[10, 20])


class PlaceResponse(BaseModel):
    """Place response model."""

    place_id: str
    name: str
    category: str | None = None
    lat: float | None = None
    lng: float | None = None
    distance_km: float | None = None
    rating: float | None = None
    description: str | None = None


class NearbyResponse(BaseModel):
    """Nearby places response model."""

    places: list[PlaceResponse]
    count: int
    query: dict


class ClearHistoryRequest(BaseModel):
    """Clear history request model."""

    user_id: str = Field(..., description="User ID to clear history for")
    session_id: str | None = Field(
        None,
        description="Session ID to clear (clears all if not provided)",
    )


class HistoryResponse(BaseModel):
    """Chat history response model."""

    user_id: str
    sessions: list[str]
    current_session: str | None
    message_count: int


class MessageItem(BaseModel):
    """Single chat message."""
    role: str
    content: str
    timestamp: str


class MessagesResponse(BaseModel):
    """Chat messages response."""
    user_id: str
    session_id: str
    messages: list[MessageItem]
    count: int


@router.post(
    "/nearby",
    response_model=NearbyResponse,
    summary="Find nearby places (Neo4j)",
    description="""
Find places near a given location using Neo4j spatial query.

This endpoint directly tests the `find_nearby_places` MCP tool.

## Test Cases
- Case 1: lat=16.0626442, lng=108.2462143, max_distance_km=18.72
- Case 2: lat=16.0623184, lng=108.2306049, max_distance_km=17.94
""",
)
async def find_nearby(request: NearbyRequest) -> NearbyResponse:
    """
    Find nearby places using Neo4j graph database.

    Directly calls the find_nearby_places MCP tool.
    """
    places = await mcp_tools.find_nearby_places(
        lat=request.lat,
        lng=request.lng,
        max_distance_km=request.max_distance_km,
        category=request.category,
        limit=request.limit,
    )

    return NearbyResponse(
        places=[
            PlaceResponse(
                place_id=p.place_id,
                name=p.name,
                category=p.category,
                lat=p.lat,
                lng=p.lng,
                distance_km=p.distance_km,
                rating=p.rating,
                description=p.description,
            )
            for p in places
        ],
        count=len(places),
        query={
            "lat": request.lat,
            "lng": request.lng,
            "max_distance_km": request.max_distance_km,
            "category": request.category,
        },
    )


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Chat with LocalMate Agent",
    description="""
Chat with the Multi-Modal Contextual Agent (MMCA).

## Session Management
- Each user can have up to **3 sessions** stored
- Provide `user_id` and optional `session_id` to maintain conversation history
- History is automatically injected into the agent prompt

## LLM Providers
- **Google**: Gemini models (gemini-2.0-flash, etc.)
- **MegaLLM**: DeepSeek models (deepseek-r1-distill-llama-70b, etc.)

## Examples
- "Tìm quán cafe gần bãi biển Mỹ Khê"
- "Nhà hàng hải sản nào gần Cầu Rồng?"
""",
)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    """
    Chat endpoint with per-user history support.

    Send a natural language message, select provider and model.
    The agent will analyze your intent, query relevant data sources,
    and return a synthesized response with conversation context.
    """
    # Determine model to use
    if request.model:
        model = request.model
    elif request.provider == LLMProvider.GOOGLE:
        model = settings.default_gemini_model
    else:
        model = settings.default_megallm_model

    # Get session ID
    session_id = request.session_id or "default"

    # Get conversation history for context
    history = chat_history.get_history(
        user_id=request.user_id,
        session_id=session_id,
        max_messages=6,  # Last 3 exchanges (6 messages)
    )

    # Add user message to history
    chat_history.add_message(
        user_id=request.user_id,
        role="user",
        content=request.message,
        session_id=session_id,
    )

    # Choose agent based on react_mode
    if request.react_mode:
        # ReAct multi-step agent
        agent = ReActAgent(
            provider=request.provider.value,
            model=model,
            max_steps=request.max_steps,
        )
        response_text, agent_state = await agent.run(
            query=request.message,
            db=db,
            image_url=request.image_url,
            history=history,
        )
        
        # Convert state to workflow
        workflow = agent.to_workflow(agent_state)
        workflow_data = workflow.to_dict()
        
        # Add assistant response to history
        chat_history.add_message(
            user_id=request.user_id,
            role="assistant",
            content=response_text,
            session_id=session_id,
        )
        
        workflow_response = WorkflowResponse(
            query=workflow_data["query"],
            intent_detected=workflow_data["intent_detected"],
            tools_used=workflow_data["tools_used"],
            steps=[WorkflowStepResponse(**s) for s in workflow_data["steps"]],
            total_duration_ms=workflow_data["total_duration_ms"],
        )
        
        return ChatResponse(
            response=response_text,
            status="success",
            provider=request.provider.value,
            model=model,
            user_id=request.user_id,
            session_id=session_id,
            workflow=workflow_response,
            tools_used=workflow.tools_used,
            duration_ms=agent_state.total_duration_ms,
        )
    
    else:
        # Single-step agent (original behavior)
        agent = MMCAAgent(provider=request.provider.value, model=model)

        # Pass history to agent
        result = await agent.chat(
            message=request.message,
            db=db,
            image_url=request.image_url,
            history=history,
        )

        # Add assistant response to history
        chat_history.add_message(
            user_id=request.user_id,
            role="assistant",
            content=result.response,
            session_id=session_id,
        )

        # Build workflow response
        workflow_data = result.workflow.to_dict()
        workflow_response = WorkflowResponse(
            query=workflow_data["query"],
            intent_detected=workflow_data["intent_detected"],
            tools_used=workflow_data["tools_used"],
            steps=[WorkflowStepResponse(**s) for s in workflow_data["steps"]],
            total_duration_ms=workflow_data["total_duration_ms"],
        )

        return ChatResponse(
            response=result.response,
            status="success",
            provider=request.provider.value,
            model=model,
            user_id=request.user_id,
            session_id=session_id,
            workflow=workflow_response,
            tools_used=result.tools_used,
            duration_ms=result.total_duration_ms,
        )


@router.post(
    "/chat/clear",
    summary="Clear chat history",
    description="Clears the conversation history for a specific user/session.",
)
async def clear_chat(request: ClearHistoryRequest):
    """Clear conversation history for a user."""
    if request.session_id:
        chat_history.clear_session(request.user_id, request.session_id)
        message = f"Session '{request.session_id}' cleared for user '{request.user_id}'"
    else:
        chat_history.clear_all_sessions(request.user_id)
        message = f"All sessions cleared for user '{request.user_id}'"

    return {"status": "success", "message": message}


@router.get(
    "/chat/history/{user_id}",
    response_model=HistoryResponse,
    summary="Get chat history info",
    description="Get information about user's chat sessions.",
)
async def get_history_info(user_id: str) -> HistoryResponse:
    """Get chat history information for a user."""
    sessions = chat_history.get_session_ids(user_id)
    messages = chat_history.get_messages(user_id)

    return HistoryResponse(
        user_id=user_id,
        sessions=sessions,
        current_session="default" if "default" in sessions else (sessions[0] if sessions else None),
        message_count=len(messages),
    )


@router.get(
    "/chat/messages/{user_id}",
    response_model=MessagesResponse,
    summary="Get chat messages",
    description="Get actual chat messages from a specific session.",
)
async def get_chat_messages(
    user_id: str,
    session_id: str = "default",
) -> MessagesResponse:
    """Get chat messages for a session."""
    messages = chat_history.get_messages(user_id, session_id)
    
    return MessagesResponse(
        user_id=user_id,
        session_id=session_id,
        messages=[
            MessageItem(
                role=m.role,
                content=m.content,
                timestamp=m.timestamp.isoformat(),
            )
            for m in messages
        ],
        count=len(messages),
    )


class ImageSearchResult(BaseModel):
    """Image search result model."""

    place_id: str
    name: str
    category: str | None = None
    rating: float | None = None
    similarity: float
    matched_images: int = 1
    image_url: str | None = None


class ImageSearchResponse(BaseModel):
    """Image search response model."""

    results: list[ImageSearchResult]
    total: int


@router.post(
    "/search/image",
    response_model=ImageSearchResponse,
    summary="Search places by image",
    description="""
Upload an image to find visually similar places.

Uses image embeddings stored in Supabase pgvector.
""",
)
async def search_by_image(
    image: UploadFile = File(..., description="Image file to search"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
    db: AsyncSession = Depends(get_db),
) -> ImageSearchResponse:
    """
    Search places by uploading an image.

    Uses visual embeddings to find similar places.
    """
    try:
        # Read image bytes
        image_bytes = await image.read()

        if len(image_bytes) > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=400, detail="Image too large (max 10MB)")

        # Search using visual tool
        results = await mcp_tools.search_by_image_bytes(
            db=db,
            image_bytes=image_bytes,
            limit=limit,
        )

        return ImageSearchResponse(
            results=[
                ImageSearchResult(
                    place_id=r.place_id,
                    name=r.name,
                    category=r.category,
                    rating=r.rating,
                    similarity=r.similarity,
                    matched_images=r.matched_images,
                    image_url=r.image_url,
                )
                for r in results
            ],
            total=len(results),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image search error: {str(e)}")

