"""Profile model - linked to Supabase auth.users."""

import uuid

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class Profile(Base, TimestampMixin):
    """
    User profile model.

    This table is linked to Supabase auth.users table.
    The id column references auth.users(id).
    """

    __tablename__ = "profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str | None] = mapped_column(String, nullable=True)
    role: Mapped[str] = mapped_column(String, nullable=False, default="tourist")
    locale: Mapped[str] = mapped_column(String, default="vi_VN")
    avatar_url: Mapped[str | None] = mapped_column(String, nullable=True)
