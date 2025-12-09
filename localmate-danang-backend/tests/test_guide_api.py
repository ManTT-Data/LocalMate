"""Tests for Guide API endpoints."""

import pytest
from httpx import AsyncClient


class TestGuideEndpointsAuth:
    """Test authentication for Guide endpoints."""

    @pytest.mark.asyncio
    async def test_fun_fact_requires_auth(self, client: AsyncClient):
        """POST /fun-fact should require authentication."""
        response = await client.post(
            "/api/v1/guide/fun-fact",
            json={"place_id": "test-place"}
        )
        assert response.status_code == 401  # Unauthorized without token

    @pytest.mark.asyncio
    async def test_tips_requires_auth(self, client: AsyncClient):
        """POST /tips should require authentication."""
        response = await client.post(
            "/api/v1/guide/tips",
            json={"place_id": "test-place"}
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_language_card_requires_auth(self, client: AsyncClient):
        """POST /language-card should require authentication."""
        response = await client.post(
            "/api/v1/guide/language-card",
            json={"phrase_type": "greeting"}
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_content_requires_auth(self, client: AsyncClient):
        """POST /content should require authentication."""
        response = await client.post(
            "/api/v1/guide/content",
            json={"place_id": "test-place"}
        )
        assert response.status_code == 401
