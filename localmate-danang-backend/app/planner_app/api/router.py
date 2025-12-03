"""
Planner App Router

Main router for Planner App endpoints
"""

from fastapi import APIRouter
from app.planner_app.api import routes_itineraries

router = APIRouter()

# Include route modules
router.include_router(routes_itineraries.router, prefix="/itineraries", tags=["Itineraries"])


@router.get("/health")
async def planner_health():
    """Health check for Planner App"""
    return {"status": "healthy", "app": "planner"}
