"""Shared constants for LocalMate Agent."""

from app.shared.constants.prompts import (
    # System Prompts
    SYSTEM_PROMPT,
    REACT_SYSTEM_PROMPT,
    SYNTHESIS_PROMPT_TEMPLATE,
    
    # Location & Category Mappings
    KNOWN_LOCATIONS,
    CATEGORY_KEYWORDS,
    
    # Intent Detection Keywords
    LOCATION_KEYWORDS,
    SOCIAL_KEYWORDS,
    
    # Default Values
    DANANG_CENTER,
)

__all__ = [
    "SYSTEM_PROMPT",
    "REACT_SYSTEM_PROMPT", 
    "SYNTHESIS_PROMPT_TEMPLATE",
    "KNOWN_LOCATIONS",
    "CATEGORY_KEYWORDS",
    "LOCATION_KEYWORDS",
    "SOCIAL_KEYWORDS",
    "DANANG_CENTER",
]
