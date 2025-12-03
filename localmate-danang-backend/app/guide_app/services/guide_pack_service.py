"""
Guide Pack Service

Business logic cho guide pack generation
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.repositories.place_repository import PlaceRepository
from app.shared.repositories.driver_repository import DriverRepository
from app.guide_app.schemas.guide_pack import (
    GuidePackRequest,
    GuidePackResponse,
    GuidePackCard,
    LanguageCard,
)
from app.guide_app.agents.guide_agent import guide_agent
from app.shared.core.logging import get_logger
from app.shared.core.exceptions import raise_not_found

logger = get_logger(__name__)


class GuidePackService:
    """Service layer for guide pack operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.place_repo = PlaceRepository(db)
        self.driver_repo = DriverRepository(db)
    
    async def generate_guide_pack(
        self,
        request: GuidePackRequest,
    ) -> GuidePackResponse:
        """
        Generate guide pack for driver
        """
        logger.info(f"Generating guide pack for driver {request.driver_id}")
        
        # Step 1: Get driver info
        driver = await self.driver_repo.get_by_user_id(request.driver_id)
        
        # Step 2: Determine current place
        if request.current_place_id:
            place = await self.place_repo.get(request.current_place_id)
        elif request.current_lat and request.current_lon:
            # Find nearest place
            nearby_places = await self.place_repo.get_nearby_simple(
                request.current_lat,
                request.current_lon,
                radius_km=1.0,
                limit=1,
            )
            place = nearby_places[0] if nearby_places else None
        else:
            place = None
        
        if not place:
            raise_not_found("No place found for the given location")
        
        # Step 3: Generate guide pack using AI agent
        agent_result = await guide_agent.generate_guide_pack(
            place_id=place.id,
            place_name=place.name,
            latitude=place.latitude,
            longitude=place.longitude,
            passenger_language=request.passenger_language,
            include_fun_facts=request.include_fun_facts,
        )
        
        # Step 4: Convert to response schema
        cards = [
            GuidePackCard(
                card_type=card["card_type"],
                title=card["title"],
                content=card["content"],
                place_name=card.get("place_name"),
                language_phrases=LanguageCard(**card["language_phrases"]) if "language_phrases" in card else None,
            )
            for card in agent_result["cards"]
        ]
        
        # Convert language cards
        quick_phrases = [
            LanguageCard(**phrase)
            for phrase in agent_result["quick_phrases"]
        ]
        
        # Step 5: Get nearby attractions
        nearby = await self.place_repo.get_nearby_simple(
            place.latitude,
            place.longitude,
            radius_km=2.0,
            limit=5,
        )
        nearby_names = [p.name for p in nearby if p.id != place.id]
        
        return GuidePackResponse(
            trip_id=request.trip_id,
            driver_id=request.driver_id,
            current_place=place.name,
            nearby_attractions=nearby_names,
            cards=cards,
            driver_summary=agent_result["driver_summary"],
            quick_phrases=quick_phrases,
        )


# This service would typically be used by the API routes
