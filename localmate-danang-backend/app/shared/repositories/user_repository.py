"""
User Repository

Specific queries for User model
"""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.models.user import User
from app.shared.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User model"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_by_role(self, role: str, limit: int = 100) -> list[User]:
        """Get users by role"""
        result = await self.db.execute(
            select(User).where(User.role == role).limit(limit)
        )
        return list(result.scalars().all())
