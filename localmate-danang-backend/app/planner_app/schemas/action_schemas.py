"""Action schemas for MCP suggested actions."""

import uuid
from enum import Enum

from pydantic import BaseModel


class ActionType(str, Enum):
    """Types of suggested actions."""

    BOOK_RIDE = "book_ride"
    BOOK_HOTEL = "book_hotel"
    BOOK_TICKET = "book_ticket"
    CALL_VENUE = "call_venue"
    NAVIGATE = "navigate"


class SuggestedAction(BaseModel):
    """A suggested action for the user."""

    id: uuid.UUID
    type: ActionType
    label: str
    description: str | None = None
    from_stop_index: int | None = None
    to_stop_index: int | None = None
    provider: str | None = None
    estimate_price: str | None = None
    duration_minutes: int | None = None
    deep_link: str | None = None
    params: dict | None = None


class RideActionParams(BaseModel):
    """Parameters for a ride booking action."""

    from_lat: float
    from_lng: float
    from_name: str
    to_lat: float
    to_lng: float
    to_name: str
    ride_type: str = "GrabCar"


class SuggestedActionsResponse(BaseModel):
    """Response containing suggested actions for an itinerary."""

    itinerary_id: uuid.UUID
    actions: list[SuggestedAction]
