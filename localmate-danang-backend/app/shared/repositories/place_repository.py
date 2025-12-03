"""
Place Repository

Specific queries for Place model
"""

from typing import List, Optional
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.models.place import Place
from app.shared.repositories.base import BaseRepository


class PlaceRepository(BaseRepository[Place]):
    """Repository for Place model"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Place, db)
    
    async def get_by_category(self, category: str, limit: int = 100) -> List[Place]:
        """Get places by category"""
        result = await self.db.execute(
            select(Place).where(Place.category == category).limit(limit)
        )
        return list(result.scalars().all())
    
    async def search_by_name(self, name: str, limit: int = 20) -> List[Place]:
        """Search places by name (case-insensitive)"""
        result = await self.db.execute(
            select(Place)
            .where(
                or_(
                    Place.name.ilike(f"%{name}%"),
                    Place.name_vi.ilike(f"%{name}%")
                )
            )
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_by_tags(self, tags: List[str], limit: int = 50) -> List[Place]:
        """Get places that have any of the given tags"""
        result = await self.db.execute(
            select(Place)
            .where(Place.tags.overlap(tags))
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_nearby_simple(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 5.0,
        limit: int = 50,
    ) -> List[Place]:
        """
        Get places near a location using bounding box
        (Simple version - for accurate distance, use geo utils or Neo4j)
        """
        # Rough approximation: 1 degree ≈ 111 km
        lat_delta = radius_km / 111
        lon_delta = radius_km / (111 * abs(0.98))  # Adjust for latitude
        
        result = await self.db.execute(
            select(Place)
            .where(
                and_(
                    Place.latitude.between(latitude - lat_delta, latitude + lat_delta),
                    Place.longitude.between(longitude - lon_delta, longitude + lon_delta),
                )
            )
            .limit(limit)
        )
        return list(result.scalars().all())
