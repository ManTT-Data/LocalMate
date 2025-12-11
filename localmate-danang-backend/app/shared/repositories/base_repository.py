"""Base repository with common CRUD operations."""

from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic base repository for CRUD operations."""

    def __init__(self, model: type[ModelType]):
        """Initialize with model class."""
        self.model = model

    async def get_by_id(
        self,
        db: AsyncSession,
        id: UUID,
    ) -> ModelType | None:
        """Get a record by ID."""
        result = await db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        db: AsyncSession,
        obj: ModelType,
    ) -> ModelType:
        """Create a new record."""
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def delete(
        self,
        db: AsyncSession,
        obj: ModelType,
    ) -> None:
        """Delete a record."""
        await db.delete(obj)
        await db.commit()
