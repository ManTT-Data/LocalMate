"""Graph Tool - Neo4j spatial search with place details, relationships, and OSM geocoding.

Features:
- Spatial search (find nearby places by coordinates)
- Place details with photos and reviews
- Same category relationships
- OpenStreetMap geocoding fallback
"""

from dataclasses import dataclass, field
from typing import Optional, Any

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
    distance_km: float | None = None
    rating: float | None = None
    description: str | None = None


@dataclass
class NearbyPlace:
    """Nearby place with distance."""

    place_id: str
    name: str
    category: str
    rating: float
    distance_km: float


@dataclass
class Review:
    """Place review."""

    text: str
    rating: int
    reviewer: str


@dataclass
class PlaceDetails:
    """Complete place details from Neo4j."""

    place_id: str
    name: str
    category: str
    rating: float
    address: str
    phone: str | None = None
    website: str | None = None
    google_maps_url: str | None = None
    description: str | None = None
    specialty: str | None = None
    price_range: str | None = None
    coordinates: dict[str, float] = field(default_factory=dict)
    photos_count: int = 0
    reviews_count: int = 0
    photos: list[str] = field(default_factory=list)
    reviews: list[Review] = field(default_factory=list)
    nearby_places: list[NearbyPlace] = field(default_factory=list)
    same_category: list[dict[str, Any]] = field(default_factory=list)


# Available categories in Neo4j
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
    "description": """Tìm địa điểm gần một vị trí hoặc lấy chi tiết địa điểm.

Dùng khi:
- Người dùng hỏi về vị trí, khoảng cách, "gần đây", "gần X"
- Cần tìm quán xung quanh một landmark (Cầu Rồng, Mỹ Khê, Bà Nà)
- Lấy chi tiết đầy đủ về một địa điểm cụ thể

Categories: Restaurant, Coffee shop, Cafe, Bar, Hotel, Seafood restaurant, 
Japanese restaurant, Korean restaurant, Gym, Fitness center, v.v.""",
    "parameters": {
        "location": "Tên địa điểm trung tâm (VD: 'Bãi biển Mỹ Khê', 'Cầu Rồng')",
        "category": "Loại địa điểm: restaurant, coffee, hotel, bar, seafood, gym, etc.",
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
    Find nearby places using Neo4j spatial query.

    Args:
        lat: Center latitude
        lng: Center longitude
        max_distance_km: Maximum distance in kilometers
        category: Optional category filter
        limit: Maximum results

    Returns:
        List of nearby places ordered by distance
    """
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
            category=r["category"] or '',
            lat=r["lat"] or 0.0,
            lng=r["lng"] or 0.0,
            distance_km=r.get("distance_km"),
            rating=r.get("rating"),
            description=r.get("description"),
        )
        for r in results
    ]


async def get_place_details(
    place_id: str,
    include_nearby: bool = True,
    include_same_category: bool = True,
    nearby_limit: int = 5,
) -> PlaceDetails | None:
    """
    Get complete place details including photos, reviews, and relationships.

    Args:
        place_id: The place identifier
        include_nearby: Whether to include nearby places
        include_same_category: Whether to include same category places
        nearby_limit: Limit for nearby/related results

    Returns:
        PlaceDetails or None if not found
    """
    # Main place query with photos and reviews
    query = """
    MATCH (p:Place {id: $place_id})
    OPTIONAL MATCH (p)-[:HAS_PHOTO]->(photo:Photo)
    OPTIONAL MATCH (p)-[:HAS_REVIEW]->(review:Review)
    RETURN p,
           collect(DISTINCT photo.path) as photos,
           collect(DISTINCT {
               text: review.text,
               rating: review.rating,
               reviewer: review.reviewer
           }) as reviews
    """

    results = await neo4j_client.run_cypher(query, {"place_id": place_id})

    if not results or not results[0].get('p'):
        return None

    record = results[0]
    place = record['p']

    details = PlaceDetails(
        place_id=place.get('id', place_id),
        name=place.get('name', 'Unknown'),
        category=place.get('category', ''),
        rating=float(place.get('rating', 0) or 0),
        address=place.get('address', ''),
        phone=place.get('phone'),
        website=place.get('website'),
        google_maps_url=place.get('google_maps_url'),
        description=place.get('description'),
        specialty=place.get('specialty'),
        price_range=place.get('price_range'),
        coordinates={
            'lat': float(place.get('latitude', 0) or 0),
            'lng': float(place.get('longitude', 0) or 0)
        },
        photos_count=int(place.get('photos_count', 0) or 0),
        reviews_count=int(place.get('reviews_count', 0) or 0),
        photos=record.get('photos', [])[:10],
        reviews=[
            Review(
                text=r['text'] or '',
                rating=int(r['rating'] or 0),
                reviewer=r['reviewer'] or ''
            )
            for r in record.get('reviews', [])[:5]
            if r.get('text')
        ]
    )

    # Get nearby places
    if include_nearby:
        details.nearby_places = await get_nearby_by_relationship(place_id, nearby_limit)

    # Get same category places
    if include_same_category:
        details.same_category = await get_same_category_places(place_id, nearby_limit)

    return details


async def get_nearby_by_relationship(
    place_id: str,
    limit: int = 5,
    max_distance_km: float = 2.0
) -> list[NearbyPlace]:
    """
    Get places near a given place using NEAR relationship.

    Args:
        place_id: The source place identifier
        limit: Maximum number of results
        max_distance_km: Maximum distance in km

    Returns:
        List of NearbyPlace objects
    """
    query = """
    MATCH (p:Place {id: $place_id})-[n:NEAR]-(other:Place)
    WHERE n.distance_km <= $max_distance
    RETURN other.id as place_id,
           other.name as name,
           other.category as category,
           other.rating as rating,
           n.distance_km as distance_km
    ORDER BY n.distance_km
    LIMIT $limit
    """

    results = await neo4j_client.run_cypher(query, {
        "place_id": place_id,
        "max_distance": max_distance_km,
        "limit": limit
    })

    return [
        NearbyPlace(
            place_id=r['place_id'],
            name=r['name'],
            category=r['category'] or '',
            rating=float(r['rating'] or 0),
            distance_km=round(float(r['distance_km'] or 0), 2)
        )
        for r in results
    ]


async def get_same_category_places(
    place_id: str,
    limit: int = 5
) -> list[dict[str, Any]]:
    """
    Get other places in the same category.

    Args:
        place_id: The source place identifier
        limit: Maximum number of results

    Returns:
        List of places in same category, ordered by rating
    """
    query = """
    MATCH (p:Place {id: $place_id})-[:IN_CATEGORY]->(c:Category)<-[:IN_CATEGORY]-(other:Place)
    WHERE other.id <> $place_id
    RETURN other.id as place_id,
           other.name as name,
           other.category as category,
           other.rating as rating,
           other.address as address
    ORDER BY other.rating DESC
    LIMIT $limit
    """

    results = await neo4j_client.run_cypher(query, {
        "place_id": place_id,
        "limit": limit
    })

    return [
        {
            'place_id': r['place_id'],
            'name': r['name'],
            'category': r['category'] or '',
            'rating': float(r['rating'] or 0),
            'address': r['address'] or ''
        }
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
