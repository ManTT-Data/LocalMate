"""Planner App router - aggregates all planner endpoints."""

from fastapi import APIRouter

from .itineraries_router import router as itineraries_router
from .mcp_router import router as mcp_router

router = APIRouter()

router.include_router(
    itineraries_router,
    prefix="/itineraries",
    tags=["itineraries"],
)

router.include_router(
    mcp_router,
    prefix="/mcp",
    tags=["mcp"],
)
