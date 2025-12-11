"""RAG Pipeline - Semantic Search for preferences + Graph for optimization."""

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.graph.place_graph_service import PlaceGraphService, PlaceResult, place_graph_service
from app.shared.graph.semantic_search import SemanticSearchService, semantic_search_service


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

    Search Flow:
    1. Semantic Search: Select places matching user preferences
    2. Graph (Neo4j): Pick optimal places nearby (for route optimization)
    """

    def __init__(
        self,
        graph_service: PlaceGraphService | None = None,
        search_service: SemanticSearchService | None = None,
    ):
        """Initialize with optional service overrides."""
        self._graph = graph_service or place_graph_service
        self._search = search_service or semantic_search_service

    async def search_by_preferences(
        self,
        db: AsyncSession,
        query: str,
        limit: int = 10,
    ) -> list[RAGSearchResult]:
        """
        Step 1: Semantic Search to select places by user preferences.

        Uses pgvector embeddings to find places matching the query.

        Args:
            db: Database session
            query: Natural language query (e.g., "beach seafood view")
            limit: Maximum results

        Returns:
            List of places matching preferences
        """
        try:
            semantic_results = await self._search.search_by_text(
                db, query, limit=limit, threshold=0.6
            )

            return [
                RAGSearchResult(
                    place_id=sr.place_id,
                    name=sr.metadata.get("name", sr.place_id) if sr.metadata else sr.place_id,
                    lat=sr.metadata.get("lat", 0.0) if sr.metadata else 0.0,
                    lng=sr.metadata.get("lng", 0.0) if sr.metadata else 0.0,
                    category=sr.metadata.get("category", "unknown") if sr.metadata else "unknown",
                    rating=sr.metadata.get("rating") if sr.metadata else None,
                    description=sr.metadata.get("description") if sr.metadata else None,
                    relevance_score=sr.similarity,
                )
                for sr in semantic_results
            ]
        except Exception:
            return []

    async def optimize_with_graph(
        self,
        center_lat: float,
        center_lng: float,
        max_distance_km: float = 10.0,
        category: str | None = None,
        limit: int = 10,
    ) -> list[RAGSearchResult]:
        """
        Step 2: Use Graph (Neo4j) to pick optimal nearby places.

        Finds places near a center point for route optimization.

        Args:
            center_lat: Center latitude
            center_lng: Center longitude
            max_distance_km: Maximum distance from center
            category: Optional category filter
            limit: Maximum results

        Returns:
            List of nearby places ordered by distance
        """
        try:
            graph_results = await self._graph.find_nearby_places(
                lat=center_lat,
                lng=center_lng,
                max_distance_km=max_distance_km,
                category=category,
                limit=limit,
            )

            return [
                RAGSearchResult(
                    place_id=p.place_id,
                    name=p.name,
                    lat=p.lat,
                    lng=p.lng,
                    category=p.category,
                    rating=p.rating,
                    description=p.description,
                    relevance_score=1.0 - (p.distance_km or 0) / max_distance_km,
                )
                for p in graph_results
            ]
        except Exception:
            return []

    async def search(
        self,
        db: AsyncSession,
        query: str,
        center_lat: float | None = None,
        center_lng: float | None = None,
        limit: int = 10,
    ) -> list[RAGSearchResult]:
        """
        Combined search: Semantic + Graph optimization.

        Flow:
        1. Semantic Search to get places matching preferences
        2. If center provided, also get nearby places from Graph
        3. Combine and rank results

        Args:
            db: Database session
            query: Search query
            center_lat: Optional center for Graph search
            center_lng: Optional center for Graph search
            limit: Maximum results

        Returns:
            Combined and ranked results
        """
        results_map: dict[str, RAGSearchResult] = {}

        # 1. Semantic Search
        semantic_results = await self.search_by_preferences(db, query, limit=limit)
        for r in semantic_results:
            results_map[r.place_id] = r

        # 2. Graph optimization (if center provided)
        if center_lat is not None and center_lng is not None:
            graph_results = await self.optimize_with_graph(
                center_lat=center_lat,
                center_lng=center_lng,
                limit=limit,
            )
            for r in graph_results:
                if r.place_id not in results_map:
                    results_map[r.place_id] = r
                else:
                    # Boost score if found in both
                    existing = results_map[r.place_id]
                    existing.relevance_score = max(existing.relevance_score, r.relevance_score)

        # Sort by relevance
        results = sorted(
            results_map.values(),
            key=lambda r: r.relevance_score,
            reverse=True,
        )

        return results[:limit]


# Singleton instance
rag_pipeline = RAGPipeline()
