"""Security utilities - JWT verification DISABLED for demo."""

import uuid
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings

# Optional security - allows requests without token
security = HTTPBearer(auto_error=False)

# Demo user for when auth is disabled
DEMO_USER = {
    "id": "00000000-0000-0000-0000-000000000001",
    "email": "demo@localmate.vn",
    "role": "tourist",
}


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> dict:
    """
    Get current user - DEMO MODE: returns demo user if no token provided.

    In production, set APP_DEBUG=false to require real JWT.

    Args:
        credentials: Optional Bearer token from Authorization header

    Returns:
        User object (demo user if no token, real user if valid token)
    """
    # Demo mode: return demo user if no credentials or debug mode
    if settings.app_debug:
        if credentials is None:
            return type("User", (), DEMO_USER)()
        
        # If token provided, try to verify (optional)
        try:
            from app.shared.integrations.supabase_client import supabase
            token = credentials.credentials
            response = supabase.auth.get_user(token)
            return response.user
        except Exception:
            # If verification fails in debug mode, still return demo user
            return type("User", (), DEMO_USER)()
    
    # Production mode: require valid JWT
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        from app.shared.integrations.supabase_client import supabase
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
    user_id = getattr(current_user, 'id', None) or current_user.get('id')
    return uuid.UUID(str(user_id))
