"""
Booking model

Lưu các booking từ MCP tools (Grab, Hotel, Tickets)
"""

from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, JSON
from app.shared.db.session import Base
from app.shared.models.base import TimestampMixin


class Booking(Base, TimestampMixin):
    """Booking records from MCP tools"""
    
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    itinerary_id = Column(Integer, ForeignKey("itineraries.id"), nullable=True, index=True)
    
    # Booking type
    booking_type = Column(String(50), nullable=False, index=True)  # grab, hotel, ticket, activity
    
    # External booking reference
    external_id = Column(String(255), nullable=True, index=True)
    external_provider = Column(String(100), nullable=True)  # grab, agoda, klook
    
    # Booking details (JSON for flexibility)
    # Grab: {from, to, vehicle_type, price, driver_name, ...}
    # Hotel: {hotel_name, check_in, check_out, rooms, ...}
    details = Column(JSON, default={}, nullable=False)
    
    # Status
    status = Column(String(50), default="pending", nullable=False)  # pending, confirmed, completed, cancelled
    
    # Pricing
    amount = Column(Float, nullable=True)
    currency = Column(String(10), default="VND", nullable=True)
    
    # Timestamps
    booking_date = Column(DateTime, nullable=True)
    service_date = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Booking {self.booking_type} - {self.status}>"
