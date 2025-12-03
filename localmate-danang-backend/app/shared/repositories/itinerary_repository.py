"""
Itinerary Repository

Specific queries for Itinerary model
"""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.models.itinerary import Itinerary, ItineraryStop
from app.shared.repositories.base import BaseRepository


class ItineraryRepository(BaseRepository[Itinerary]):
    """Repository for Itinerary model"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Itinerary, db)
    
    async def get_with_stops(self, id: int) -> Optional[Itinerary]:
        """Get itinerary with all stops loaded"""
        result = await self.db.execute(
            select(Itinerary)
            .where(Itinerary.id == id)
            .options(selectinload(Itinerary.stops))
        )
        return result.scalar_one_or_none()
    
    async def get_by_user(
        self,
        user_id: int,
        status: Optional[str] = None,
        limit: int = 20,
    ) -> List[Itinerary]:
        """Get itineraries for a user"""
        query = select(Itinerary).where(Itinerary.user_id == user_id)
        
        if status:
            query = query.where(Itinerary.status == status)
        
        query = query.order_by(Itinerary.created_at.desc()).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def create_with_stops(
        self,
        itinerary_data: dict,
        stops_data: List[dict],
    ) -> Itinerary:
        """Create itinerary with stops in a single transaction"""
        itinerary = Itinerary(**itinerary_data)
        self.db.add(itinerary)
        await self.db.flush()
        
        # Create stops
        for stop_data in stops_data:
            stop = ItineraryStop(**stop_data, itinerary_id=itinerary.id)
            self.db.add(stop)
        
        await self.db.flush()
        await self.db.refresh(itinerary)
        return await self.get_with_stops(itinerary.id)
