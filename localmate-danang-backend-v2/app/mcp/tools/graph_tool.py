"""Graph Tool - Spatial search using Neo4j and OSM geocoding."""

from dataclasses import dataclass

import httpx

from app.shared.integrations.neo4j_client import neo4j_client


@dataclass
class PlaceResult:
    """Result from nearby places search."""

    place_id: str
    name: str
    category: str
    lat: float
    lng: float
    distance_km: float | None
    rating: float | None
    description: str | None


# Available categories in Neo4j (for reference in prompts)
AVAILABLE_CATEGORIES = [
    "Asian restaurant", "Athletic club", "Badminton court", "Bakery", "Bar",
    "Bistro", "Board game club", "Breakfast restaurant", "Cafe",
    "Cantonese restaurant", "Chicken restaurant", "Chinese restaurant",
    "Cocktail bar", "Coffee shop", "Country food restaurant", "Deli",
    "Dessert shop", "Disco club", "Dumpling restaurant", "Espresso bar",
    "Family restaurant", "Fine dining restaurant", "Fitness center",
    "Food court", "French restaurant", "Game store", "Gym",
    "Hamburger restaurant", "Holiday apartment rental", "Hot pot restaurant",
    "Hotel", "Ice cream shop", "Indian restaurant", "Irish pub",
    "Italian restaurant", "Izakaya restaurant", "Japanese restaurant",
    "Korean barbecue restaurant", "Korean restaurant", "Live music bar",
    "Malaysian restaurant", "Mexican restaurant", "Movie theater",
    "Musical club", "Noodle shop", "Pho restaurant", "Pickleball court",
    "Pizza restaurant", "Ramen restaurant", "Restaurant", "Restaurant or cafe",
    "Rice cake shop", "Sandwich shop", "Seafood restaurant", "Soccer field",
    "Soup shop", "Sports bar", "Sports club", "Sports complex", "Steak house",
    "Sushi restaurant", "Takeout Restaurant", "Tennis court", "Tiffin center",
    "Udon noodle restaurant", "Vegan restaurant", "Vegetarian restaurant",
    "Vietnamese restaurant",
]


# Tool definition for agent
TOOL_DEFINITION = {
    "name": "find_nearby_places",
    "description": """Tìm địa điểm gần một vị trí. Dùng khi người dùng hỏi về vị trí, khoảng cách, 'gần đây'.

Các category có sẵn trong database:
- Ăn uống: Restaurant, Vietnamese restaurant, Seafood restaurant, Pho restaurant, 
  Coffee shop, Cafe, Bar, Steak house, Japanese restaurant, Korean restaurant, 
  Italian restaurant, French restaurant, Mexican restaurant, Pizza restaurant, 
  Ramen restaurant, Sushi restaurant, Hot pot restaurant, Bakery, Dessert shop
- Lưu trú: Hotel, Holiday apartment rental
- Thể thao: Gym, Fitness center, Sports complex, Badminton court, Tennis court, 
  Pickleball court, Soccer field
- Giải trí: Movie theater, Game store, Board game club, Disco club, Live music bar""",
    "parameters": {
        "location": "Tên địa điểm trung tâm (ví dụ: 'Bãi biển Mỹ Khê', 'Cầu Rồng')",
        "category": "Loại địa điểm: restaurant, coffee, hotel, bar, steak, seafood, gym, etc.",
        "max_distance_km": "Khoảng cách tối đa tính theo km (mặc định 5)",
        "limit": "Số kết quả tối đa (mặc định 10)",
    },
}


async def find_nearby_places(
    lat: float,
    lng: float,
    max_distance_km: float = 5.0,
    category: str | None = None,
    limit: int = 10,
) -> list[PlaceResult]:
    """
    Graph Spatial - Find nearby places using Neo4j.

    Uses Neo4j's spatial capabilities to find places within
    a given radius from a point.

    Args:
        lat: Center latitude
        lng: Center longitude
        max_distance_km: Maximum distance in kilometers
        category: Optional category filter (cafe, restaurant, etc.)
        limit: Maximum results

    Returns:
        List of nearby places ordered by distance
    """
    # Build Cypher query with optional category filter
    category_filter = ""
    if category:
        category_filter = "AND toLower(p.category) CONTAINS toLower($category)"

    query = f"""
    MATCH (p:Place)
    WITH p, point.distance(
        point({{latitude: p.latitude, longitude: p.longitude}}),
        point({{latitude: $lat, longitude: $lng}})
    ) / 1000 as distance_km
    WHERE distance_km <= $max_distance {category_filter}
    RETURN 
        p.id as place_id,
        p.name as name,
        p.category as category,
        p.latitude as lat,
        p.longitude as lng,
        distance_km,
        p.rating as rating,
        p.description as description
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

    results = await neo4j_client.run_cypher(query, params)

    return [
        PlaceResult(
            place_id=r["place_id"],
            name=r["name"],
            category=r["category"],
            lat=r["lat"],
            lng=r["lng"],
            distance_km=r.get("distance_km"),
            rating=r.get("rating"),
            description=r.get("description"),
        )
        for r in results
    ]


async def geocode_location(location_name: str, country: str = "Vietnam") -> tuple[float, float] | None:
    """
    Geocode a location name using OpenStreetMap Nominatim API.

    Args:
        location_name: Name of the place (e.g., "Cầu Rồng", "Bãi biển Mỹ Khê")
        country: Country to bias search (default: Vietnam)

    Returns:
        (lat, lng) tuple or None if not found
    """
    # Add Da Nang context to improve accuracy
    search_query = f"{location_name}, Da Nang, {country}"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://nominatim.openstreetmap.org/search",
                params={
                    "q": search_query,
                    "format": "json",
                    "limit": 1,
                    "addressdetails": 0,
                },
                headers={
                    "User-Agent": "LocalMate-DaNang/1.0 (travel assistant app)",
                },
            )
            response.raise_for_status()
            data = response.json()

            if data and len(data) > 0:
                lat = float(data[0]["lat"])
                lng = float(data[0]["lon"])
                return (lat, lng)

    except Exception:
        pass

    return None


async def get_location_coordinates(location_name: str) -> tuple[float, float] | None:
    """
    Get coordinates for a location name.

    First tries Neo4j, then falls back to OpenStreetMap Nominatim.

    Args:
        location_name: Name of the place (e.g., "Khách sạn Rex", "Cầu Rồng")

    Returns:
        (lat, lng) tuple or None if not found
    """
    # Try Neo4j first
    try:
        query = """
        MATCH (p:Place)
        WHERE toLower(p.name) CONTAINS toLower($name)
        RETURN p.latitude as lat, p.longitude as lng
        LIMIT 1
        """
        results = await neo4j_client.run_cypher(query, {"name": location_name})
        if results and results[0].get("lat") and results[0].get("lng"):
            return (results[0]["lat"], results[0]["lng"])
    except Exception:
        pass

    # Fallback to OpenStreetMap Nominatim
    osm_result = await geocode_location(location_name)
    if osm_result:
        return osm_result

    return None
