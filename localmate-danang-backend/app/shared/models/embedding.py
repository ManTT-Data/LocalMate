"""PlaceEmbedding model for semantic search."""

import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class PlaceEmbedding(Base, TimestampMixin):
    """
    Place embedding model for semantic search.

    Stores vector embeddings for places from Neo4j.
    - text_embedding: 768-dim from text-embedding-004
    - image_embedding: 512-dim from CLIP
    """

    __tablename__ = "place_embeddings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    place_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    text_embedding: Mapped[list[float] | None] = mapped_column(
        Vector(768),
        nullable=True,
    )
    image_embedding: Mapped[list[float] | None] = mapped_column(
        Vector(512),
        nullable=True,
    )
    place_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
