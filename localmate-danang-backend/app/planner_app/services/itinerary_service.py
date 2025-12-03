"""
Itinerary Service

Business logic cho itinerary planning
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.repositories.itinerary_repository import ItineraryRepository
from app.planner_app.schemas.itinerary import (
    ItineraryPlanRequest,
    ItineraryPlanResponse,
    ItineraryStopResponse,
    ItineraryDetail,
)
from app.planner_app.agents.planner_agent import planner_agent
from app.shared.core.logging import get_logger

logger = get_logger(__name__)


class ItineraryService:
    """Service layer for itinerary operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ItineraryRepository(db)
    
    async def create_itinerary_plan(
        self,
        request: ItineraryPlanRequest,
    ) -> ItineraryPlanResponse:
        """
        Create a new itinerary using Planner Agent
        """
        logger.info(f"Creating itinerary for user {request.user_id}")
        
        # Step 1: Generate itinerary using AI agent
        agent_result = await planner_agent.create_itinerary(
            duration_days=request.duration_days,
            interests=request.interests,
            budget=request.budget,
            family_size=request.family_size,
            start_lat=request.start_lat or 16.0544,
            start_lon=request.start_lon or 108.2022,
        )
        
        # Step 2: Save to database
        itinerary_data = {
            "user_id": request.user_id,
            "title": agent_result["title"],
            "description": agent_result["description"],
            "duration_days": request.duration_days,
            "budget_total": agent_result.get("estimated_cost"),
            "preferences": {
                "interests": request.interests,
                "budget": request.budget,
                "family_size": request.family_size,
            },
            "status": "draft",
        }
        
        stops_data = [
            {
                "place_id": stop["place_id"],
                "order": stop["order"],
                "duration_minutes": stop.get("duration_minutes"),
                "description": stop.get("description"),
                "tips": stop.get("tips"),
                "transport_mode": stop.get("transport_mode"),
                "transport_duration_minutes": stop.get("transport_duration_minutes"),
            }
            for stop in agent_result["stops"]
        ]
        
        itinerary = await self.repo.create_with_stops(itinerary_data, stops_data)
        
        # Step 3: Convert to response schema
        return ItineraryPlanResponse(
            itinerary_id=itinerary.id,
            title=itinerary.title,
            description=itinerary.description,
            duration_days=itinerary.duration_days,
            total_stops=len(agent_result["stops"]),
            stops=[
                ItineraryStopResponse(**stop)
                for stop in agent_result["stops"]
            ],
            summary=agent_result.get("summary"),
            estimated_total_cost=agent_result.get("estimated_cost"),
        )
    
    async def get_itinerary_detail(self, itinerary_id: int) -> Optional[ItineraryDetail]:
        """Get itinerary details"""
        itinerary = await self.repo.get_with_stops(itinerary_id)
        
        if not itinerary:
            return None
        
        # Convert stops to response format
        stops = [
            ItineraryStopResponse(
                order=stop.order,
                place_id=stop.place_id,
                place_name="Place Name",  # TODO: Join with Place model
                category="Category",
                arrival_time=stop.arrival_time.isoformat() if stop.arrival_time else None,
                departure_time=stop.departure_time.isoformat() if stop.departure_time else None,
                duration_minutes=stop.duration_minutes,
                description=stop.description,
                tips=stop.tips,
                transport_mode=stop.transport_mode,
                transport_duration_minutes=stop.transport_duration_minutes,
                transport_cost=stop.transport_cost,
            )
            for stop in sorted(itinerary.stops, key=lambda x: x.order)
        ]
        
        return ItineraryDetail(
            id=itinerary.id,
            user_id=itinerary.user_id,
            title=itinerary.title,
            description=itinerary.description,
            start_date=itinerary.start_date.isoformat() if itinerary.start_date else None,
            end_date=itinerary.end_date.isoformat() if itinerary.end_date else None,
            duration_days=itinerary.duration_days,
            status=itinerary.status,
            stops=stops,
            created_at=itinerary.created_at,
            updated_at=itinerary.updated_at,
        )
    
    async def get_user_itineraries(
        self,
        user_id: int,
        status: Optional[str] = None,
    ) -> List[ItineraryDetail]:
        """Get all itineraries for a user"""
        itineraries = await self.repo.get_by_user(user_id, status)
        
        # Convert to response format (without stops for list view)
        results = []
        for itinerary in itineraries:
            # Load stops for each
            full_itinerary = await self.repo.get_with_stops(itinerary.id)
            if full_itinerary:
                detail = await self.get_itinerary_detail(full_itinerary.id)
                if detail:
                    results.append(detail)
        
        return results
