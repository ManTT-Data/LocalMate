"""
Guide Pack Schemas

Request/Response models cho Guide Pack generation
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class GuidePackRequest(BaseModel):
    """Request to generate a guide pack"""
    driver_id: int
    trip_id: Optional[str] = None
    
    # Current context
    current_place_id: Optional[int] = None
    current_lat: Optional[float] = None
    current_lon: Optional[float] = None
    
    # Passenger info
    passenger_language: str = Field(default="en", description="Passenger's language (en, ja, ko, zh, vi)")
    passenger_interests: List[str] = Field(default_factory=list)
    
    # Options
    include_affiliate: bool = Field(default=True, description="Include affiliate suggestions")
    include_fun_facts: bool = Field(default=True)


class LanguageCard(BaseModel):
    """Quick phrase in multiple languages"""
    english: str
    vietnamese: str
    japanese: Optional[str] = None
    korean: Optional[str] = None
    chinese: Optional[str] = None


class GuidePackCard(BaseModel):
    """Single card in the guide pack"""
    card_type: str = Field(description="place_info, fun_fact, local_tip, language_card, affiliate")
    title: str
    content: str
    
    # Optional fields
    place_name: Optional[str] = None
    image_url: Optional[str] = None
    language_phrases: Optional[LanguageCard] = None
    
    # For affiliate cards
    affiliate_venue: Optional[str] = None
    commission_info: Optional[str] = None


class GuidePackResponse(BaseModel):
    """Complete guide pack for a driver"""
    trip_id: Optional[str] = None
    driver_id: int
    
    # Current location context
    current_place: Optional[str] = None
    nearby_attractions: List[str] = Field(default_factory=list)
    
    # Guide pack cards
    cards: List[GuidePackCard]
    
    # Summary for driver
    driver_summary: str
    
    # Quick reference
    quick_phrases: List[LanguageCard] = Field(default_factory=list)
