"""Itineraries router - API endpoints for itinerary operations."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user, get_current_user_id
from app.planner_app.schemas.itinerary_schemas import (
    ItineraryPlanRequest,
    ItineraryPlanResponse,
)
from app.planner_app.services.itinerary_service import itinerary_service
from app.shared.db.session import get_db

router = APIRouter()


@router.post("/plan", response_model=ItineraryPlanResponse)
async def plan_itinerary(
    request: ItineraryPlanRequest,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    """
    Create a new itinerary plan.

    - **duration_days**: Number of travel days (required, >= 1)
    - **interests**: List of interests like ['beach', 'seafood', 'coffee']
    - **budget**: Budget level: 'low', 'medium', 'high'
    - **family_size**: Number of travelers
    """
    return await itinerary_service.create_itinerary_plan(db, user_id, request)


@router.get("/{itinerary_id}", response_model=ItineraryPlanResponse)
async def get_itinerary(
    itinerary_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user),  # Auth required
):
    """Get an itinerary by ID."""
    result = await itinerary_service.get_itinerary(db, itinerary_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Itinerary not found",
        )
    return result


@router.get("/", response_model=list[ItineraryPlanResponse])
async def list_itineraries(
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    """List all itineraries for the current user."""
    return await itinerary_service.get_user_itineraries(db, user_id)
