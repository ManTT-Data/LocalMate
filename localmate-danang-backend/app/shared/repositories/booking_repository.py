"""
Booking Repository

Specific queries for Booking model
"""

from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.models.booking import Booking
from app.shared.repositories.base import BaseRepository


class BookingRepository(BaseRepository[Booking]):
    """Repository for Booking model"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Booking, db)
    
    async def get_by_user(self, user_id: int, limit: int = 50) -> List[Booking]:
        """Get bookings for a user"""
        result = await self.db.execute(
            select(Booking)
            .where(Booking.user_id == user_id)
            .order_by(Booking.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_by_itinerary(self, itinerary_id: int) -> List[Booking]:
        """Get bookings for an itinerary"""
        result = await self.db.execute(
            select(Booking).where(Booking.itinerary_id == itinerary_id)
        )
        return list(result.scalars().all())
    
    async def get_by_external_id(self, external_id: str) -> Booking | None:
        """Get booking by external provider ID"""
        result = await self.db.execute(
            select(Booking).where(Booking.external_id == external_id)
        )
        return result.scalar_one_or_none()
