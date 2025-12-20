"""Prompts package for LocalMate Agent."""

from app.shared.prompts.prompts import (
    MMCA_SYSTEM_PROMPT,
    REACT_SYSTEM_PROMPT,
    GREETING_SYSTEM_PROMPT,
    SYNTHESIS_SYSTEM_PROMPT,
    INTENT_SYSTEM_PROMPT,
    INTENT_DETECTION_PROMPT,
    SMART_PLAN_SYSTEM_PROMPT,
    TOOL_DEFINITIONS,
    TOOL_PURPOSES,
    # Tool-specific definitions
    FIND_NEARBY_PLACES_TOOL,
    RETRIEVE_CONTEXT_TEXT_TOOL,
    RETRIEVE_SIMILAR_VISUALS_TOOL,
    SEARCH_SOCIAL_MEDIA_TOOL,
    # Database constants
    AVAILABLE_CATEGORIES,
    # Prompt builders
    build_greeting_prompt,
    build_intent_prompt,
    build_synthesis_prompt,
    build_reasoning_prompt,
    build_smart_plan_prompt,
)

__all__ = [
    "MMCA_SYSTEM_PROMPT",
    "REACT_SYSTEM_PROMPT",
    "GREETING_SYSTEM_PROMPT",
    "SYNTHESIS_SYSTEM_PROMPT",
    "INTENT_SYSTEM_PROMPT",
    "INTENT_DETECTION_PROMPT",
    "SMART_PLAN_SYSTEM_PROMPT",
    "TOOL_DEFINITIONS",
    "TOOL_PURPOSES",
    "FIND_NEARBY_PLACES_TOOL",
    "RETRIEVE_CONTEXT_TEXT_TOOL",
    "RETRIEVE_SIMILAR_VISUALS_TOOL",
    "SEARCH_SOCIAL_MEDIA_TOOL",
    "AVAILABLE_CATEGORIES",
    "build_greeting_prompt",
    "build_intent_prompt",
    "build_synthesis_prompt",
    "build_reasoning_prompt",
    "build_smart_plan_prompt",
]
