"""User Profile Router."""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.shared.db.session import get_db
from app.users import Profile, ProfileUpdate, ProfileResponse


router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=ProfileResponse,
    summary="Get current user profile",
    description="Returns the profile for the authenticated user.",
)
async def get_my_profile(
    user_id: str = Query(..., description="User ID (from auth)"),
    db: AsyncSession = Depends(get_db),
) -> ProfileResponse:
    """Get current user's profile."""
    result = await db.execute(
        text("""
            SELECT id, full_name, phone, role, locale, avatar_url, created_at, updated_at
            FROM profiles 
            WHERE id = :user_id
        """),
        {"user_id": user_id}
    )
    row = result.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    profile = Profile(
        id=str(row.id),
        full_name=row.full_name,
        phone=row.phone,
        role=row.role,
        locale=row.locale,
        avatar_url=row.avatar_url,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )
    
    return ProfileResponse(profile=profile, message="Profile retrieved")


@router.put(
    "/me",
    response_model=ProfileResponse,
    summary="Update current user profile",
    description="Updates the profile for the authenticated user.",
)
async def update_my_profile(
    updates: ProfileUpdate,
    user_id: str = Query(..., description="User ID (from auth)"),
    db: AsyncSession = Depends(get_db),
) -> ProfileResponse:
    """Update current user's profile."""
    # Build dynamic update query
    update_fields = []
    params = {"user_id": user_id}
    
    if updates.full_name is not None:
        update_fields.append("full_name = :full_name")
        params["full_name"] = updates.full_name
    if updates.phone is not None:
        update_fields.append("phone = :phone")
        params["phone"] = updates.phone
    if updates.locale is not None:
        update_fields.append("locale = :locale")
        params["locale"] = updates.locale
    if updates.avatar_url is not None:
        update_fields.append("avatar_url = :avatar_url")
        params["avatar_url"] = updates.avatar_url
    
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    update_fields.append("updated_at = NOW()")
    
    query = f"""
        UPDATE profiles 
        SET {', '.join(update_fields)}
        WHERE id = :user_id
        RETURNING id, full_name, phone, role, locale, avatar_url, created_at, updated_at
    """
    
    result = await db.execute(text(query), params)
    await db.commit()
    
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    profile = Profile(
        id=str(row.id),
        full_name=row.full_name,
        phone=row.phone,
        role=row.role,
        locale=row.locale,
        avatar_url=row.avatar_url,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )
    
    return ProfileResponse(profile=profile, message="Profile updated")


@router.get(
    "/{user_id}",
    response_model=ProfileResponse,
    summary="Get user profile by ID",
    description="Returns the profile for a specific user (admin only).",
)
async def get_profile_by_id(
    user_id: str,
    db: AsyncSession = Depends(get_db),
) -> ProfileResponse:
    """Get user profile by ID."""
    result = await db.execute(
        text("""
            SELECT id, full_name, phone, role, locale, avatar_url, created_at, updated_at
            FROM profiles 
            WHERE id = :user_id
        """),
        {"user_id": user_id}
    )
    row = result.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    profile = Profile(
        id=str(row.id),
        full_name=row.full_name,
        phone=row.phone,
        role=row.role,
        locale=row.locale,
        avatar_url=row.avatar_url,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )
    
    return ProfileResponse(profile=profile, message="Profile retrieved")
