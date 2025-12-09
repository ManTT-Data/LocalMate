"""MCP Router - API endpoints for MCP actions."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.planner_app.schemas.action_schemas import SuggestedAction, SuggestedActionsResponse
from app.planner_app.services.itinerary_service import itinerary_service
from app.shared.db.session import get_db
from app.shared.integrations.mcp.mcp_service import mcp_service

router = APIRouter()


class ExecuteToolRequest(BaseModel):
    """Request to execute an MCP tool."""

    tool_name: str
    params: dict


class ExecuteToolResponse(BaseModel):
    """Response from tool execution."""

    status: str
    data: dict | None = None
    error: str | None = None


@router.get("/tools")
async def list_tools(
    _: dict = Depends(get_current_user),
):
    """List all available MCP tools."""
    return {"tools": mcp_service.list_tools()}


@router.post("/execute", response_model=ExecuteToolResponse)
async def execute_tool(
    request: ExecuteToolRequest,
    _: dict = Depends(get_current_user),
):
    """
    Execute an MCP tool.

    - **tool_name**: Name of the tool to execute
    - **params**: Tool-specific parameters
    """
    result = await mcp_service.execute_tool(request.tool_name, request.params)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tool '{request.tool_name}' not found",
        )

    return ExecuteToolResponse(
        status=result.status.value,
        data=result.data,
        error=result.error,
    )


@router.get(
    "/itineraries/{itinerary_id}/actions",
    response_model=SuggestedActionsResponse,
)
async def get_itinerary_actions(
    itinerary_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    """
    Get suggested actions for an itinerary.

    Returns ride booking actions between stops.
    """
    # Get itinerary
    itinerary = await itinerary_service.get_itinerary(db, itinerary_id)
    if not itinerary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Itinerary not found",
        )

    # Convert stops to dict format
    stops = [
        {
            "lat": stop.snapshot.get("lat", 0) if stop.snapshot else 0,
            "lng": stop.snapshot.get("lng", 0) if stop.snapshot else 0,
            "name": stop.snapshot.get("name", stop.place_id) if stop.snapshot else stop.place_id,
        }
        for stop in itinerary.stops
    ]

    # Generate actions
    actions = await mcp_service.generate_all_actions(stops)

    return SuggestedActionsResponse(
        itinerary_id=itinerary_id,
        actions=actions,
    )


class RideEstimateRequest(BaseModel):
    """Request for ride estimate."""

    from_lat: float
    from_lng: float
    to_lat: float
    to_lng: float
    ride_type: str = "GrabCar"


@router.post("/ride/estimate")
async def estimate_ride(
    request: RideEstimateRequest,
    _: dict = Depends(get_current_user),
):
    """
    Get a ride estimate between two points.

    - **from_lat, from_lng**: Pickup coordinates
    - **to_lat, to_lng**: Dropoff coordinates
    - **ride_type**: GrabCar, GrabBike, or GrabCar Plus
    """
    result = await mcp_service.execute_tool(
        "grab_transport",
        request.model_dump(),
    )

    if result and result.data:
        return result.data

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=result.error if result else "Failed to estimate ride",
    )
