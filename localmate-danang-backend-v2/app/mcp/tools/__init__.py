"""MCP Tools Package - Model Context Protocol tools for the agent.

Tools:
1. retrieve_context_text - Text search via pgvector + places_metadata
2. retrieve_similar_visuals - Image search via pgvector + places_metadata  
3. find_nearby_places - Neo4j spatial search + place details
"""

from app.mcp.tools.text_tool import (
    TextSearchResult,
    retrieve_context_text,
    TOOL_DEFINITION as TEXT_TOOL_DEFINITION,
)
from app.mcp.tools.visual_tool import (
    ImageSearchResult,
    retrieve_similar_visuals,
    search_by_image_url,
    search_by_image_bytes,
    TOOL_DEFINITION as VISUAL_TOOL_DEFINITION,
)
from app.mcp.tools.graph_tool import (
    PlaceResult,
    PlaceDetails,
    NearbyPlace,
    Review,
    AVAILABLE_CATEGORIES,
    find_nearby_places,
    get_place_details,
    get_nearby_by_relationship,
    get_same_category_places,
    get_location_coordinates,
    TOOL_DEFINITION as GRAPH_TOOL_DEFINITION,
)
from app.mcp.tools.social_tool import (
    SocialSearchResult,
    search_social_media,
    TOOL_DEFINITION as SOCIAL_TOOL_DEFINITION,
)



# Combined tool definitions for agent
TOOL_DEFINITIONS = [
    TEXT_TOOL_DEFINITION,
    VISUAL_TOOL_DEFINITION,
    GRAPH_TOOL_DEFINITION,
    SOCIAL_TOOL_DEFINITION,
]


class MCPTools:
    """
    MCP Tools container implementing the 3 core tools for MMCA Agent.
    """

    TOOL_DEFINITIONS = TOOL_DEFINITIONS
    AVAILABLE_CATEGORIES = AVAILABLE_CATEGORIES

    # Text Tool
    async def retrieve_context_text(self, db, query, limit=10, threshold=0.3):
        """Semantic search in text descriptions."""
        return await retrieve_context_text(db, query, limit, threshold)

    # Visual Tool
    async def retrieve_similar_visuals(self, db, image_url=None, image_bytes=None, limit=10, threshold=0.2):
        """Visual similarity search using image embeddings."""
        return await retrieve_similar_visuals(db, image_url, image_bytes, limit, threshold)

    async def search_by_image_url(self, db, image_url, limit=10):
        """Search places by image URL."""
        return await search_by_image_url(db, image_url, limit)

    async def search_by_image_bytes(self, db, image_bytes, limit=10):
        """Search places by uploading image bytes."""
        return await search_by_image_bytes(db, image_bytes, limit)

    # Graph Tool
    async def find_nearby_places(self, lat, lng, max_distance_km=5.0, category=None, limit=10):
        """Find nearby places using Neo4j spatial query."""
        return await find_nearby_places(lat, lng, max_distance_km, category, limit)

    async def get_place_details(self, place_id, include_nearby=True, include_same_category=True, nearby_limit=5):
        """Get complete place details with photos, reviews, and relationships."""
        return await get_place_details(place_id, include_nearby, include_same_category, nearby_limit)

    async def get_same_category_places(self, place_id, limit=5):
        """Get other places in the same category."""
        return await get_same_category_places(place_id, limit)

    async def geocode_location(self, location_name, country="Vietnam"):
        """Geocode a location using OpenStreetMap Nominatim."""
        return await geocode_location(location_name, country)

    async def get_location_coordinates(self, location_name):
        """Get coordinates for a location (Neo4j + OSM fallback)."""
        return await get_location_coordinates(location_name)
    
    # Social Tool
    async def search_social_media(self, query: str, limit: int = 10, freshness: str = "pw", platforms: list[str] = None) -> list[SocialSearchResult]:
        """Search for social media content (news, trends)."""
        return await search_social_media(query, limit, freshness, platforms)




# Global MCP tools instance
mcp_tools = MCPTools()


# Re-export for convenience
_all_ = [
    "MCPTools",
    "mcp_tools",
    "TextSearchResult",
    "ImageSearchResult",
    "PlaceResult",
    "PlaceDetails",
    "NearbyPlace",
    "Review",
    "retrieve_context_text",
    "retrieve_similar_visuals",
    "find_nearby_places",
    "get_place_details",
    "geocode_location",
    "get_location_coordinates",
    "TOOL_DEFINITIONS",
    "AVAILABLE_CATEGORIES",
]
