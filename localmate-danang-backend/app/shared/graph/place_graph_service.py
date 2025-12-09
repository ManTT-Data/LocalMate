"""Place Graph Service - Neo4j queries for places."""

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


class PlaceGraphService:
    """Service for querying places from Neo4j graph database."""

    def __init__(self, client: Neo4jClient | None = None):
        """Initialize with Neo4j client."""
        self._client = client or neo4j_client

    async def find_places_by_category(
        self,
        category: str,
        limit: int = 10,
        min_rating: float = 0.0,
    ) -> list[PlaceResult]:
        """
        Find places by category.

        Args:
            category: Category to filter (e.g., 'restaurant', 'beach')
            limit: Maximum number of results
            min_rating: Minimum rating filter

        Returns:
            List of PlaceResult
        """
        query = """
        MATCH (p:Place)
        WHERE toLower(p.category) CONTAINS toLower($category)
          AND (p.rating IS NULL OR p.rating >= $min_rating)
        RETURN p.id AS place_id, p.name AS name, 
               p.lat AS lat, p.lng AS lng,
               p.category AS category, p.rating AS rating,
               p.description AS description
        ORDER BY p.rating DESC
        LIMIT $limit
        """
        results = await self._client.run_cypher(
            query,
            {"category": category, "limit": limit, "min_rating": min_rating},
        )
        return [PlaceResult(**r) for r in results]

    async def find_places_by_interests(
        self,
        interests: list[str],
        limit: int = 10,
        min_rating: float = 0.0,
    ) -> list[PlaceResult]:
        """
        Find places matching any of the given interests.

        Args:
            interests: List of interest keywords
            limit: Maximum number of results
            min_rating: Minimum rating filter

        Returns:
            List of PlaceResult
        """
        query = """
        MATCH (p:Place)
        WHERE (p.rating IS NULL OR p.rating >= $min_rating)
          AND any(interest IN $interests WHERE 
              toLower(p.category) CONTAINS toLower(interest) OR
              toLower(p.name) CONTAINS toLower(interest) OR
              (p.tags IS NOT NULL AND any(tag IN p.tags WHERE toLower(tag) CONTAINS toLower(interest)))
          )
        RETURN p.id AS place_id, p.name AS name,
               p.lat AS lat, p.lng AS lng,
               p.category AS category, p.rating AS rating,
               p.description AS description
        ORDER BY p.rating DESC
        LIMIT $limit
        """
        results = await self._client.run_cypher(
            query,
            {"interests": interests, "limit": limit, "min_rating": min_rating},
        )
        return [PlaceResult(**r) for r in results]

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
            point({{latitude: p.lat, longitude: p.lng}}),
            point({{latitude: $lat, longitude: $lng}})
        ) / 1000 AS distance_km
        WHERE distance_km <= $max_distance
        {category_filter}
        RETURN p.id AS place_id, p.name AS name,
               p.lat AS lat, p.lng AS lng,
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
            )
            for r in results
        ]

    async def find_restaurant_and_cafe_for_evening(
        self,
        interests: list[str] | None = None,
        max_distance_km: float = 3.0,
    ) -> list[PlaceResult]:
        """
        Find a restaurant and cafe combo for an evening out.

        MVP: Simplified logic.

        Args:
            interests: Optional interest filters
            max_distance_km: Max distance between venues

        Returns:
            List with restaurant and cafe
        """
        # Find a restaurant (prefer seafood if in interests)
        restaurant_category = "restaurant"
        if interests and "seafood" in interests:
            restaurant_category = "seafood"

        restaurants = await self.find_places_by_category(
            category=restaurant_category,
            limit=1,
            min_rating=4.0,
        )

        if not restaurants:
            restaurants = await self.find_places_by_category(
                category="restaurant",
                limit=1,
            )

        # Find a cafe near the restaurant
        if restaurants:
            cafes = await self.find_nearby_places(
                lat=restaurants[0].lat,
                lng=restaurants[0].lng,
                max_distance_km=max_distance_km,
                category="cafe",
                limit=1,
            )
            return restaurants + cafes

        return restaurants


# Singleton instance
place_graph_service = PlaceGraphService()
