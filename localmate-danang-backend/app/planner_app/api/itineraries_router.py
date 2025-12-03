"""
Itinerary Routes

API endpoints cho travel planning
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.db.session import get_db
from app.planner_app.schemas.itinerary import (
    ItineraryPlanRequest,
    ItineraryPlanResponse,
    ItineraryDetail,
)
from app.planner_app.services.itinerary_service import ItineraryService

router = APIRouter()


@router.post("/plan", response_model=ItineraryPlanResponse)
async def create_itinerary_plan(
    request: ItineraryPlanRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new travel itinerary plan using AI
    
    This endpoint uses the Planner Agent to generate a personalized
    itinerary based on user preferences, budget, and interests.
    """
    service = ItineraryService(db)
    itinerary = await service.create_itinerary_plan(request)
    return itinerary


@router.get("/{itinerary_id}", response_model=ItineraryDetail)
async def get_itinerary(
    itinerary_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get itinerary details by ID"""
    service = ItineraryService(db)
    itinerary = await service.get_itinerary_detail(itinerary_id)
    
    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary not found")
    
    return itinerary


@router.get("/user/{user_id}", response_model=List[ItineraryDetail])
async def get_user_itineraries(
    user_id: int,
    status: str = None,
    db: AsyncSession = Depends(get_db),
):
    """Get all itineraries for a user"""
    service = ItineraryService(db)
    itineraries = await service.get_user_itineraries(user_id, status)
    return itineraries
