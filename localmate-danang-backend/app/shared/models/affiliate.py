"""
Affiliate model

Lưu thông tin affiliate programs và hoa hồng
"""

from sqlalchemy import Column, String, Integer, Float, ForeignKey, Boolean, JSON
from app.shared.db.session import Base
from app.shared.models.base import TimestampMixin


class AffiliateProgram(Base, TimestampMixin):
    """Affiliate programs for venues (restaurants, cafes, etc.)"""
    
    __tablename__ = "affiliate_programs"
    
    id = Column(Integer, primary_key=True, index=True)
    place_id = Column(Integer, ForeignKey("places.id"), nullable=False, index=True)
    
    # Program details
    program_name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    
    # Commission structure
    commission_type = Column(String(50), nullable=False)  # percentage, fixed
    commission_value = Column(Float, nullable=False)  # e.g., 10.0 for 10% or 50000 for 50,000 VND
    
    # Terms and conditions
    minimum_spend = Column(Float, nullable=True)  # Minimum customer spend required
    valid_from = Column(String(10), nullable=True)  # e.g., "2024-01-01"
    valid_to = Column(String(10), nullable=True)  # e.g., "2024-12-31"
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Additional terms (JSON)
    terms = Column(JSON, default={}, nullable=True)
    
    # For drivers
    driver_instructions = Column(String(1000), nullable=True)  # How to pitch to customer
    customer_benefit = Column(String(500), nullable=True)  # What customer gets
    
    def __repr__(self):
        return f"<AffiliateProgram {self.program_name}>"
