"""Planner Agent - generates itinerary plans using Semantic Search + TSP."""

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.planner_app.schemas.itinerary_schemas import ItineraryPlanRequest
from app.shared.constants.prompts.planner_prompts import ITINERARY_TITLE_PROMPT
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

    Flow:
    1. Use Semantic Search to select places by interests
    3. Optimize route using TSP
    4. Generate title with LLM
    """

    def __init__(
        self,
        rag: RAGPipeline | None = None,
        llm: GeminiClient | None = None,
    ):
        """Initialize with optional service overrides."""
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
        1. Semantic Search for places matching interests
        3. Optimize route using TSP
        4. Generate title with LLM
        5. Distribute across days

        Args:
            request: User's planning request
            db: Optional database session for semantic search

        Returns:
            PlannerItineraryResult with optimized stops
        """
        places = []

        # 1. Semantic Search for places matching interests
        if db is not None and request.interests:
            query = " ".join(request.interests)
            rag_results = await self._rag.search_by_preferences(
                db,
                query=query,
                limit=request.duration_days * 3,
            )
            places = [
                type("Place", (), {
                    "place_id": r.place_id,
                    "name": r.name,
                    "lat": r.lat,
                    "lng": r.lng,
                    "category": r.category,
                    "rating": r.rating,
                })()
                for r in rag_results
            ]

        # Fallback to dummy data if no places found
        if not places:
            return await self._create_dummy_itinerary(request)

        # 3. Optimize route using TSP
        points = [(p.lat, p.lng) for p in places]
        optimized_order = await optimize_route(
            points,
            start_lat=request.start_location_lat,
            start_lng=request.start_location_lng,
        )

        # 4. Generate title with LLM
        try:
            prompt = ITINERARY_TITLE_PROMPT.format(
                duration_days=request.duration_days,
                interests=", ".join(request.interests) if request.interests else "khám phá",
            )
            title = await self._llm.generate(prompt, temperature=0.8)
            title = title.strip().strip('"')
        except Exception:
            title = f"Khám phá Đà Nẵng {request.duration_days} ngày"

        # 5. Create stops with optimized order
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
                        "lat": place.lat,
                        "lng": place.lng,
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
                "place_id": "danang_dragon_bridge",
                "lat": 16.0611,
                "lng": 108.2272,
                "name": "Cầu Rồng",
                "category": "landmark",
            },
            {
                "place_id": "danang_my_khe_beach",
                "lat": 16.0544,
                "lng": 108.2452,
                "name": "Bãi biển Mỹ Khê",
                "category": "beach",
            },
            {
                "place_id": "danang_bana_hills",
                "lat": 15.9977,
                "lng": 107.9875,
                "name": "Bà Nà Hills",
                "category": "attraction",
            },
            {
                "place_id": "marble_mountains",
                "lat": 16.0034,
                "lng": 108.2628,
                "name": "Ngũ Hành Sơn",
                "category": "landmark",
            },
            {
                "place_id": "han_market",
                "lat": 16.0678,
                "lng": 108.2240,
                "name": "Chợ Hàn",
                "category": "market",
            },
        ]

        num_places = min(len(dummy_places), request.duration_days + 2)
        selected = dummy_places[:num_places]

        # Optimize route
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
                        "lat": place["lat"],
                        "lng": place["lng"],
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
