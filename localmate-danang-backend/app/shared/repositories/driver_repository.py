"""
Driver Repository

Specific queries for DriverProfile model
"""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.models.driver import DriverProfile
from app.shared.repositories.base import BaseRepository


class DriverRepository(BaseRepository[DriverProfile]):
    """Repository for DriverProfile model"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(DriverProfile, db)
    
    async def get_by_user_id(self, user_id: int) -> Optional[DriverProfile]:
        """Get driver profile by user ID"""
        result = await self.db.execute(
            select(DriverProfile).where(DriverProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_grab_id(self, grab_driver_id: str) -> Optional[DriverProfile]:
        """Get driver profile by Grab driver ID"""
        result = await self.db.execute(
            select(DriverProfile).where(DriverProfile.grab_driver_id == grab_driver_id)
        )
        return result.scalar_one_or_none()
