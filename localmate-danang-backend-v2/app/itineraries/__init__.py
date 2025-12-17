"""Itineraries models."""

from datetime import datetime, date
from pydantic import BaseModel, Field


class StopBase(BaseModel):
    """Base stop fields."""
    place_id: str = Field(..., description="Place ID from places_metadata")
    day_index: int = Field(..., ge=1, description="Day number (1-indexed)")
    order_index: int = Field(..., ge=1, description="Order within the day")
    arrival_time: datetime | None = Field(None, description="Planned arrival time")
    stay_minutes: int | None = Field(None, description="Duration in minutes")
    notes: str | None = Field(None, description="User notes")
    tags: list[str] = Field(default_factory=list, description="Tags")


class StopCreate(StopBase):
    """Create stop request."""
    snapshot: dict | None = Field(None, description="Place snapshot (name, category, etc.) - optional, will be fetched from DB if not provided")


class StopUpdate(BaseModel):
    """Update stop - all optional."""
    day_index: int | None = None
    order_index: int | None = None
    arrival_time: datetime | None = None
    stay_minutes: int | None = None
    notes: str | None = None
    tags: list[str] | None = None


class Stop(StopBase):
    """Full stop with metadata."""
    id: str
    itinerary_id: str
    # Snapshot from places_metadata
    snapshot: dict | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ItineraryBase(BaseModel):
    """Base itinerary fields."""
    title: str = Field(..., description="Itinerary title")
    start_date: date | None = Field(None, description="Start date")
    end_date: date | None = Field(None, description="End date")
    total_days: int = Field(..., ge=1, description="Total trip days")
    total_budget: float | None = Field(None, description="Budget amount")
    currency: str = Field(default="VND", description="Currency code")


class ItineraryCreate(ItineraryBase):
    """Create itinerary request."""
    pass


class ItineraryUpdate(BaseModel):
    """Update itinerary - all optional."""
    title: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    total_days: int | None = None
    total_budget: float | None = None
    currency: str | None = None


class Itinerary(ItineraryBase):
    """Full itinerary with stops."""
    id: str
    user_id: str
    stops: list[Stop] = Field(default_factory=list)
    meta: dict | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ItineraryListItem(BaseModel):
    """Summary for list view."""
    id: str
    title: str
    start_date: date | None
    end_date: date | None
    total_days: int
    stop_count: int
    created_at: datetime


class ItineraryResponse(BaseModel):
    """API response wrapper."""
    itinerary: Itinerary
    message: str = "Success"


class StopResponse(BaseModel):
    """API response for stop."""
    stop: Stop
    message: str = "Success"
