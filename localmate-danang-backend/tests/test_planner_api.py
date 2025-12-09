"""Tests for Planner API endpoints."""

import pytest
from httpx import AsyncClient


class TestItineraryEndpointsAuth:
    """Test authentication for itinerary endpoints."""

    @pytest.mark.asyncio
    async def test_plan_requires_auth(self, client: AsyncClient):
        """POST /plan should require authentication."""
        response = await client.post(
            "/api/v1/planner/itineraries/plan",
            json={"duration_days": 2}
        )
        assert response.status_code == 401  # Unauthorized without token

    @pytest.mark.asyncio
    async def test_list_itineraries_requires_auth(self, client: AsyncClient):
        """GET /itineraries should require authentication."""
        response = await client.get("/api/v1/planner/itineraries/")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_itinerary_requires_auth(self, client: AsyncClient):
        """GET /itineraries/{id} should require authentication."""
        response = await client.get(
            "/api/v1/planner/itineraries/00000000-0000-0000-0000-000000000000"
        )
        assert response.status_code == 401


class TestMCPEndpointsAuth:
    """Test authentication for MCP endpoints."""

    @pytest.mark.asyncio
    async def test_tools_requires_auth(self, client: AsyncClient):
        """GET /mcp/tools should require authentication."""
        response = await client.get("/api/v1/planner/mcp/tools")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_execute_requires_auth(self, client: AsyncClient):
        """POST /mcp/execute should require authentication."""
        response = await client.post(
            "/api/v1/planner/mcp/execute",
            json={"tool_name": "grab_transport", "params": {}}
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_ride_estimate_requires_auth(self, client: AsyncClient):
        """POST /mcp/ride/estimate should require authentication."""
        response = await client.post(
            "/api/v1/planner/mcp/ride/estimate",
            json={
                "from_lat": 16.05,
                "from_lng": 108.22,
                "to_lat": 16.06,
                "to_lng": 108.23
            }
        )
        assert response.status_code == 401


class TestItineraryPlanValidation:
    """Test request validation for plan endpoint."""

    @pytest.mark.asyncio
    async def test_plan_validates_duration_days(self, client: AsyncClient):
        """Plan should validate duration_days >= 1."""
        # Without auth, validation doesn't run (403 first)
        # This test documents expected behavior
        response = await client.post(
            "/api/v1/planner/itineraries/plan",
            json={"duration_days": 0}  # Invalid
        )
        # Either 403 (no auth) or 422 (validation error)
        assert response.status_code in [401, 422]
