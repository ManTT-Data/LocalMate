"""Prompts package for LocalMate Agent."""

from app.shared.prompts.prompts import (
    MMCA_SYSTEM_PROMPT,
    REACT_SYSTEM_PROMPT,
    GREETING_SYSTEM_PROMPT,
    SYNTHESIS_SYSTEM_PROMPT,
    TOOL_DEFINITIONS,
    TOOL_PURPOSES,
    # Tool-specific definitions
    FIND_NEARBY_PLACES_TOOL,
    RETRIEVE_CONTEXT_TEXT_TOOL,
    RETRIEVE_SIMILAR_VISUALS_TOOL,
    SEARCH_SOCIAL_MEDIA_TOOL,
    # Database constants
    AVAILABLE_CATEGORIES,
    CATEGORY_KEYWORDS,
    CATEGORY_TO_DB,
    # Prompt builders
    build_greeting_prompt,
    build_synthesis_prompt,
    build_reasoning_prompt,
)

__all__ = [
    "MMCA_SYSTEM_PROMPT",
    "REACT_SYSTEM_PROMPT",
    "GREETING_SYSTEM_PROMPT",
    "SYNTHESIS_SYSTEM_PROMPT",
    "TOOL_DEFINITIONS",
    "TOOL_PURPOSES",
    "FIND_NEARBY_PLACES_TOOL",
    "RETRIEVE_CONTEXT_TEXT_TOOL",
    "RETRIEVE_SIMILAR_VISUALS_TOOL",
    "SEARCH_SOCIAL_MEDIA_TOOL",
    "AVAILABLE_CATEGORIES",
    "CATEGORY_KEYWORDS",
    "CATEGORY_TO_DB",
    "build_greeting_prompt",
    "build_synthesis_prompt",
    "build_reasoning_prompt",
]
