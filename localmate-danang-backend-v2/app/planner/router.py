"""Trip Planner Router - API endpoints for plan management."""

from fastapi import APIRouter, HTTPException, Query

from app.planner.models import (
    Plan,
    PlanItem,
    CreatePlanRequest,
    CreatePlanResponse,
    AddPlaceRequest,
    ReorderRequest,
    ReplaceRequest,
    OptimizeResponse,
    PlanResponse,
)
from app.planner.service import planner_service


router = APIRouter(prefix="/planner", tags=["Trip Planner"])


@router.post(
    "/create",
    response_model=CreatePlanResponse,
    summary="Create a new trip plan",
    description="Creates an empty trip plan for the user.",
)
async def create_plan(
    request: CreatePlanRequest,
    user_id: str = Query(default="anonymous", description="User ID"),
) -> CreatePlanResponse:
    """Create a new empty plan."""
    plan = planner_service.create_plan(user_id=user_id, name=request.name)
    
    return CreatePlanResponse(
        plan_id=plan.plan_id,
        name=plan.name,
        message=f"Created plan '{plan.name}'",
    )


@router.get(
    "/{plan_id}",
    response_model=PlanResponse,
    summary="Get a trip plan",
    description="Retrieves a plan by ID.",
)
async def get_plan(
    plan_id: str,
    user_id: str = Query(default="anonymous", description="User ID"),
) -> PlanResponse:
    """Get a plan by ID."""
    plan = planner_service.get_plan(user_id=user_id, plan_id=plan_id)
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    return PlanResponse(plan=plan, message="Plan retrieved")


@router.get(
    "/user/plans",
    response_model=list[Plan],
    summary="Get all user plans",
    description="Retrieves all plans for a user.",
)
async def get_user_plans(
    user_id: str = Query(default="anonymous", description="User ID"),
) -> list[Plan]:
    """Get all plans for a user."""
    return planner_service.get_user_plans(user_id)


@router.post(
    "/{plan_id}/add",
    response_model=PlanItem,
    summary="Add a place to plan",
    description="Adds a new place to the end of the plan.",
)
async def add_place(
    plan_id: str,
    request: AddPlaceRequest,
    user_id: str = Query(default="anonymous", description="User ID"),
) -> PlanItem:
    """Add a place to the plan."""
    # Try to find existing plan or create default
    plan = planner_service.get_plan(user_id, plan_id)
    if not plan:
        # Auto-create plan if it doesn't exist
        plan = planner_service.create_plan(user_id=user_id)
    
    item = planner_service.add_place(
        user_id=user_id,
        plan_id=plan.plan_id,
        place=request.place,
        notes=request.notes,
    )
    
    if not item:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    return item


@router.delete(
    "/{plan_id}/remove/{item_id}",
    summary="Remove a place from plan",
    description="Removes a place from the plan by item ID.",
)
async def remove_place(
    plan_id: str,
    item_id: str,
    user_id: str = Query(default="anonymous", description="User ID"),
) -> dict:
    """Remove a place from the plan."""
    success = planner_service.remove_place(
        user_id=user_id,
        plan_id=plan_id,
        item_id=item_id,
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return {"status": "success", "message": f"Removed item {item_id}"}


@router.put(
    "/{plan_id}/reorder",
    response_model=PlanResponse,
    summary="Reorder places in plan",
    description="Manually reorder places by providing new order of item IDs.",
)
async def reorder_places(
    plan_id: str,
    request: ReorderRequest,
    user_id: str = Query(default="anonymous", description="User ID"),
) -> PlanResponse:
    """Reorder places in the plan."""
    success = planner_service.reorder_places(
        user_id=user_id,
        plan_id=plan_id,
        new_order=request.new_order,
    )
    
    if not success:
        raise HTTPException(
            status_code=400, 
            detail="Invalid order. Ensure all item IDs are included."
        )
    
    plan = planner_service.get_plan(user_id, plan_id)
    return PlanResponse(plan=plan, message="Plan reordered")


@router.post(
    "/{plan_id}/optimize",
    response_model=OptimizeResponse,
    summary="Optimize route (TSP)",
    description="""
Optimizes the route using TSP (Traveling Salesman Problem) algorithm.

Uses Nearest Neighbor heuristic with 2-opt improvement.
Minimizes total travel distance.
""",
)
async def optimize_route(
    plan_id: str,
    user_id: str = Query(default="anonymous", description="User ID"),
    start_index: int = Query(default=0, description="Index of starting place"),
) -> OptimizeResponse:
    """Optimize the route using TSP."""
    # Get original distance for comparison
    plan = planner_service.get_plan(user_id, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    if len(plan.items) < 2:
        return OptimizeResponse(
            plan_id=plan_id,
            items=plan.items,
            total_distance_km=0,
            estimated_duration_min=0,
            message="Need at least 2 places to optimize",
        )
    
    original_distance = plan.total_distance_km or 0
    
    # Optimize
    optimized_plan = planner_service.optimize_plan(
        user_id=user_id,
        plan_id=plan_id,
        start_index=start_index,
    )
    
    if not optimized_plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    # Calculate savings
    distance_saved = original_distance - optimized_plan.total_distance_km if original_distance > 0 else None
    
    return OptimizeResponse(
        plan_id=plan_id,
        items=optimized_plan.items,
        total_distance_km=optimized_plan.total_distance_km,
        estimated_duration_min=optimized_plan.estimated_duration_min,
        distance_saved_km=round(distance_saved, 2) if distance_saved else None,
        message=f"Route optimized! Total: {optimized_plan.total_distance_km}km, ~{optimized_plan.estimated_duration_min}min",
    )


@router.put(
    "/{plan_id}/replace/{item_id}",
    response_model=PlanItem,
    summary="Replace a place in plan",
    description="Replaces an existing place with a new one.",
)
async def replace_place(
    plan_id: str,
    item_id: str,
    request: ReplaceRequest,
    user_id: str = Query(default="anonymous", description="User ID"),
) -> PlanItem:
    """Replace a place in the plan."""
    item = planner_service.replace_place(
        user_id=user_id,
        plan_id=plan_id,
        item_id=item_id,
        new_place=request.new_place,
    )
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return item


@router.delete(
    "/{plan_id}",
    summary="Delete a plan",
    description="Deletes an entire plan.",
)
async def delete_plan(
    plan_id: str,
    user_id: str = Query(default="anonymous", description="User ID"),
) -> dict:
    """Delete a plan."""
    success = planner_service.delete_plan(user_id=user_id, plan_id=plan_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    return {"status": "success", "message": f"Deleted plan {plan_id}"}
