"""Planner Agent - generates itinerary plans with LLM and RAG."""

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.planner_app.schemas.itinerary_schemas import ItineraryPlanRequest
from app.shared.graph.place_graph_service import PlaceGraphService, place_graph_service
from app.shared.graph.rag_pipeline import RAGPipeline, rag_pipeline
from app.shared.graph.tsp_solver import optimize_route
from app.shared.integrations.gemini_client import GeminiClient, gemini_client


@dataclass
class PlannerStop:
    """Represents a single stop in a planned itinerary."""

    place_id: str
    lat: float
    lng: float
    day_index: int
    order_index: int
    snapshot: dict | None = None


@dataclass
class PlannerItineraryResult:
    """Result from the planner agent."""

    title: str
    total_days: int
    currency: str
    stops: list[PlannerStop]


class PlannerAgent:
    """
    Agent for creating itinerary plans.

    Uses RAG pipeline for intelligent place selection
    and TSP for route optimization.
    """

    def __init__(
        self,
        graph_service: PlaceGraphService | None = None,
        rag: RAGPipeline | None = None,
        llm: GeminiClient | None = None,
    ):
        """Initialize with optional service overrides."""
        self._graph_service = graph_service or place_graph_service
        self._rag = rag or rag_pipeline
        self._llm = llm or gemini_client

    async def create_itinerary(
        self,
        request: ItineraryPlanRequest,
        db: AsyncSession | None = None,
    ) -> PlannerItineraryResult:
        """
        Create an itinerary plan based on user request.

        Flow:
        1. Use RAG to find relevant places (if db available)
        2. Fallback to Neo4j if RAG not available
        3. Optimize route using TSP
        4. Generate title with LLM
        5. Distribute across days

        Args:
            request: User's planning request
            db: Optional database session for RAG

        Returns:
            PlannerItineraryResult with optimized stops
        """
        places = []
        use_rag = db is not None and request.interests

        # 1. Try RAG search first
        if use_rag:
            try:
                query = " ".join(request.interests or [])
                rag_results = await self._rag.search(
                    db,
                    query=query,
                    limit=request.duration_days * 3,
                )
                places = [
                    type(
                        "Place",
                        (),
                        {
                            "place_id": r.place_id,
                            "name": r.name,
                            "lat": r.lat,
                            "lng": r.lng,
                            "category": r.category,
                            "rating": r.rating,
                        },
                    )()
                    for r in rag_results
                ]
            except Exception:
                pass  # Fall through to other methods

        # 2. Fallback to Neo4j
        if not places and request.interests:
            places = await self._graph_service.find_places_by_interests(
                interests=request.interests,
                limit=request.duration_days * 3,
                min_rating=3.5,
            )

        # 3. Fallback to dummy data
        if not places:
            return await self._create_dummy_itinerary(request)

        # 4. Optimize route using TSP
        points = [(p.lat, p.lng) for p in places]
        optimized_order = await optimize_route(
            points,
            start_lat=request.start_location_lat,
            start_lng=request.start_location_lng,
        )

        # 5. Generate title with LLM
        try:
            title = await self._llm.generate_itinerary_title(
                duration_days=request.duration_days,
                interests=request.interests,
            )
        except Exception:
            title = f"Khám phá Đà Nẵng {request.duration_days} ngày"

        # 6. Create stops with optimized order
        stops = []
        places_per_day = max(1, len(optimized_order) // request.duration_days)

        for i, place_idx in enumerate(optimized_order):
            place = places[place_idx]
            day = min((i // places_per_day) + 1, request.duration_days)
            order_in_day = (i % places_per_day) + 1

            stops.append(
                PlannerStop(
                    place_id=place.place_id,
                    lat=place.lat,
                    lng=place.lng,
                    day_index=day,
                    order_index=order_in_day,
                    snapshot={
                        "name": place.name,
                        "category": place.category,
                        "rating": getattr(place, "rating", None),
                    },
                )
            )

        return PlannerItineraryResult(
            title=title,
            total_days=request.duration_days,
            currency="VND",
            stops=stops,
        )

    async def _create_dummy_itinerary(
        self,
        request: ItineraryPlanRequest,
    ) -> PlannerItineraryResult:
        """Fallback: Create itinerary with dummy data."""
        dummy_places = [
            {
                "place_id": "my-khe-beach",
                "lat": 16.0544,
                "lng": 108.2480,
                "name": "Bãi biển Mỹ Khê",
                "category": "beach",
            },
            {
                "place_id": "be-man-seafood",
                "lat": 16.0512,
                "lng": 108.2465,
                "name": "Nhà hàng Bé Mặn",
                "category": "restaurant",
            },
            {
                "place_id": "son-tra-peninsula",
                "lat": 16.1167,
                "lng": 108.2667,
                "name": "Bán đảo Sơn Trà",
                "category": "nature",
            },
            {
                "place_id": "marble-mountains",
                "lat": 16.0034,
                "lng": 108.2628,
                "name": "Ngũ Hành Sơn",
                "category": "landmark",
            },
            {
                "place_id": "han-river-bridge",
                "lat": 16.0726,
                "lng": 108.2269,
                "name": "Cầu Sông Hàn",
                "category": "landmark",
            },
        ]

        num_places = min(len(dummy_places), request.duration_days + 2)
        selected = dummy_places[:num_places]

        # Optimize even dummy data
        points = [(p["lat"], p["lng"]) for p in selected]
        order = await optimize_route(
            points,
            start_lat=request.start_location_lat,
            start_lng=request.start_location_lng,
        )

        stops = []
        places_per_day = max(1, len(order) // request.duration_days)

        for i, idx in enumerate(order):
            place = selected[idx]
            day = min((i // places_per_day) + 1, request.duration_days)
            stops.append(
                PlannerStop(
                    place_id=place["place_id"],
                    lat=place["lat"],
                    lng=place["lng"],
                    day_index=day,
                    order_index=(i % places_per_day) + 1,
                    snapshot={
                        "name": place["name"],
                        "category": place["category"],
                    },
                )
            )

        return PlannerItineraryResult(
            title=f"Khám phá Đà Nẵng {request.duration_days} ngày",
            total_days=request.duration_days,
            currency="VND",
            stops=stops,
        )


# Singleton instance
planner_agent = PlannerAgent()
