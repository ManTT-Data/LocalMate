"""Pydantic schemas for Itinerary API."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


class ItineraryPlanRequest(BaseModel):
    """Request schema for creating a new itinerary plan."""

    duration_days: int = Field(ge=1, description="Number of travel days")
    family_size: int | None = Field(default=None, description="Number of travelers")
    interests: list[str] | None = Field(
        default=None,
        description="List of interests, e.g. ['beach', 'seafood', 'coffee']",
    )
    budget: str | None = Field(
        default=None,
        description="Budget level: 'low', 'medium', 'high'",
    )
    start_date: date | None = Field(default=None, description="Trip start date")
    start_location_lat: float | None = Field(
        default=None,
        description="Starting location latitude",
    )
    start_location_lng: float | None = Field(
        default=None,
        description="Starting location longitude",
    )


class ItineraryStopResponse(BaseModel):
    """Response schema for a single stop in an itinerary."""

    id: uuid.UUID
    day_index: int
    order_index: int
    place_id: str
    arrival_time: datetime | None = None
    stay_minutes: int | None = None
    snapshot: dict | None = None

    class Config:
        from_attributes = True


class ItineraryPlanResponse(BaseModel):
    """Response schema for a complete itinerary plan."""

    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    total_days: int
    currency: str
    created_at: datetime
    stops: list[ItineraryStopResponse]

    class Config:
        from_attributes = True
