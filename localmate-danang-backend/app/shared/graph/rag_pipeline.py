"""RAG Pipeline - combines LLM, embeddings, and graph for intelligent search."""

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.graph.place_graph_service import PlaceGraphService, PlaceResult, place_graph_service
from app.shared.graph.semantic_search import SemanticSearchService, semantic_search_service
from app.shared.integrations.gemini_client import GeminiClient, gemini_client


@dataclass
class RAGSearchResult:
    """Result from RAG pipeline search."""

    place_id: str
    name: str
    lat: float
    lng: float
    category: str
    rating: float | None
    description: str | None
    relevance_score: float


class RAGPipeline:
    """
    RAG Pipeline for intelligent place search.

    Flow:
    1. Parse user intent with LLM
    2. Semantic search in pgvector
    3. Graph search in Neo4j
    4. Combine and rank results
    """

    def __init__(
        self,
        llm: GeminiClient | None = None,
        graph_service: PlaceGraphService | None = None,
        search_service: SemanticSearchService | None = None,
    ):
        """Initialize with optional service overrides."""
        self._llm = llm or gemini_client
        self._graph = graph_service or place_graph_service
        self._search = search_service or semantic_search_service

    async def search(
        self,
        db: AsyncSession,
        query: str,
        limit: int = 10,
    ) -> list[RAGSearchResult]:
        """
        Search places using RAG pipeline.

        Args:
            db: Database session
            query: Natural language query
            limit: Maximum results

        Returns:
            List of search results ranked by relevance
        """
        # 1. Parse intent
        intent = await self._llm.parse_intent(query)
        categories = intent.get("categories", [])
        specialty = intent.get("specialty", [])
        min_rating = intent.get("min_rating", 4.0)

        # 2. Semantic search (if embeddings available)
        semantic_results = []
        try:
            semantic_results = await self._search.search_by_text(
                db, query, limit=limit, threshold=0.6
            )
        except Exception:
            pass  # Embeddings may not be set up yet

        # 3. Graph search based on intent
        graph_results = []
        if categories or specialty:
            interests = categories + specialty
            graph_results = await self._graph.find_places_by_interests(
                interests=interests,
                limit=limit,
                min_rating=min_rating,
            )

        # 4. Combine results
        results_map: dict[str, RAGSearchResult] = {}

        # Add graph results
        for place in graph_results:
            results_map[place.place_id] = RAGSearchResult(
                place_id=place.place_id,
                name=place.name,
                lat=place.lat,
                lng=place.lng,
                category=place.category,
                rating=place.rating,
                description=place.description,
                relevance_score=0.7,  # Base score for graph results
            )

        # Boost with semantic results
        for sr in semantic_results:
            if sr.place_id in results_map:
                # Boost existing result
                results_map[sr.place_id].relevance_score = max(
                    results_map[sr.place_id].relevance_score,
                    sr.similarity,
                )
            elif sr.metadata:
                # Add from semantic search
                results_map[sr.place_id] = RAGSearchResult(
                    place_id=sr.place_id,
                    name=sr.metadata.get("name", sr.place_id),
                    lat=sr.metadata.get("lat", 0.0),
                    lng=sr.metadata.get("lng", 0.0),
                    category=sr.metadata.get("category", "unknown"),
                    rating=sr.metadata.get("rating"),
                    description=sr.metadata.get("description"),
                    relevance_score=sr.similarity,
                )

        # Sort by relevance
        results = sorted(
            results_map.values(),
            key=lambda r: r.relevance_score,
            reverse=True,
        )

        return results[:limit]

    async def search_by_image(
        self,
        db: AsyncSession,
        image_url: str,
        limit: int = 10,
    ) -> list[RAGSearchResult]:
        """
        Search places by image similarity.

        Args:
            db: Database session
            image_url: URL of query image
            limit: Maximum results

        Returns:
            List of search results
        """
        # Semantic image search
        semantic_results = await self._search.search_by_image(
            db, image_url, limit=limit, threshold=0.6
        )

        results = []
        for sr in semantic_results:
            if sr.metadata:
                results.append(
                    RAGSearchResult(
                        place_id=sr.place_id,
                        name=sr.metadata.get("name", sr.place_id),
                        lat=sr.metadata.get("lat", 0.0),
                        lng=sr.metadata.get("lng", 0.0),
                        category=sr.metadata.get("category", "unknown"),
                        rating=sr.metadata.get("rating"),
                        description=sr.metadata.get("description"),
                        relevance_score=sr.similarity,
                    )
                )

        return results

    async def generate_description(
        self,
        place: PlaceResult | RAGSearchResult,
    ) -> str:
        """Generate LLM description for a place."""
        return await self._llm.generate_stop_description(
            place_name=place.name if hasattr(place, 'name') else place.place_id,
            category=place.category,
        )


# Singleton instance
rag_pipeline = RAGPipeline()
