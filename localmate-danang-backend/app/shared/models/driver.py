"""
Driver model

Lưu thông tin driver (Grab drivers) nội bộ
"""

from sqlalchemy import Column, String, Integer, Float, ForeignKey, Boolean, JSON
from app.shared.db.session import Base
from app.shared.models.base import TimestampMixin


class DriverProfile(Base, TimestampMixin):
    """Driver profile for Grab drivers using Guide Pack"""
    
    __tablename__ = "driver_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    
    # Driver details
    driver_name = Column(String(255), nullable=False)
    phone_number = Column(String(50), nullable=True)
    vehicle_type = Column(String(100), nullable=True)  # car, bike
    license_plate = Column(String(50), nullable=True)
    
    # Grab integration
    grab_driver_id = Column(String(255), nullable=True, unique=True, index=True)
    
    # Language capabilities (Array of language codes)
    languages = Column(JSON, default=["vi", "en"], nullable=False)  # ["vi", "en", "ja", "ko"]
    
    # Performance metrics
    rating = Column(Float, nullable=True)
    total_trips = Column(Integer, default=0, nullable=False)
    
    # Guide Pack usage
    guide_pack_enabled = Column(Boolean, default=True, nullable=False)
    
    # Preferences
    preferences = Column(JSON, default={}, nullable=True)
    
    def __repr__(self):
        return f"<DriverProfile {self.driver_name}>"
