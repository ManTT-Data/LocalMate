"""Text RAG Tool - Semantic search in text descriptions using pgvector."""

from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.integrations.embedding_client import embedding_client


@dataclass
class TextSearchResult:
    """Result from text context search."""

    place_id: str
    similarity: float
    metadata: dict | None


# Tool definition for agent
TOOL_DEFINITION = {
    "name": "retrieve_context_text",
    "description": "Tìm kiếm thông tin chi tiết, mô tả, đánh giá từ văn bản. Dùng khi người dùng hỏi về menu, review, mô tả địa điểm.",
    "parameters": {
        "query": "Câu query tìm kiếm (ví dụ: 'quán phở nước dùng đậm đà')",
        "limit": "Số kết quả tối đa (mặc định 10)",
    },
}


async def retrieve_context_text(
    db: AsyncSession,
    query: str,
    limit: int = 10,
    threshold: float = 0.6,
) -> list[TextSearchResult]:
    """
    RAG Text - Semantic search in text descriptions.

    Uses pgvector to find places matching the query based on
    text embeddings (768-dim from text-embedding-004).

    Args:
        db: Database session
        query: Natural language query
        limit: Maximum results
        threshold: Minimum similarity threshold

    Returns:
        List of places with similarity scores
    """
    # Generate embedding for query
    query_embedding = await embedding_client.embed_text(query)

    # Search using pgvector cosine similarity
    results = await db.execute(
        text("""
            SELECT 
                place_id,
                1 - (text_embedding <=> :embedding::vector) as similarity,
                metadata as place_metadata
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
        TextSearchResult(
            place_id=row.place_id,
            similarity=row.similarity,
            metadata=row.place_metadata,
        )
        for row in results.fetchall()
    ]
