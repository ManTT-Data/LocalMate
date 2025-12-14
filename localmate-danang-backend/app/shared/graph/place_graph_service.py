"""Place Graph Service - Neo4j queries for nearby places."""

from dataclasses import dataclass

from app.shared.integrations.neo4j_client import Neo4jClient, neo4j_client


@dataclass
class PlaceResult:
    """Result from Neo4j place query."""

    place_id: str
    name: str
    lat: float
    lng: float
    category: str
    rating: float | None = None
    description: str | None = None
    distance_km: float | None = None


class PlaceGraphService:
    """Service for querying places from Neo4j graph database."""

    def __init__(self, client: Neo4jClient | None = None):
        """Initialize with Neo4j client."""
        self._client = client or neo4j_client

    async def find_nearby_places(
        self,
        lat: float,
        lng: float,
        max_distance_km: float = 5.0,
        category: str | None = None,
        limit: int = 10,
    ) -> list[PlaceResult]:
        """
        Find places near a given location.

        This is the main function for Neo4j - used by Graph optimization
        in the RAG pipeline to pick optimal places.

        Args:
            lat: Center latitude
            lng: Center longitude
            max_distance_km: Maximum distance in kilometers
            category: Optional category filter
            limit: Maximum number of results

        Returns:
            List of PlaceResult ordered by distance
        """
        category_filter = ""
        if category:
            category_filter = "AND toLower(p.category) CONTAINS toLower($category)"

        query = f"""
        MATCH (p:Place)
        WITH p, point.distance(
            point({{latitude: p.latitude, longitude: p.longitude}}),
            point({{latitude: $lat, longitude: $lng}})
        ) / 1000 AS distance_km
        WHERE distance_km <= $max_distance
        {category_filter}
        RETURN p.id AS place_id, p.name AS name,
               p.latitude AS lat, p.longitude AS lng,
               p.category AS category, p.rating AS rating,
               p.description AS description,
               distance_km
        ORDER BY distance_km
        LIMIT $limit
        """
        params = {
            "lat": lat,
            "lng": lng,
            "max_distance": max_distance_km,
            "limit": limit,
        }
        if category:
            params["category"] = category

        results = await self._client.run_cypher(query, params)
        return [
            PlaceResult(
                place_id=r["place_id"],
                name=r["name"],
                lat=r["lat"],
                lng=r["lng"],
                category=r["category"],
                rating=r.get("rating"),
                description=r.get("description"),
                distance_km=r.get("distance_km"),
            )
            for r in results
        ]


# Singleton instance
place_graph_service = PlaceGraphService()
