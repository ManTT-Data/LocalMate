"""
Place model

Lưu thông tin địa điểm (Dragon Bridge, Bé Mặn, cafes,...)
"""

from sqlalchemy import Column, String, Integer, Float, Text, JSON, ARRAY
from app.shared.db.session import Base
from app.shared.models.base import TimestampMixin


class Place(Base, TimestampMixin):
    """Place table - địa điểm du lịch, quán ăn, khách sạn,..."""
    
    __tablename__ = "places"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(500), nullable=False, index=True)
    name_vi = Column(String(500), nullable=True)  # Tên tiếng Việt
    description = Column(Text, nullable=True)
    description_vi = Column(Text, nullable=True)
    
    # Location
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    address = Column(String(500), nullable=True)
    address_vi = Column(String(500), nullable=True)
    
    # Category
    category = Column(String(100), nullable=False, index=True)  # restaurant, cafe, hotel, attraction, etc.
    subcategory = Column(String(100), nullable=True)  # seafood, coffee, beach, temple, etc.
    
    # Tags for filtering (Array of strings)
    tags = Column(ARRAY(String), default=[], nullable=False)  # ["beachfront", "family-friendly", "romantic"]
    
    # Metadata
    rating = Column(Float, nullable=True)  # 1-5
    price_level = Column(Integer, nullable=True)  # 1-4 ($, $$, $$$, $$$$)
    
    # Opening hours (JSON)
    # Example: {"monday": "09:00-22:00", "tuesday": "09:00-22:00", ...}
    opening_hours = Column(JSON, default={}, nullable=True)
    
    # External IDs
    google_place_id = Column(String(255), nullable=True, index=True)
    facebook_page_id = Column(String(255), nullable=True)
    
    # Rich content
    images = Column(ARRAY(String), default=[], nullable=True)  # URLs to images
    
    # Neo4j node ID (for graph sync)
    neo4j_node_id = Column(String(100), nullable=True, index=True)
    
    def __repr__(self):
        return f"<Place {self.name} ({self.category})>"
