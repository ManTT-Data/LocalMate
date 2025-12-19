"""Visual RAG Tool - Image similarity search using local SigLIP embeddings.

Schema: place_image_embeddings (place_id, embedding, image_url, metadata)
        places_metadata (place_id, name, category, rating, raw_data)
        
Uses local SigLIP model (ViT-B-16-SigLIP) for generating 768-dim image embeddings.
"""

from dataclasses import dataclass
from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.integrations.siglip_client import get_siglip_client


@dataclass
class ImageSearchResult:
    """Result from visual similarity search."""

    place_id: str
    name: str
    category: str
    rating: float
    similarity: float
    matched_images: int = 1
    image_url: str = ""

# Tool definition for agent - imported from centralized prompts
from app.shared.prompts import RETRIEVE_SIMILAR_VISUALS_TOOL as TOOL_DEFINITION


async def retrieve_similar_visuals(
    db: AsyncSession,
    image_url: str | None = None,
    image_bytes: bytes | None = None,
    limit: int = 10,
    threshold: float = 0.2,
) -> list[ImageSearchResult]:
    """
    Visual similarity search using local SigLIP embeddings.

    Uses place_image_embeddings table with JOIN to places_metadata.

    Args:
        db: Database session
        image_url: URL of the query image
        image_bytes: Raw image bytes (alternative to URL)
        limit: Maximum results
        threshold: Minimum similarity threshold

    Returns:
        List of places with visual similarity scores
    """
    # Get SigLIP client (singleton)
    siglip = get_siglip_client()
    
    # Generate image embedding using local model
    if image_bytes:
        image_embedding = siglip.embed_image_bytes(image_bytes)
    elif image_url:
        image_embedding = siglip.embed_image_url(image_url)
    else:
        return []

    if image_embedding is None:
        return []

    # Convert numpy array to PostgreSQL vector format
    embedding_str = "[" + ",".join(str(x) for x in image_embedding.tolist()) + "]"

    # Search with JOIN to places_metadata
    sql = text(f"""
        SELECT 
            e.place_id,
            e.image_url,
            1 - (e.embedding <=> '{embedding_str}'::vector) as similarity,
            m.name,
            m.category,
            m.rating
        FROM place_image_embeddings e
        JOIN places_metadata m ON e.place_id = m.place_id
        WHERE 1 - (e.embedding <=> '{embedding_str}'::vector) > :threshold
          AND m.name IS NOT NULL 
          AND m.name != ''
        ORDER BY e.embedding <=> '{embedding_str}'::vector
        LIMIT 100
    """)

    results = await db.execute(sql, {
        "threshold": threshold,
    })

    rows = results.fetchall()

    # Aggregate by place (multiple images per place)
    place_scores: dict = {}

    for r in rows:
        pid = r.place_id

        if pid not in place_scores:
            place_scores[pid] = {
                'total_score': 0.0,
                'count': 0,
                'data': r,
                'best_image': r.image_url,
            }

        place_scores[pid]['total_score'] += float(r.similarity)
        place_scores[pid]['count'] += 1
        
        # Keep best matching image
        if float(r.similarity) > place_scores[pid]['total_score'] / place_scores[pid]['count']:
            place_scores[pid]['best_image'] = r.image_url

    # Sort by average similarity
    sorted_places = sorted(
        place_scores.items(),
        key=lambda x: x[1]['total_score'] / x[1]['count'],
        reverse=True
    )[:limit]

    # Build results
    return [
        ImageSearchResult(
            place_id=pid,
            name=data['data'].name or '',
            category=data['data'].category or '',
            rating=float(data['data'].rating or 0),
            similarity=round(data['total_score'] / data['count'], 4),
            matched_images=data['count'],
            image_url=data['best_image'] or '',
        )
        for pid, data in sorted_places
    ]


async def search_by_image_url(
    db: AsyncSession,
    image_url: str,
    limit: int = 10,
) -> list[ImageSearchResult]:
    """Search places by image URL."""
    return await retrieve_similar_visuals(db=db, image_url=image_url, limit=limit)


async def search_by_image_bytes(
    db: AsyncSession,
    image_bytes: bytes,
    limit: int = 10,
) -> list[ImageSearchResult]:
    """Search places by uploading image bytes."""
    return await retrieve_similar_visuals(db=db, image_bytes=image_bytes, limit=limit)
