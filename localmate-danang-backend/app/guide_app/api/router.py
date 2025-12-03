"""
Guide App Router

Main router for Guide App (Driver side)
"""

from fastapi import APIRouter
from app.guide_app.api import routes_driver_guide

router = APIRouter()

# Include route modules
router.include_router(routes_driver_guide.router, prefix="/guide-pack", tags=["Guide Pack"])


@router.get("/health")
async def guide_health():
    """Health check for Guide App"""
    return {"status": "healthy", "app": "guide"}
