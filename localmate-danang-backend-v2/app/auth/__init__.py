"""Authentication models."""

from datetime import datetime
from pydantic import BaseModel, Field


class GoogleLoginRequest(BaseModel):
    """Google OAuth login request."""
    access_token: str = Field(..., description="Google OAuth access token")


class LoginResponse(BaseModel):
    """Login response."""
    user_id: str = Field(..., description="User ID (UUID)")
    email: str = Field(..., description="User email")
    full_name: str = Field(..., description="User's full name")
    avatar_url: str | None = Field(None, description="Avatar URL")
    token: str = Field(..., description="JWT token")
    message: str = "Login successful"


class LogoutResponse(BaseModel):
    """Logout response."""
    message: str = "Logout successful"
