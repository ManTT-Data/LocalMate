"""Guide Router - single content endpoint."""

from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.guide_app.agents.guide_agent import guide_agent
from app.guide_app.schemas.guide_schemas import (
    GuideContentRequest,
    GuideContentResponse,
)

router = APIRouter()


@router.post("/content", response_model=GuideContentResponse)
async def get_guide_content(
    request: GuideContentRequest,
    _: dict = Depends(get_current_user),
):
    """
    Get full guide content for a place.

    Returns fun facts, tips, best time to visit, suggested duration, and highlights.

    - **place_id**: Place identifier from Neo4j
    - **place_name**: Optional place name (will fetch from DB if not provided)
    """
    result = await guide_agent.generate_guide_content(
        place_id=request.place_id,
        place_name=request.place_name,
    )
    return GuideContentResponse(**result)
