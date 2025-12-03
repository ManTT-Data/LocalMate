"""
Itinerary model

Lưu hành trình du lịch được tạo bởi Planner Agent
"""

from sqlalchemy import Column, String, Integer, Float, ForeignKey, Text, DateTime, JSON
from sqlalchemy.orm import relationship
from app.shared.db.session import Base
from app.shared.models.base import TimestampMixin


class Itinerary(Base, TimestampMixin):
    """Itinerary master table"""
    
    __tablename__ = "itineraries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    
    # Trip details
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    duration_days = Column(Integer, nullable=True)
    
    # Budget and preferences
    budget_total = Column(Float, nullable=True)
    preferences = Column(JSON, default={}, nullable=True)  # family_size, interests, etc.
    
    # Status
    status = Column(String(50), default="draft", nullable=False)  # draft, confirmed, completed
    
    # Relationships
    stops = relationship("ItineraryStop", back_populates="itinerary", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Itinerary {self.title}>"


class ItineraryStop(Base, TimestampMixin):
    """Individual stops in an itinerary"""
    
    __tablename__ = "itinerary_stops"
    
    id = Column(Integer, primary_key=True, index=True)
    itinerary_id = Column(Integer, ForeignKey("itineraries.id"), nullable=False, index=True)
    place_id = Column(Integer, ForeignKey("places.id"), nullable=False, index=True)
    
    # Stop details
    order = Column(Integer, nullable=False)  # Order in the itinerary (1, 2, 3,...)
    arrival_time = Column(DateTime, nullable=True)
    departure_time = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    
    # AI-generated content
    title = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)  # Why visit this place
    tips = Column(Text, nullable=True)  # Local tips
    
    # Transportation to next stop
    transport_mode = Column(String(50), nullable=True)  # walk, grab, bike
    transport_duration_minutes = Column(Integer, nullable=True)
    transport_cost = Column(Float, nullable=True)
    
    # Relationships
    itinerary = relationship("Itinerary", back_populates="stops")
    
    def __repr__(self):
        return f"<ItineraryStop {self.order} for Itinerary {self.itinerary_id}>"
