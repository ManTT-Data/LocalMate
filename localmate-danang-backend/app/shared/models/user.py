"""
User model

Lưu thông tin user (tourist, driver, admin) và preferences
"""

from sqlalchemy import Column, String, Integer, Enum, JSON
from app.shared.db.session import Base
from app.shared.models.base import TimestampMixin
import enum


class UserRole(str, enum.Enum):
    """User role enum"""
    TOURIST = "tourist"
    DRIVER = "driver"
    ADMIN = "admin"


class User(Base, TimestampMixin):
    """User table"""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.TOURIST, nullable=False)
    
    # User preferences (JSON field)
    # Example: {"language": "en", "interests": ["beach", "seafood"], "budget": "medium"}
    preferences = Column(JSON, default={}, nullable=False)
    
    # Travel profile
    home_country = Column(String(100), nullable=True)
    preferred_language = Column(String(10), default="en", nullable=False)
    
    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
