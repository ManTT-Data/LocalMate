"""Guide Router - API endpoints for Guide Pack features."""

from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.guide_app.agents.guide_agent import guide_agent
from app.guide_app.schemas.guide_schemas import (
    FunFactRequest,
    FunFactResponse,
    GuideContentRequest,
    GuideContentResponse,
    LanguageCardRequest,
    LanguageCardResponse,
    LocalTipRequest,
    LocalTipResponse,
)

router = APIRouter()


@router.post("/fun-fact", response_model=FunFactResponse)
async def get_fun_fact(
    request: FunFactRequest,
    _: dict = Depends(get_current_user),
):
    """
    Get a fun fact about a place.

    - **place_id**: Place identifier from Neo4j
    - **locale**: Response locale (default: vi_VN)
    """
    return await guide_agent.generate_fun_fact(
        place_id=request.place_id,
    )


@router.post("/tips", response_model=LocalTipResponse)
async def get_local_tips(
    request: LocalTipRequest,
    _: dict = Depends(get_current_user),
):
    """
    Get local tips for a place.

    - **place_id**: Place identifier
    - **category**: Optional tip category (food, transport, culture)
    - **locale**: Response locale
    """
    return await guide_agent.generate_local_tips(
        place_id=request.place_id,
        category=request.category,
    )


@router.post("/language-card", response_model=LanguageCardResponse)
async def get_language_card(
    request: LanguageCardRequest,
    _: dict = Depends(get_current_user),
):
    """
    Get a Vietnamese language learning card.

    - **phrase_type**: Type of phrase (greeting, ordering, directions, emergency)
    - **locale**: Response locale
    """
    return await guide_agent.generate_language_card(
        phrase_type=request.phrase_type,
    )


@router.post("/content", response_model=GuideContentResponse)
async def get_guide_content(
    request: GuideContentRequest,
    _: dict = Depends(get_current_user),
):
    """
    Get all guide content for a place.

    - **place_id**: Place identifier
    - **content_types**: Optional list of content to include (facts, tips, phrases)
    - **locale**: Response locale
    """
    return await guide_agent.generate_guide_content(
        place_id=request.place_id,
        content_types=request.content_types,
    )
