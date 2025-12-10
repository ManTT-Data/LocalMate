"""Pydantic schemas for Guide Pack API."""

from pydantic import BaseModel


class GuideContentRequest(BaseModel):
    """Request for guide content for a place."""

    place_id: str
    place_name: str | None = None


class GuideContentResponse(BaseModel):
    """Response with full guide content."""

    place_id: str
    place_name: str
    category: str
    rating: float
    fun_fact: str
    tips: list[str]
    best_time_to_visit: str
    suggested_duration: str
    highlights: list[str]
