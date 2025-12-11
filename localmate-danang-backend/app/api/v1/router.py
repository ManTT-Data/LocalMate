"""API v1 router - aggregates all API endpoints."""

from fastapi import APIRouter

from app.guide_app.api.router import router as guide_router
from app.planner_app.api.router import router as planner_router

api_router = APIRouter()

api_router.include_router(
    planner_router,
    prefix="/planner",
    tags=["planner"],
)

api_router.include_router(
    guide_router,
    prefix="/guide",
    tags=["guide"],
)
