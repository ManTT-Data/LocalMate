"""MCP Service - orchestrates MCP tools and generates suggested actions."""

import uuid
from typing import Any

from app.planner_app.schemas.action_schemas import (
    ActionType,
    RideActionParams,
    SuggestedAction,
)
from app.shared.integrations.mcp.base_tool import MCPBaseTool, ToolResult
from app.shared.integrations.mcp.grab_transport_tool import grab_transport_tool


class MCPService:
    """Service for managing MCP tools and generating actions."""

    def __init__(self):
        """Initialize with available tools."""
        self._tools: dict[str, MCPBaseTool] = {
            "grab_transport": grab_transport_tool,
        }

    def get_tool(self, name: str) -> MCPBaseTool | None:
        """Get a tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> list[dict]:
        """List all available tools with their specs."""
        return [tool.get_tool_spec() for tool in self._tools.values()]

    async def execute_tool(self, name: str, params: dict) -> ToolResult | None:
        """Execute a tool by name with parameters."""
        tool = self.get_tool(name)
        if not tool:
            return None
        return await tool.execute(params)

    async def generate_ride_actions(
        self,
        stops: list[dict],
    ) -> list[SuggestedAction]:
        """
        Generate ride booking actions between consecutive stops.

        Args:
            stops: List of stop dicts with lat, lng, name

        Returns:
            List of suggested ride actions
        """
        actions = []

        for i in range(len(stops) - 1):
            from_stop = stops[i]
            to_stop = stops[i + 1]

            # Get ride estimate
            result = await grab_transport_tool.execute({
                "from_lat": from_stop["lat"],
                "from_lng": from_stop["lng"],
                "to_lat": to_stop["lat"],
                "to_lng": to_stop["lng"],
                "ride_type": "GrabCar",
            })

            if result.data:
                actions.append(
                    SuggestedAction(
                        id=uuid.uuid4(),
                        type=ActionType.BOOK_RIDE,
                        label=f"Đặt xe đến {to_stop.get('name', 'điểm tiếp theo')}",
                        description=f"Khoảng {result.data['distance_km']} km, {result.data['duration_minutes']} phút",
                        from_stop_index=i,
                        to_stop_index=i + 1,
                        provider="grab",
                        estimate_price=result.data["estimate_price"],
                        duration_minutes=result.data["duration_minutes"],
                        params=RideActionParams(
                            from_lat=from_stop["lat"],
                            from_lng=from_stop["lng"],
                            from_name=from_stop.get("name", ""),
                            to_lat=to_stop["lat"],
                            to_lng=to_stop["lng"],
                            to_name=to_stop.get("name", ""),
                        ).model_dump(),
                    )
                )

        return actions

    async def generate_all_actions(
        self,
        stops: list[dict],
    ) -> list[SuggestedAction]:
        """
        Generate all suggested actions for an itinerary.

        Args:
            stops: List of stops

        Returns:
            All suggested actions
        """
        actions = []

        # Add ride actions
        ride_actions = await self.generate_ride_actions(stops)
        actions.extend(ride_actions)

        # TODO: Add hotel, ticket actions in future phases

        return actions


# Singleton instance
mcp_service = MCPService()
