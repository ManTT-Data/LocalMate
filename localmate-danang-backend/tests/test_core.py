"""Tests for core endpoints (health, root)."""

import pytest
from httpx import AsyncClient


class TestHealthEndpoint:
    """Test cases for /health endpoint."""

    @pytest.mark.asyncio
    async def test_health_check_returns_200(self, client: AsyncClient):
        """Health check should return 200 OK."""
        response = await client.get("/health")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_health_check_has_status_field(self, client: AsyncClient):
        """Health check should have status field."""
        response = await client.get("/health")
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_health_check_has_version(self, client: AsyncClient):
        """Health check should have version field."""
        response = await client.get("/health")
        data = response.json()
        assert "version" in data
        assert data["version"] == "0.1.0"

    @pytest.mark.asyncio
    async def test_health_check_has_services(self, client: AsyncClient):
        """Health check should have services status."""
        response = await client.get("/health")
        data = response.json()
        assert "services" in data
        assert "neo4j" in data["services"]


class TestRootEndpoint:
    """Test cases for / endpoint."""

    @pytest.mark.asyncio
    async def test_root_returns_200(self, client: AsyncClient):
        """Root endpoint should return 200 OK."""
        response = await client.get("/")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_root_has_api_info(self, client: AsyncClient):
        """Root should return API information."""
        response = await client.get("/")
        data = response.json()
        assert "name" in data
        assert "LocalMate" in data["name"]
        assert "version" in data
        assert "docs" in data
        assert data["docs"] == "/docs"
