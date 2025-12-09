"""Semantic search service using embeddings and pgvector."""

from dataclasses import dataclass

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.integrations.embedding_client import embedding_client
from app.shared.models.embedding import PlaceEmbedding


@dataclass
class SemanticSearchResult:
    """Result from semantic search."""

    place_id: str
    similarity: float
    metadata: dict | None


class SemanticSearchService:
    """Service for semantic search using embeddings."""

    async def search_by_text(
        self,
        db: AsyncSession,
        query: str,
        limit: int = 10,
        threshold: float = 0.7,
    ) -> list[SemanticSearchResult]:
        """
        Search places by text query using semantic similarity.

        Args:
            db: Database session
            query: Text query
            limit: Maximum results
            threshold: Minimum similarity threshold

        Returns:
            List of search results ordered by similarity
        """
        # Generate embedding for query
        query_embedding = await embedding_client.embed_text(query)

        # Search using pgvector
        results = await db.execute(
            text("""
                SELECT 
                    place_id,
                    1 - (text_embedding <=> :embedding::vector) as similarity,
                    place_metadata
                FROM place_embeddings
                WHERE 1 - (text_embedding <=> :embedding::vector) > :threshold
                ORDER BY text_embedding <=> :embedding::vector
                LIMIT :limit
            """),
            {
                "embedding": str(query_embedding),
                "threshold": threshold,
                "limit": limit,
            },
        )

        return [
            SemanticSearchResult(
                place_id=row.place_id,
                similarity=row.similarity,
                metadata=row.place_metadata,
            )
            for row in results.fetchall()
        ]

    async def search_by_image(
        self,
        db: AsyncSession,
        image_url: str,
        limit: int = 10,
        threshold: float = 0.7,
    ) -> list[SemanticSearchResult]:
        """
        Search places by image similarity.

        Args:
            db: Database session
            image_url: URL of query image
            limit: Maximum results
            threshold: Minimum similarity

        Returns:
            List of search results
        """
        # Generate image embedding
        image_embedding = await embedding_client.embed_image(image_url)
        if not image_embedding:
            return []

        results = await db.execute(
            text("""
                SELECT 
                    place_id,
                    1 - (image_embedding <=> :embedding::vector) as similarity,
                    place_metadata
                FROM place_embeddings
                WHERE image_embedding IS NOT NULL
                  AND 1 - (image_embedding <=> :embedding::vector) > :threshold
                ORDER BY image_embedding <=> :embedding::vector
                LIMIT :limit
            """),
            {
                "embedding": str(image_embedding),
                "threshold": threshold,
                "limit": limit,
            },
        )

        return [
            SemanticSearchResult(
                place_id=row.place_id,
                similarity=row.similarity,
                metadata=row.place_metadata,
            )
            for row in results.fetchall()
        ]

    async def upsert_embedding(
        self,
        db: AsyncSession,
        place_id: str,
        text_content: str | None = None,
        image_url: str | None = None,
        metadata: dict | None = None,
    ) -> PlaceEmbedding:
        """
        Create or update embedding for a place.

        Args:
            db: Database session
            place_id: Place ID from Neo4j
            text_content: Text to embed
            image_url: Image URL to embed
            metadata: Place metadata to store

        Returns:
            Created/updated PlaceEmbedding
        """
        # Check if exists
        result = await db.execute(
            select(PlaceEmbedding).where(PlaceEmbedding.place_id == place_id)
        )
        embedding = result.scalar_one_or_none()

        # Generate embeddings
        text_emb = None
        image_emb = None

        if text_content:
            text_emb = await embedding_client.embed_text(text_content)
        if image_url:
            image_emb = await embedding_client.embed_image(image_url)

        if embedding:
            # Update existing
            if text_emb:
                embedding.text_embedding = text_emb
            if image_emb:
                embedding.image_embedding = image_emb
            if metadata:
                embedding.place_metadata = metadata
        else:
            # Create new
            embedding = PlaceEmbedding(
                place_id=place_id,
                text_embedding=text_emb,
                image_embedding=image_emb,
                place_metadata=metadata,
            )
            db.add(embedding)

        await db.commit()
        await db.refresh(embedding)
        return embedding


# Singleton instance
semantic_search_service = SemanticSearchService()
