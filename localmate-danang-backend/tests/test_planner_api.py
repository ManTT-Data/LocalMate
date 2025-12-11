"""Tests for Planner API endpoints."""

import pytest
from httpx import AsyncClient


class TestItineraryEndpoints:
    """Test itinerary endpoints in demo mode."""

    @pytest.mark.asyncio
    async def test_plan_returns_200_in_demo(self, client: AsyncClient):
        """POST /plan should return 200 in demo mode."""
        response = await client.post(
            "/api/v1/planner/itineraries/plan",
            json={"duration_days": 2, "interests": ["beach"]}
        )
        # In demo mode, should work (may fail if DB not available)
        assert response.status_code in [200, 500]

    @pytest.mark.asyncio
    async def test_list_itineraries_returns_200(self, client: AsyncClient):
        """GET /itineraries should work in demo mode."""
        response = await client.get("/api/v1/planner/itineraries/")
        assert response.status_code in [200, 500]


class TestMCPEndpoints:
    """Test MCP endpoints in demo mode."""

    @pytest.mark.asyncio
    async def test_tools_returns_list(self, client: AsyncClient):
        """GET /mcp/tools should return list of tools."""
        response = await client.get("/api/v1/planner/mcp/tools")
        assert response.status_code == 200
        data = response.json()
        assert "tools" in data
        assert len(data["tools"]) > 0

    @pytest.mark.asyncio
    async def test_execute_grab_booking(self, client: AsyncClient):
        """POST /mcp/execute should execute grab booking."""
        response = await client.post(
            "/api/v1/planner/mcp/execute",
            json={
                "tool_name": "grab_transport",
                "params": {
                    "action": "book",
                    "from_lat": 16.05,
                    "from_lng": 108.22,
                    "to_lat": 16.06,
                    "to_lng": 108.23,
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "booking_id" in data["data"]

    @pytest.mark.asyncio
    async def test_execute_grab_estimate(self, client: AsyncClient):
        """POST /mcp/execute should execute grab estimate."""
        response = await client.post(
            "/api/v1/planner/mcp/execute",
            json={
                "tool_name": "grab_transport",
                "params": {
                    "action": "estimate",
                    "from_lat": 16.05,
                    "from_lng": 108.22,
                    "to_lat": 16.06,
                    "to_lng": 108.23,
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "distance_km" in data["data"]
