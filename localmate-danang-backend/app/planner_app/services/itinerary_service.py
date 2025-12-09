"""Itinerary service - orchestrates planning and persistence."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.planner_app.agents.planner_agent import planner_agent
from app.planner_app.schemas.itinerary_schemas import (
    ItineraryPlanRequest,
    ItineraryPlanResponse,
    ItineraryStopResponse,
)
from app.shared.repositories.itinerary_repository import itinerary_repository


class ItineraryService:
    """Service for itinerary operations."""

    async def create_itinerary_plan(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        request: ItineraryPlanRequest,
    ) -> ItineraryPlanResponse:
        """
        Create a new itinerary plan.

        Flow:
        1. Call planner_agent to generate plan
        2. Save to database
        3. Return response

        Args:
            db: Database session
            user_id: Owner's user ID
            request: Planning request

        Returns:
            Created itinerary response
        """
        # 1. Generate plan
        result = await planner_agent.create_itinerary(request)

        # 2. Prepare stops data
        stops_data = [
            {
                "day_index": stop.day_index,
                "order_index": stop.order_index,
                "place_id": stop.place_id,
                "stay_minutes": 60,  # Default 1 hour
                "snapshot": stop.snapshot,
            }
            for stop in result.stops
        ]

        # 3. Save to database
        itinerary = await itinerary_repository.create_with_stops(
            db=db,
            user_id=user_id,
            title=result.title,
            total_days=result.total_days,
            currency=result.currency,
            meta={"interests": request.interests, "budget": request.budget},
            stops=stops_data,
        )

        # 4. Fetch with stops for response
        itinerary = await itinerary_repository.get_with_stops(db, itinerary.id)

        return self._to_response(itinerary)

    async def get_itinerary(
        self,
        db: AsyncSession,
        itinerary_id: uuid.UUID,
    ) -> ItineraryPlanResponse | None:
        """
        Get an itinerary by ID.

        Args:
            db: Database session
            itinerary_id: Itinerary ID

        Returns:
            Itinerary response or None
        """
        itinerary = await itinerary_repository.get_with_stops(db, itinerary_id)
        if not itinerary:
            return None
        return self._to_response(itinerary)

    async def get_user_itineraries(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> list[ItineraryPlanResponse]:
        """Get all itineraries for a user."""
        itineraries = await itinerary_repository.get_user_itineraries(db, user_id)
        return [self._to_response(it) for it in itineraries]

    def _to_response(self, itinerary) -> ItineraryPlanResponse:
        """Map database model to response schema."""
        return ItineraryPlanResponse(
            id=itinerary.id,
            user_id=itinerary.user_id,
            title=itinerary.title,
            total_days=itinerary.total_days,
            currency=itinerary.currency,
            created_at=itinerary.created_at,
            stops=[
                ItineraryStopResponse(
                    id=stop.id,
                    day_index=stop.day_index,
                    order_index=stop.order_index,
                    place_id=stop.place_id,
                    arrival_time=stop.arrival_time,
                    stay_minutes=stop.stay_minutes,
                    snapshot=stop.snapshot,
                )
                for stop in sorted(
                    itinerary.stops,
                    key=lambda s: (s.day_index, s.order_index),
                )
            ],
        )


# Singleton instance
itinerary_service = ItineraryService()
