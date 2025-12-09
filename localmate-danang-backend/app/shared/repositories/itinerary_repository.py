"""Itinerary repository for database operations."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.shared.models.itinerary import Itinerary, ItineraryStop

from .base_repository import BaseRepository


class ItineraryRepository(BaseRepository[Itinerary]):
    """Repository for Itinerary CRUD operations."""

    def __init__(self):
        """Initialize with Itinerary model."""
        super().__init__(Itinerary)

    async def create_with_stops(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        title: str,
        total_days: int,
        currency: str,
        meta: dict | None,
        stops: list[dict],
    ) -> Itinerary:
        """
        Create an itinerary with its stops in a single transaction.

        Args:
            db: Database session
            user_id: Owner's user ID
            title: Itinerary title
            total_days: Number of days
            currency: Currency code
            meta: Additional metadata
            stops: List of stop dictionaries

        Returns:
            Created Itinerary with stops
        """
        # Create itinerary
        itinerary = Itinerary(
            user_id=user_id,
            title=title,
            total_days=total_days,
            currency=currency,
            meta=meta,
        )
        db.add(itinerary)
        await db.flush()  # Get itinerary.id

        # Create stops
        for stop_data in stops:
            stop = ItineraryStop(
                itinerary_id=itinerary.id,
                day_index=stop_data["day_index"],
                order_index=stop_data["order_index"],
                place_id=stop_data["place_id"],
                stay_minutes=stop_data.get("stay_minutes"),
                snapshot=stop_data.get("snapshot"),
            )
            db.add(stop)

        await db.commit()
        await db.refresh(itinerary)
        return itinerary

    async def get_with_stops(
        self,
        db: AsyncSession,
        itinerary_id: uuid.UUID,
    ) -> Itinerary | None:
        """
        Get an itinerary with its stops eagerly loaded.

        Args:
            db: Database session
            itinerary_id: Itinerary ID

        Returns:
            Itinerary with stops or None
        """
        result = await db.execute(
            select(Itinerary)
            .options(selectinload(Itinerary.stops))
            .where(Itinerary.id == itinerary_id)
        )
        return result.scalar_one_or_none()

    async def get_user_itineraries(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        limit: int = 20,
    ) -> list[Itinerary]:
        """Get all itineraries for a user."""
        result = await db.execute(
            select(Itinerary)
            .where(Itinerary.user_id == user_id)
            .order_by(Itinerary.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())


# Singleton instance
itinerary_repository = ItineraryRepository()
