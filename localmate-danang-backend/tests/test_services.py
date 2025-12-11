"""Tests for internal services and utilities."""

import pytest
from app.shared.utils.geo_utils import haversine_distance, bounding_box
from app.shared.graph.tsp_solver import nearest_neighbor_tsp, optimize_route
from app.shared.integrations.mcp.grab_transport_tool import GrabTransportTool
from app.shared.integrations.mcp.base_tool import ToolStatus


class TestGeoUtils:
    """Test geographic utility functions."""

    def test_haversine_same_point(self):
        """Distance between same point should be 0."""
        point = (16.0544, 108.2480)
        distance = haversine_distance(point, point)
        assert distance == 0.0

    def test_haversine_known_distance(self):
        """Test with known distance between two points."""
        # My Khe Beach to Dragon Bridge (~2km)
        my_khe = (16.0544, 108.2480)
        dragon_bridge = (16.0611, 108.2272)
        distance = haversine_distance(my_khe, dragon_bridge)
        # Should be approximately 2km
        assert 1.5 < distance < 3.0

    def test_haversine_symmetry(self):
        """Distance should be same in both directions."""
        point1 = (16.0544, 108.2480)
        point2 = (16.0611, 108.2272)
        d1 = haversine_distance(point1, point2)
        d2 = haversine_distance(point2, point1)
        assert d1 == d2

    def test_bounding_box_returns_tuple(self):
        """Bounding box should return 4 coordinates."""
        result = bounding_box(16.05, 108.22, 5.0)
        assert len(result) == 4
        min_lat, min_lng, max_lat, max_lng = result
        assert min_lat < 16.05 < max_lat
        assert min_lng < 108.22 < max_lng


class TestTSPSolver:
    """Test TSP optimization functions."""

    @pytest.mark.asyncio
    async def test_tsp_single_point(self):
        """TSP with single point should return [0]."""
        points = [(16.05, 108.22)]
        order = await nearest_neighbor_tsp(points)
        assert order == [0]

    @pytest.mark.asyncio
    async def test_tsp_two_points(self):
        """TSP with two points should return [0, 1]."""
        points = [(16.05, 108.22), (16.06, 108.23)]
        order = await nearest_neighbor_tsp(points)
        assert order == [0, 1]

    @pytest.mark.asyncio
    async def test_tsp_returns_all_indices(self):
        """TSP should visit all points."""
        points = [
            (16.05, 108.22),
            (16.06, 108.23),
            (16.07, 108.24),
        ]
        order = await nearest_neighbor_tsp(points)
        assert len(order) == 3
        assert set(order) == {0, 1, 2}

    @pytest.mark.asyncio
    async def test_optimize_route_empty(self):
        """Optimize route with empty list should return []."""
        order = await optimize_route([])
        assert order == []


class TestGrabTransportTool:
    """Test Grab transport MCP tool."""

    @pytest.fixture
    def tool(self):
        return GrabTransportTool()

    def test_tool_name(self, tool):
        """Tool should have correct name."""
        assert tool.name == "grab_transport"

    def test_tool_has_description(self, tool):
        """Tool should have description."""
        assert len(tool.description) > 0

    def test_tool_spec_has_parameters(self, tool):
        """Tool spec should have parameters."""
        spec = tool.get_tool_spec()
        assert "name" in spec
        assert "parameters" in spec
        assert "properties" in spec["parameters"]
        assert "action" in spec["parameters"]["properties"]

    @pytest.mark.asyncio
    async def test_book_ride(self, tool):
        """Book ride should return booking result."""
        result = await tool.book_ride(
            from_lat=16.05,
            from_lng=108.22,
            from_name="Điểm A",
            to_lat=16.06,
            to_lng=108.23,
            to_name="Điểm B",
        )
        assert result.provider == "grab"
        assert result.booking_id.startswith("GRAB-")
        assert result.status == "pending"
        assert "₫" in result.estimated_price

    @pytest.mark.asyncio
    async def test_execute_book_success(self, tool):
        """Execute book should return success."""
        result = await tool.execute({
            "action": "book",
            "from_lat": 16.05,
            "from_lng": 108.22,
            "to_lat": 16.06,
            "to_lng": 108.23,
        })
        assert result.status == ToolStatus.SUCCESS
        assert result.data is not None
        assert "booking_id" in result.data

    @pytest.mark.asyncio
    async def test_execute_estimate_success(self, tool):
        """Execute estimate should return success."""
        result = await tool.execute({
            "action": "estimate",
            "from_lat": 16.05,
            "from_lng": 108.22,
            "to_lat": 16.06,
            "to_lng": 108.23,
        })
        assert result.status == ToolStatus.SUCCESS
        assert result.data is not None
        assert "distance_km" in result.data

    @pytest.mark.asyncio
    async def test_execute_failure_missing_field(self, tool):
        """Execute should fail with missing fields."""
        result = await tool.execute({
            "action": "book",
            "from_lat": 16.05,
            # Missing other required fields
        })
        assert result.status == ToolStatus.FAILED
        assert "Missing" in result.error
