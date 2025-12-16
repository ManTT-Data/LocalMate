"""Trip Planner Models - Pydantic schemas for Plan and PlanItem."""

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class PlaceInput(BaseModel):
    """Place data for adding to plan."""
    
    place_id: str = Field(..., description="Unique place identifier")
    name: str = Field(..., description="Place name")
    category: str = Field(default="", description="Place category")
    lat: float = Field(..., description="Latitude")
    lng: float = Field(..., description="Longitude")
    rating: Optional[float] = Field(None, description="Rating 0-5")
    description: Optional[str] = Field(None, description="Place description")


class PlanItem(BaseModel):
    """A place in the plan with order and metadata."""
    
    item_id: str = Field(..., description="Unique item identifier")
    place_id: str = Field(..., description="Reference to place")
    name: str = Field(..., description="Place name")
    category: str = Field(default="", description="Category")
    lat: float = Field(..., description="Latitude")
    lng: float = Field(..., description="Longitude")
    order: int = Field(..., description="Order in plan (1-indexed)")
    added_at: datetime = Field(default_factory=datetime.now)
    notes: Optional[str] = Field(None, description="User notes")
    rating: Optional[float] = None
    distance_from_prev_km: Optional[float] = Field(None, description="Distance from previous item")


class Plan(BaseModel):
    """A trip plan containing multiple places."""
    
    plan_id: str = Field(..., description="Unique plan identifier")
    user_id: str = Field(..., description="Owner user ID")
    name: str = Field(default="My Trip", description="Plan name")
    items: list[PlanItem] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    total_distance_km: Optional[float] = Field(None, description="Total route distance")
    estimated_duration_min: Optional[int] = Field(None, description="Estimated duration")
    is_optimized: bool = Field(default=False, description="Route has been optimized")


# Request/Response Models

class CreatePlanRequest(BaseModel):
    """Request to create a new plan."""
    
    name: str = Field(default="My Trip", description="Plan name")


class CreatePlanResponse(BaseModel):
    """Response after creating a plan."""
    
    plan_id: str
    name: str
    message: str


class AddPlaceRequest(BaseModel):
    """Request to add a place to plan."""
    
    place: PlaceInput
    notes: Optional[str] = None


class ReorderRequest(BaseModel):
    """Request to reorder places in plan."""
    
    new_order: list[str] = Field(..., description="List of item_ids in new order")


class ReplaceRequest(BaseModel):
    """Request to replace a place."""
    
    new_place: PlaceInput


class OptimizeResponse(BaseModel):
    """Response from route optimization."""
    
    plan_id: str
    items: list[PlanItem]
    total_distance_km: float
    estimated_duration_min: int
    distance_saved_km: Optional[float] = None
    message: str


class PlanResponse(BaseModel):
    """Full plan response."""
    
    plan: Plan
    message: str
