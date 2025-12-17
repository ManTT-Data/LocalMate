"""Authentication Router."""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.db.session import get_db
from app.auth import GoogleLoginRequest, LoginResponse, LogoutResponse
from app.auth.controls import login_control, logout_control


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Login with Google OAuth",
    description="Authenticate user with Google OAuth access token and return JWT token.",
)
async def login(
    request: GoogleLoginRequest,
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    """
    Login with Google OAuth.
    
    Verifies the Google access token, creates or updates the user profile,
    and returns a JWT token for authentication.
    """
    try:
        result = await login_control(request.access_token, db)
        
        return LoginResponse(
            user_id=result["user_id"],
            email=result["email"],
            full_name=result["full_name"],
            avatar_url=result["avatar_url"],
            token=result["token"],
            message="Login successful"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Login failed: {str(e)}"
        )


@router.post(
    "/logout",
    response_model=LogoutResponse,
    summary="Logout user",
    description="Logout the current user.",
)
async def logout(
    user_id: str = Query(..., description="User ID (from JWT token)"),
    db: AsyncSession = Depends(get_db),
) -> LogoutResponse:
    """
    Logout user.
    
    Performs logout operations such as logging the event.
    Client should discard the JWT token after this call.
    """
    try:
        result = await logout_control(user_id, db)
        
        return LogoutResponse(message=result["message"])
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Logout failed: {str(e)}"
        )
