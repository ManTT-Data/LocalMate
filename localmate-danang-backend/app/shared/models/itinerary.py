"""Itinerary and ItineraryStop models."""

import uuid
from datetime import date, datetime

from sqlalchemy import ARRAY, Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class Itinerary(Base, TimestampMixin):
    """Itinerary model - represents a trip plan."""

    __tablename__ = "itineraries"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("profiles.id"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    total_days: Mapped[int] = mapped_column(Integer, nullable=False)
    total_budget: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String, default="VND")
    meta: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    stops: Mapped[list["ItineraryStop"]] = relationship(
        "ItineraryStop",
        back_populates="itinerary",
        cascade="all, delete-orphan",
    )


class ItineraryStop(Base, TimestampMixin):
    """
    ItineraryStop model - represents a stop in an itinerary.

    The place_id references a Place node in Neo4j.
    """

    __tablename__ = "itinerary_stops"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    itinerary_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("itineraries.id"),
        nullable=False,
    )
    day_index: Mapped[int] = mapped_column(Integer, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    place_id: Mapped[str] = mapped_column(String, nullable=False)  # Neo4j Place.id
    arrival_time: Mapped[datetime | None] = mapped_column(nullable=True)
    stay_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(String, nullable=True)
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    snapshot: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    itinerary: Mapped["Itinerary"] = relationship(
        "Itinerary",
        back_populates="stops",
    )
