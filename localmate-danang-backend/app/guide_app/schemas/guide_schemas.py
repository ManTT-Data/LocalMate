"""Pydantic schemas for Guide Pack API."""

from pydantic import BaseModel


class FunFactRequest(BaseModel):
    """Request for a fun fact about a place."""

    place_id: str
    locale: str = "vi_VN"


class FunFactResponse(BaseModel):
    """Response with a fun fact."""

    place_id: str
    fact: str
    source: str | None = None


class LocalTipRequest(BaseModel):
    """Request for local tips."""

    place_id: str
    category: str | None = None  # food, transport, culture
    locale: str = "vi_VN"


class LocalTipResponse(BaseModel):
    """Response with local tips."""

    place_id: str
    tips: list[str]
    category: str | None = None


class LanguageCardRequest(BaseModel):
    """Request for a language learning card."""

    phrase_type: str  # greeting, ordering, directions, emergency
    locale: str = "vi_VN"


class LanguageCardResponse(BaseModel):
    """Response with language card."""

    phrase_type: str
    vietnamese: str
    english: str
    pronunciation: str
    context: str | None = None


class GuideContentRequest(BaseModel):
    """Request for guide content for a place."""

    place_id: str
    content_types: list[str] | None = None  # facts, tips, phrases
    locale: str = "vi_VN"


class GuideContentResponse(BaseModel):
    """Response with all guide content."""

    place_id: str
    fun_fact: str | None = None
    tips: list[str] | None = None
    phrases: list[LanguageCardResponse] | None = None
