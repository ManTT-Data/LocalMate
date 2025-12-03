"""
Driver Guide Routes

API endpoints for driver guide pack generation
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.db.session import get_db
from app.guide_app.schemas.guide_pack import GuidePackRequest, GuidePackResponse
from app.guide_app.services.guide_pack_service import GuidePackService

router = APIRouter()


@router.post("/generate", response_model=GuidePackResponse)
async def generate_guide_pack(
    request: GuidePackRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a Guide Pack for a driver's current trip
    
    This provides:
    - Place information
    - Fun facts and local stories
    - Quick phrases in passenger's language
    - Optional affiliate suggestions
    """
    service = GuidePackService(db)
    guide_pack = await service.generate_guide_pack(request)
    return guide_pack


@router.get("/trip/{trip_id}", response_model=GuidePackResponse)
async def get_guide_pack_for_trip(
    trip_id: str,
    driver_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get guide pack for a specific trip"""
    service = GuidePackService(db)
    request = GuidePackRequest(
        driver_id=driver_id,
        trip_id=trip_id,
        current_place_id=None,  # Will be loaded from trip
        passenger_language="en",
    )
    guide_pack = await service.generate_guide_pack(request)
    return guide_pack
