"""
Itinerary Schemas

Request/Response models cho itinerary planning
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ItineraryPlanRequest(BaseModel):
    """Request to create an itinerary plan"""
    user_id: int
    
    # Trip details
    start_date: Optional[str] = None  # YYYY-MM-DD format
    duration_days: int = Field(ge=1, le=14, description="Trip duration in days")
    
    # Group details
    family_size: int = Field(default=2, ge=1, le=20)
    
    # Preferences
    interests: List[str] = Field(default_factory=list, description="e.g., ['beach', 'seafood', 'culture']")
    budget: str = Field(default="medium", description="low, medium, high, luxury")
    
    # Starting location (optional)
    start_lat: Optional[float] = None
    start_lon: Optional[float] = None
    
    # Additional preferences
    preferred_categories: List[str] = Field(default_factory=list, description="e.g., ['restaurant', 'cafe']")
    avoid_categories: List[str] = Field(default_factory=list)
    
    # Special requirements
    special_requirements: Optional[str] = None  # Free text


class ItineraryStopResponse(BaseModel):
    """Single stop in itinerary"""
    order: int
    place_id: int
    place_name: str
    category: str
    
    arrival_time: Optional[str] = None
    departure_time: Optional[str] = None
    duration_minutes: Optional[int] = None
    
    description: Optional[str] = None
    tips: Optional[str] = None
    
    # Transport to next stop
    transport_mode: Optional[str] = None
    transport_duration_minutes: Optional[int] = None
    transport_cost: Optional[float] = None


class ItineraryPlanResponse(BaseModel):
    """Response from itinerary planning"""
    itinerary_id: int
    title: str
    description: Optional[str] = None
    
    duration_days: int
    total_stops: int
    
    stops: List[ItineraryStopResponse]
    
    # AI-generated insights
    summary: Optional[str] = None
    estimated_total_cost: Optional[float] = None


class ItineraryDetail(BaseModel):
    """Detailed itinerary information"""
    id: int
    user_id: int
    title: str
    description: Optional[str] = None
    
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    duration_days: Optional[int] = None
    
    status: str
    
    stops: List[ItineraryStopResponse]
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
