"""Security utilities for JWT verification with Supabase Auth."""

import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.shared.integrations.supabase_client import supabase

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Verify Supabase JWT and return user info.

    Args:
        credentials: Bearer token from Authorization header

    Returns:
        User object from Supabase

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        token = credentials.credentials
        response = supabase.auth.get_user(token)
        return response.user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


async def get_current_user_id(
    current_user: dict = Depends(get_current_user),
) -> uuid.UUID:
    """Extract user ID from current user."""
    return uuid.UUID(current_user.id)
