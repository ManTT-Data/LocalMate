"""User Profile models."""

from datetime import datetime
from pydantic import BaseModel, Field


class ProfileBase(BaseModel):
    """Base profile fields."""
    full_name: str = Field(default="", description="User's full name")
    phone: str | None = Field(None, description="Phone number")
    locale: str = Field(default="vi_VN", description="Locale setting")
    avatar_url: str | None = Field(None, description="Avatar URL")


class ProfileCreate(ProfileBase):
    """Create profile request (usually auto-created on signup)."""
    pass


class ProfileUpdate(BaseModel):
    """Update profile request - all fields optional."""
    full_name: str | None = None
    phone: str | None = None
    locale: str | None = None
    avatar_url: str | None = None


class Profile(ProfileBase):
    """Full profile response."""
    id: str = Field(..., description="User ID (UUID)")
    role: str = Field(default="tourist", description="User role: tourist, driver, admin")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProfileResponse(BaseModel):
    """API response wrapper."""
    profile: Profile
    message: str = "Success"
