"""Visual RAG Tool - Image similarity search using CLIP embeddings."""

from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.integrations.embedding_client import embedding_client


@dataclass
class ImageSearchResult:
    """Result from visual similarity search."""

    place_id: str
    similarity: float
    metadata: dict | None


# Tool definition for agent
TOOL_DEFINITION = {
    "name": "retrieve_similar_visuals",
    "description": "Tìm địa điểm có hình ảnh tương tự. Dùng khi người dùng gửi ảnh hoặc mô tả về không gian, decor.",
    "parameters": {
        "image_url": "URL của ảnh cần tìm kiếm tương tự",
        "limit": "Số kết quả tối đa (mặc định 10)",
    },
}


async def retrieve_similar_visuals(
    db: AsyncSession,
    image_url: str,
    limit: int = 10,
    threshold: float = 0.6,
) -> list[ImageSearchResult]:
    """
    RAG Image - Visual similarity search.

    Uses CLIP embeddings (512-dim) to find places with similar
    visual characteristics.

    Args:
        db: Database session
        image_url: URL of the query image
        limit: Maximum results
        threshold: Minimum similarity threshold

    Returns:
        List of places with visual similarity scores
    """
    # Generate image embedding using CLIP
    image_embedding = await embedding_client.embed_image(image_url)
    if not image_embedding:
        return []

    # Search using pgvector cosine similarity on image embeddings
    results = await db.execute(
        text("""
            SELECT 
                place_id,
                1 - (image_embedding <=> :embedding::vector) as similarity,
                metadata as place_metadata
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
        ImageSearchResult(
            place_id=row.place_id,
            similarity=row.similarity,
            metadata=row.place_metadata,
        )
        for row in results.fetchall()
    ]
