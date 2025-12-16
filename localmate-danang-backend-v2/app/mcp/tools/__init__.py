"""MCP Tools Package - Model Context Protocol tools for the agent.

Tools:
1. retrieve_context_text - RAG Text search via pgvector
2. retrieve_similar_visuals - RAG Image search via CLIP embeddings
3. find_nearby_places - Graph spatial search via Neo4j + OSM geocoding
"""

from app.mcp.tools.text_tool import (
    TextSearchResult,
    retrieve_context_text,
    TOOL_DEFINITION as TEXT_TOOL_DEFINITION,
)
from app.mcp.tools.visual_tool import (
    ImageSearchResult,
    retrieve_similar_visuals,
    TOOL_DEFINITION as VISUAL_TOOL_DEFINITION,
)
from app.mcp.tools.graph_tool import (
    PlaceResult,
    AVAILABLE_CATEGORIES,
    find_nearby_places,
    geocode_location,
    get_location_coordinates,
    TOOL_DEFINITION as GRAPH_TOOL_DEFINITION,
)


# Combined tool definitions for agent
TOOL_DEFINITIONS = [
    TEXT_TOOL_DEFINITION,
    VISUAL_TOOL_DEFINITION,
    GRAPH_TOOL_DEFINITION,
]


class MCPTools:
    """
    MCP Tools container implementing the 3 core tools for MMCA Agent.

    This class provides a unified interface to all MCP tools.
    """

    TOOL_DEFINITIONS = TOOL_DEFINITIONS
    AVAILABLE_CATEGORIES = AVAILABLE_CATEGORIES

    async def retrieve_context_text(self, db, query, limit=10, threshold=0.6):
        """Semantic search in text descriptions."""
        return await retrieve_context_text(db, query, limit, threshold)

    async def retrieve_similar_visuals(self, db, image_url, limit=10, threshold=0.6):
        """Visual similarity search using CLIP."""
        return await retrieve_similar_visuals(db, image_url, limit, threshold)

    async def find_nearby_places(self, lat, lng, max_distance_km=5.0, category=None, limit=10):
        """Find nearby places using Neo4j spatial query."""
        return await find_nearby_places(lat, lng, max_distance_km, category, limit)

    async def geocode_location(self, location_name, country="Vietnam"):
        """Geocode a location using OpenStreetMap Nominatim."""
        return await geocode_location(location_name, country)

    async def get_location_coordinates(self, location_name):
        """Get coordinates for a location (Neo4j + OSM fallback)."""
        return await get_location_coordinates(location_name)


# Global MCP tools instance
mcp_tools = MCPTools()


# Re-export for convenience
__all__ = [
    "MCPTools",
    "mcp_tools",
    "TextSearchResult",
    "ImageSearchResult",
    "PlaceResult",
    "TOOL_DEFINITIONS",
    "AVAILABLE_CATEGORIES",
    "retrieve_context_text",
    "retrieve_similar_visuals",
    "find_nearby_places",
    "geocode_location",
    "get_location_coordinates",
]
