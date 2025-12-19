"""Text RAG Tool - Semantic search in text descriptions using pgvector.

Schema: place_text_embeddings (place_id, embedding, content_type, source_text, metadata)
        places_metadata (place_id, name, category, rating, raw_data)
"""

from dataclasses import dataclass, field
from collections import defaultdict
from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.integrations.embedding_client import embedding_client


@dataclass
class TextSearchResult:
    """Result from text context search."""

    place_id: str
    name: str
    category: str
    rating: float
    similarity: float
    description: str = ""
    source_text: str = ""
    content_type: str = ""

# Category constants - imported from centralized prompts
from app.shared.prompts import CATEGORY_KEYWORDS, CATEGORY_TO_DB


# Tool definition for agent - imported from centralized prompts
from app.shared.prompts import RETRIEVE_CONTEXT_TEXT_TOOL as TOOL_DEFINITION


def detect_category_intent(query: str) -> Optional[str]:
    """Detect if query is asking for specific category."""
    query_lower = query.lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in query_lower for kw in keywords):
            return category
    return None


async def retrieve_context_text(
    db: AsyncSession,
    query: str,
    limit: int = 10,
    threshold: float = 0.3,
) -> list[TextSearchResult]:
    """
    Semantic search in text descriptions using pgvector.

    Uses place_text_embeddings table with JOIN to places_metadata.

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
    
    # Convert to PostgreSQL vector format
    embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

    # Detect category intent for boosting
    category_intent = detect_category_intent(query)
    category_filter = CATEGORY_TO_DB.get(category_intent, []) if category_intent else []

    # Search with JOIN to places_metadata
    # Note: Use format string for embedding since SQLAlchemy param binding 
    # doesn't work correctly with ::vector type casting
    sql = text(f"""
        SELECT DISTINCT ON (e.place_id)
            e.place_id,
            e.content_type,
            e.source_text,
            1 - (e.embedding <=> '{embedding_str}'::vector) as similarity,
            m.name,
            m.category,
            m.rating,
            m.raw_data
        FROM place_text_embeddings e
        JOIN places_metadata m ON e.place_id = m.place_id
        WHERE 1 - (e.embedding <=> '{embedding_str}'::vector) > :threshold
          AND m.name IS NOT NULL 
          AND m.name != ''
        ORDER BY e.place_id, e.embedding <=> '{embedding_str}'::vector
    """)

    results = await db.execute(sql, {
        "threshold": threshold,
    })

    rows = results.fetchall()

    # Process and score results with category boosting
    scored_results = []
    for r in rows:
        score = float(r.similarity)
        
        # Category boost (15%)
        if category_filter and r.category in category_filter:
            score += 0.15
        
        # Rating boost (5% for >= 4.5)
        if r.rating and r.rating >= 4.5:
            score += 0.05
        elif r.rating and r.rating >= 4.0:
            score += 0.02
        
        raw_data = r.raw_data or {}
        
        scored_results.append((score, TextSearchResult(
            place_id=r.place_id,
            name=r.name or '',
            category=r.category or '',
            rating=float(r.rating) if r.rating else 0.0,
            similarity=round(score, 4),
            description=raw_data.get('description', '')[:300] if isinstance(raw_data, dict) else '',
            source_text=r.source_text[:300] if r.source_text else '',
            content_type=r.content_type or '',
        )))

    # Sort by score and limit
    scored_results.sort(key=lambda x: x[0], reverse=True)
    
    return [r for _, r in scored_results[:limit]]
