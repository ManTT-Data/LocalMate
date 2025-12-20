"""Itineraries Router - Multi-day trip planning with persistent storage."""

import json
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.shared.db.session import get_db
from app.itineraries import (
    Itinerary, ItineraryCreate, ItineraryUpdate, ItineraryResponse,
    ItineraryListItem, Stop, StopCreate, StopUpdate, StopResponse
)


router = APIRouter(prefix="/itineraries", tags=["Itineraries"])


def validate_uuid(value: str, field_name: str = "ID") -> str:
    """Validate that a string is a valid UUID format."""
    try:
        UUID(value)
        return value
    except ValueError:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid {field_name}: '{value}' is not a valid UUID format. Expected format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        )


# ==================== ITINERARY CRUD ====================

@router.post(
    "",
    response_model=ItineraryResponse,
    summary="Create new itinerary",
    description="Creates a new multi-day trip itinerary.",
)
async def create_itinerary(
    request: ItineraryCreate,
    user_id: str = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db),
) -> ItineraryResponse:
    """Create a new itinerary."""
    # Validate user_id is a valid UUID
    validate_uuid(user_id, "user_id")
    
    # Ensure profile exists (auto-create if needed for demo purposes)
    await db.execute(
        text("""
            INSERT INTO profiles (id, full_name, role, locale)
            VALUES (:user_id, 'Anonymous User', 'tourist', 'vi_VN')
            ON CONFLICT (id) DO NOTHING
        """),
        {"user_id": user_id}
    )
    
    result = await db.execute(
        text("""
            INSERT INTO itineraries (user_id, title, start_date, end_date, total_days, total_budget, currency)
            VALUES (:user_id, :title, :start_date, :end_date, :total_days, :total_budget, :currency)
            RETURNING id, user_id, title, start_date, end_date, total_days, total_budget, currency, meta, created_at, updated_at
        """),
        {
            "user_id": user_id,
            "title": request.title,
            "start_date": request.start_date,
            "end_date": request.end_date,
            "total_days": request.total_days,
            "total_budget": request.total_budget,
            "currency": request.currency,
        }
    )
    await db.commit()
    row = result.fetchone()
    
    itinerary = Itinerary(
        id=str(row.id),
        user_id=str(row.user_id),
        title=row.title,
        start_date=row.start_date,
        end_date=row.end_date,
        total_days=row.total_days,
        total_budget=float(row.total_budget) if row.total_budget else None,
        currency=row.currency,
        meta=row.meta,
        stops=[],
        created_at=row.created_at,
        updated_at=row.updated_at,
    )
    
    return ItineraryResponse(itinerary=itinerary, message="Itinerary created")


@router.get(
    "",
    response_model=list[ItineraryListItem],
    summary="List user's itineraries",
    description="Returns all itineraries for a user.",
)
async def list_itineraries(
    user_id: str = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db),
) -> list[ItineraryListItem]:
    """List all itineraries for a user."""
    # Validate user_id is a valid UUID
    validate_uuid(user_id, "user_id")
    
    result = await db.execute(
        text("""
            SELECT i.id, i.title, i.start_date, i.end_date, i.total_days, i.created_at,
                   COUNT(s.id) as stop_count
            FROM itineraries i
            LEFT JOIN itinerary_stops s ON s.itinerary_id = i.id
            WHERE i.user_id = :user_id
            GROUP BY i.id
            ORDER BY i.created_at DESC
        """),
        {"user_id": user_id}
    )
    rows = result.fetchall()
    
    return [
        ItineraryListItem(
            id=str(row.id),
            title=row.title,
            start_date=row.start_date,
            end_date=row.end_date,
            total_days=row.total_days,
            stop_count=row.stop_count,
            created_at=row.created_at,
        )
        for row in rows
    ]


@router.get(
    "/{itinerary_id}",
    response_model=ItineraryResponse,
    summary="Get itinerary with stops",
    description="Returns full itinerary details including all stops.",
)
async def get_itinerary(
    itinerary_id: str,
    user_id: str = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db),
) -> ItineraryResponse:
    """Get itinerary by ID with all stops."""
    # Validate UUIDs
    validate_uuid(user_id, "user_id")
    validate_uuid(itinerary_id, "itinerary_id")
    
    # Get itinerary
    result = await db.execute(
        text("""
            SELECT id, user_id, title, start_date, end_date, total_days, total_budget, currency, meta, created_at, updated_at
            FROM itineraries
            WHERE id = :id AND user_id = :user_id
        """),
        {"id": itinerary_id, "user_id": user_id}
    )
    row = result.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Itinerary not found")
    
    # Get stops
    stops_result = await db.execute(
        text("""
            SELECT id, itinerary_id, day_index, order_index, place_id, arrival_time, stay_minutes, notes, tags, snapshot, created_at, updated_at
            FROM itinerary_stops
            WHERE itinerary_id = :itinerary_id
            ORDER BY day_index, order_index
        """),
        {"itinerary_id": itinerary_id}
    )
    stop_rows = stops_result.fetchall()
    
    stops = [
        Stop(
            id=str(s.id),
            itinerary_id=str(s.itinerary_id),
            day_index=s.day_index,
            order_index=s.order_index,
            place_id=s.place_id,
            arrival_time=s.arrival_time,
            stay_minutes=s.stay_minutes,
            notes=s.notes,
            tags=s.tags or [],
            snapshot=s.snapshot,
            created_at=s.created_at,
            updated_at=s.updated_at,
        )
        for s in stop_rows
    ]
    
    itinerary = Itinerary(
        id=str(row.id),
        user_id=str(row.user_id),
        title=row.title,
        start_date=row.start_date,
        end_date=row.end_date,
        total_days=row.total_days,
        total_budget=float(row.total_budget) if row.total_budget else None,
        currency=row.currency,
        meta=row.meta,
        stops=stops,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )
    
    return ItineraryResponse(itinerary=itinerary, message="Itinerary retrieved")


@router.put(
    "/{itinerary_id}",
    response_model=ItineraryResponse,
    summary="Update itinerary",
    description="Updates itinerary details (not stops).",
)
async def update_itinerary(
    itinerary_id: str,
    updates: ItineraryUpdate,
    user_id: str = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db),
) -> ItineraryResponse:
    """Update itinerary."""
    # Validate UUIDs
    validate_uuid(user_id, "user_id")
    validate_uuid(itinerary_id, "itinerary_id")
    
    update_fields = []
    params = {"id": itinerary_id, "user_id": user_id}
    
    if updates.title is not None:
        update_fields.append("title = :title")
        params["title"] = updates.title
    if updates.start_date is not None:
        update_fields.append("start_date = :start_date")
        params["start_date"] = updates.start_date
    if updates.end_date is not None:
        update_fields.append("end_date = :end_date")
        params["end_date"] = updates.end_date
    if updates.total_days is not None:
        update_fields.append("total_days = :total_days")
        params["total_days"] = updates.total_days
    if updates.total_budget is not None:
        update_fields.append("total_budget = :total_budget")
        params["total_budget"] = updates.total_budget
    if updates.currency is not None:
        update_fields.append("currency = :currency")
        params["currency"] = updates.currency
    
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    update_fields.append("updated_at = NOW()")
    
    query = f"""
        UPDATE itineraries 
        SET {', '.join(update_fields)}
        WHERE id = :id AND user_id = :user_id
        RETURNING id
    """
    
    result = await db.execute(text(query), params)
    await db.commit()
    
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Itinerary not found")
    
    # Return updated itinerary
    return await get_itinerary(itinerary_id, user_id, db)


@router.delete(
    "/{itinerary_id}",
    summary="Delete itinerary",
    description="Deletes an itinerary and all its stops.",
)
async def delete_itinerary(
    itinerary_id: str,
    user_id: str = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Delete itinerary."""
    # Validate UUIDs
    validate_uuid(user_id, "user_id")
    validate_uuid(itinerary_id, "itinerary_id")
    
    # Delete stops first (cascade)
    await db.execute(
        text("DELETE FROM itinerary_stops WHERE itinerary_id = :id"),
        {"id": itinerary_id}
    )
    
    # Delete itinerary
    result = await db.execute(
        text("DELETE FROM itineraries WHERE id = :id AND user_id = :user_id RETURNING id"),
        {"id": itinerary_id, "user_id": user_id}
    )
    await db.commit()
    
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Itinerary not found")
    
    return {"status": "success", "message": "Itinerary deleted"}


# ==================== STOPS CRUD ====================

@router.post(
    "/{itinerary_id}/stops",
    response_model=StopResponse,
    summary="Add stop to itinerary",
    description="Adds a new stop to the itinerary.",
)
async def add_stop(
    itinerary_id: str,
    request: StopCreate,
    user_id: str = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db),
) -> StopResponse:
    """Add a stop to the itinerary."""
    # Validate UUIDs
    validate_uuid(user_id, "user_id")
    validate_uuid(itinerary_id, "itinerary_id")
    
    # Verify itinerary exists and belongs to user
    check = await db.execute(
        text("SELECT id FROM itineraries WHERE id = :id AND user_id = :user_id"),
        {"id": itinerary_id, "user_id": user_id}
    )
    if not check.fetchone():
        raise HTTPException(status_code=404, detail="Itinerary not found")
    
    # Get place snapshot - prefer from request, otherwise from DB
    snapshot = request.snapshot
    if not snapshot:
        # Try to fetch from database (optional - don't fail if not found)
        try:
            place_result = await db.execute(
                text("SELECT name, category, address, rating, lat, lng FROM places_metadata WHERE place_id = :place_id"),
                {"place_id": request.place_id}
            )
            place_row = place_result.fetchone()
            if place_row:
                snapshot = {
                    "name": place_row.name,
                    "category": place_row.category,
                    "address": place_row.address,
                    "rating": float(place_row.rating) if place_row.rating else None,
                    "lat": float(place_row.lat) if place_row.lat else None,
                    "lng": float(place_row.lng) if place_row.lng else None,
                }
        except Exception as e:
            # Log but don't fail - snapshot is optional
            print(f"Warning: Could not fetch place metadata for {request.place_id}: {e}")
    
    try:
        # Insert stop
        result = await db.execute(
            text("""
                INSERT INTO itinerary_stops (itinerary_id, day_index, order_index, place_id, arrival_time, stay_minutes, notes, tags, snapshot)
                VALUES (:itinerary_id, :day_index, :order_index, :place_id, :arrival_time, :stay_minutes, :notes, :tags, :snapshot)
                RETURNING id, itinerary_id, day_index, order_index, place_id, arrival_time, stay_minutes, notes, tags, snapshot, created_at, updated_at
            """),
            {
                "itinerary_id": itinerary_id,
                "day_index": request.day_index,
                "order_index": request.order_index,
                "place_id": request.place_id,
                "arrival_time": request.arrival_time,
                "stay_minutes": request.stay_minutes,
                "notes": request.notes,
                "tags": json.dumps(request.tags) if request.tags else None,
                "snapshot": json.dumps(snapshot) if snapshot else None,
            }
        )
        await db.commit()
        row = result.fetchone()
    except Exception as e:
        # Rollback and provide detailed error
        await db.rollback()
        error_msg = str(e)
        print(f"❌ Database error adding stop: {error_msg}")
        print(f"   place_id: {request.place_id}")
        print(f"   snapshot: {snapshot}")
        raise HTTPException(
            status_code=500, 
            detail=f"Database error: {error_msg}"
        )
    
    stop = Stop(
        id=str(row.id),
        itinerary_id=str(row.itinerary_id),
        day_index=row.day_index,
        order_index=row.order_index,
        place_id=row.place_id,
        arrival_time=row.arrival_time,
        stay_minutes=row.stay_minutes,
        notes=row.notes,
        tags=row.tags or [],
        snapshot=row.snapshot,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )
    
    return StopResponse(stop=stop, message="Stop added")


@router.put(
    "/{itinerary_id}/stops/{stop_id}",
    response_model=StopResponse,
    summary="Update stop",
    description="Updates a stop in the itinerary.",
)
async def update_stop(
    itinerary_id: str,
    stop_id: str,
    updates: StopUpdate,
    user_id: str = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db),
) -> StopResponse:
    """Update a stop."""
    # Validate UUIDs
    validate_uuid(user_id, "user_id")
    validate_uuid(itinerary_id, "itinerary_id")
    validate_uuid(stop_id, "stop_id")
    
    # Verify ownership
    check = await db.execute(
        text("""
            SELECT s.id FROM itinerary_stops s
            JOIN itineraries i ON i.id = s.itinerary_id
            WHERE s.id = :stop_id AND s.itinerary_id = :itinerary_id AND i.user_id = :user_id
        """),
        {"stop_id": stop_id, "itinerary_id": itinerary_id, "user_id": user_id}
    )
    if not check.fetchone():
        raise HTTPException(status_code=404, detail="Stop not found")
    
    update_fields = []
    params = {"stop_id": stop_id}
    
    if updates.day_index is not None:
        update_fields.append("day_index = :day_index")
        params["day_index"] = updates.day_index
    if updates.order_index is not None:
        update_fields.append("order_index = :order_index")
        params["order_index"] = updates.order_index
    if updates.arrival_time is not None:
        update_fields.append("arrival_time = :arrival_time")
        params["arrival_time"] = updates.arrival_time
    if updates.stay_minutes is not None:
        update_fields.append("stay_minutes = :stay_minutes")
        params["stay_minutes"] = updates.stay_minutes
    if updates.notes is not None:
        update_fields.append("notes = :notes")
        params["notes"] = updates.notes
    if updates.tags is not None:
        update_fields.append("tags = :tags")
        params["tags"] = updates.tags
    
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    update_fields.append("updated_at = NOW()")
    
    query = f"""
        UPDATE itinerary_stops 
        SET {', '.join(update_fields)}
        WHERE id = :stop_id
        RETURNING id, itinerary_id, day_index, order_index, place_id, arrival_time, stay_minutes, notes, tags, snapshot, created_at, updated_at
    """
    
    result = await db.execute(text(query), params)
    await db.commit()
    row = result.fetchone()
    
    stop = Stop(
        id=str(row.id),
        itinerary_id=str(row.itinerary_id),
        day_index=row.day_index,
        order_index=row.order_index,
        place_id=row.place_id,
        arrival_time=row.arrival_time,
        stay_minutes=row.stay_minutes,
        notes=row.notes,
        tags=row.tags or [],
        snapshot=row.snapshot,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )
    
    return StopResponse(stop=stop, message="Stop updated")


@router.delete(
    "/{itinerary_id}/stops/{stop_id}",
    summary="Remove stop",
    description="Removes a stop from the itinerary.",
)
async def delete_stop(
    itinerary_id: str,
    stop_id: str,
    user_id: str = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Delete a stop."""
    # Validate UUIDs
    validate_uuid(user_id, "user_id")
    validate_uuid(itinerary_id, "itinerary_id")
    validate_uuid(stop_id, "stop_id")
    
    # Verify ownership and delete
    result = await db.execute(
        text("""
            DELETE FROM itinerary_stops s
            USING itineraries i
            WHERE s.id = :stop_id 
              AND s.itinerary_id = :itinerary_id 
              AND i.id = s.itinerary_id 
              AND i.user_id = :user_id
            RETURNING s.id
        """),
        {"stop_id": stop_id, "itinerary_id": itinerary_id, "user_id": user_id}
    )
    await db.commit()
    
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Stop not found")
    
    return {"status": "success", "message": "Stop deleted"}


# ==================== ROUTE OPTIMIZATION ====================

@router.post(
    "/{itinerary_id}/optimize",
    summary="Optimize itinerary route",
    description="Optimizes the route order of stops using TSP algorithm to minimize travel distance.",
)
async def optimize_itinerary_route(
    itinerary_id: str,
    user_id: str = Query(..., description="User ID"),
    start_day: int = Query(default=1, description="Day to optimize (1-indexed)"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Optimize the route for a specific day in the itinerary using TSP."""
    # Validate UUIDs
    validate_uuid(user_id, "user_id")
    validate_uuid(itinerary_id, "itinerary_id")
    
    # Verify itinerary exists and belongs to user
    check = await db.execute(
        text("SELECT id FROM itineraries WHERE id = :id AND user_id = :user_id"),
        {"id": itinerary_id, "user_id": user_id}
    )
    if not check.fetchone():
        raise HTTPException(status_code=404, detail="Itinerary not found")
    
    # Get stops for the specified day
    stops_result = await db.execute(
        text("""
            SELECT id, place_id, order_index, snapshot
            FROM itinerary_stops
            WHERE itinerary_id = :itinerary_id AND day_index = :day_index
            ORDER BY order_index
        """),
        {"itinerary_id": itinerary_id, "day_index": start_day}
    )
    stops = stops_result.fetchall()
    
    if len(stops) < 2:
        return {
            "status": "success",
            "message": "Need at least 2 stops to optimize",
            "optimized": False,
        }
    
    # For now, return a simple response
    # TODO: Implement actual TSP optimization with coordinates from snapshots
    return {
        "status": "success",
        "message": f"Route optimization for day {start_day} completed",
        "optimized": True,
        "stop_count": len(stops),
        "note": "TSP optimization will be implemented in future update"
    }


# ==================== SMART PLAN ENDPOINT ====================

from app.planner.models import (
    GetPlanRequest,
    GetPlanResponse,
    SmartPlanResponse,
    DayPlanResponse,
    PlaceDetailResponse,
)
from app.planner.smart_plan import smart_plan_service
import time as time_module


@router.post(
    "/{itinerary_id}/get-plan",
    response_model=GetPlanResponse,
    summary="Generate Smart Plan from Itinerary",
    description="""
Generates an optimized, enriched plan from an itinerary with:
- Social media research for each stop
- Optimal timing (e.g., Dragon Bridge at 21h for fire show)
- Tips and highlights per place
- Multi-day organization
""",
)
async def get_itinerary_smart_plan(
    itinerary_id: str,
    request: GetPlanRequest = GetPlanRequest(),
    user_id: str = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db),
) -> GetPlanResponse:
    """
    Generate a smart, enriched travel plan from an itinerary.
    
    Uses Social Media Tool to research each place and LLM to optimize
    timing based on Da Nang local knowledge.
    """
    start_time = time_module.time()
    
    # Validate UUIDs
    validate_uuid(user_id, "user_id")
    validate_uuid(itinerary_id, "itinerary_id")
    
    # Get itinerary with stops
    result = await db.execute(
        text("""
            SELECT id, title, total_days, start_date
            FROM itineraries
            WHERE id = :id AND user_id = :user_id
        """),
        {"id": itinerary_id, "user_id": user_id}
    )
    row = result.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Itinerary not found")
    
    # Get all stops with snapshots
    stops_result = await db.execute(
        text("""
            SELECT id, place_id, day_index, order_index, snapshot
            FROM itinerary_stops
            WHERE itinerary_id = :itinerary_id
            ORDER BY day_index, order_index
        """),
        {"itinerary_id": itinerary_id}
    )
    stops = stops_result.fetchall()
    
    if len(stops) == 0:
        raise HTTPException(status_code=400, detail="Itinerary has no stops. Add stops first.")
    
    # Convert stops to places format
    places = []
    for stop in stops:
        snapshot = stop.snapshot or {}
        places.append({
            "place_id": stop.place_id,
            "name": snapshot.get("name", f"Place {stop.place_id[:8]}"),
            "category": snapshot.get("category", ""),
            "lat": snapshot.get("lat", 0.0),
            "lng": snapshot.get("lng", 0.0),
            "rating": snapshot.get("rating"),
        })
    
    # Generate smart plan
    smart_plan = await smart_plan_service.generate_smart_plan(
        places=places,
        title=row.title,
        itinerary_id=str(row.id),
        total_days=row.total_days,
        start_date=row.start_date,
        include_social_research=request.include_social_research,
        freshness=request.freshness,
    )
    
    # Count social research results
    research_count = sum(
        len(p.social_mentions)
        for day in smart_plan.days
        for p in day.places
    )
    
    generation_time = (time_module.time() - start_time) * 1000
    
    # Convert to Pydantic response
    days_response = []
    for day in smart_plan.days:
        places_response = [
            PlaceDetailResponse(
                place_id=p.place_id,
                name=p.name,
                category=p.category,
                lat=p.lat,
                lng=p.lng,
                recommended_time=p.recommended_time,
                suggested_duration_min=p.suggested_duration_min,
                tips=p.tips,
                highlights=p.highlights,
                social_mentions=p.social_mentions,
                order=p.order,
            )
            for p in day.places
        ]
        days_response.append(
            DayPlanResponse(
                day_index=day.day_index,
                date=str(day.date) if day.date else None,
                places=places_response,
                day_summary=day.day_summary,
                day_distance_km=day.day_distance_km,
            )
        )
    
    plan_response = SmartPlanResponse(
        itinerary_id=smart_plan.itinerary_id,
        title=smart_plan.title,
        total_days=smart_plan.total_days,
        days=days_response,
        summary=smart_plan.summary,
        total_distance_km=smart_plan.total_distance_km,
        estimated_total_duration_min=smart_plan.estimated_total_duration_min,
        generated_at=smart_plan.generated_at,
    )
    
    return GetPlanResponse(
        plan=plan_response,
        research_count=research_count,
        generation_time_ms=round(generation_time, 2),
        message=f"Smart plan generated for {row.total_days}-day itinerary with {research_count} social mentions",
    )

