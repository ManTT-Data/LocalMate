"""Guide Agent - generates fun facts, tips, and language cards."""

from app.guide_app.schemas.guide_schemas import (
    FunFactResponse,
    GuideContentResponse,
    LanguageCardResponse,
    LocalTipResponse,
)
from app.shared.integrations.gemini_client import GeminiClient, gemini_client


class GuideAgent:
    """
    Agent for generating guide content.

    Provides fun facts, local tips, and language cards for places.
    """

    def __init__(self, llm: GeminiClient | None = None):
        """Initialize with optional LLM override."""
        self._llm = llm or gemini_client

    async def generate_fun_fact(
        self,
        place_id: str,
        place_name: str | None = None,
    ) -> FunFactResponse:
        """
        Generate a fun fact about a place.

        Args:
            place_id: Place identifier
            place_name: Optional place name

        Returns:
            FunFactResponse with generated fact
        """
        name = place_name or place_id
        prompt = f"""Tạo một fun fact thú vị về địa điểm "{name}" ở Đà Nẵng.
Yêu cầu:
- 1-2 câu
- Tiếng Việt
- Thông tin độc đáo, ít người biết
- Chỉ trả về fact, không giải thích"""

        fact = await self._llm.generate(prompt, temperature=0.8)

        return FunFactResponse(
            place_id=place_id,
            fact=fact.strip(),
            source="AI Generated",
        )

    async def generate_local_tips(
        self,
        place_id: str,
        place_name: str | None = None,
        category: str | None = None,
    ) -> LocalTipResponse:
        """
        Generate local tips for a place.

        Args:
            place_id: Place identifier
            place_name: Optional place name
            category: Optional tip category

        Returns:
            LocalTipResponse with tips
        """
        name = place_name or place_id
        category_hint = f" về {category}" if category else ""
        prompt = f"""Tạo 3 tips địa phương{category_hint} cho du khách tại "{name}" ở Đà Nẵng.
Yêu cầu:
- Mỗi tip 1 câu ngắn gọn
- Tiếng Việt
- Thực tế, hữu ích
- Trả về dạng danh sách, mỗi dòng 1 tip, bắt đầu bằng "-"
"""

        response = await self._llm.generate(prompt, temperature=0.7)

        # Parse tips from response
        tips = []
        for line in response.strip().split("\n"):
            line = line.strip()
            if line.startswith("-"):
                tips.append(line[1:].strip())
            elif line:
                tips.append(line)

        return LocalTipResponse(
            place_id=place_id,
            tips=tips[:3],  # Limit to 3 tips
            category=category,
        )

    async def generate_language_card(
        self,
        phrase_type: str,
    ) -> LanguageCardResponse:
        """
        Generate a language learning card.

        Args:
            phrase_type: Type of phrase (greeting, ordering, etc.)

        Returns:
            LanguageCardResponse with phrase info
        """
        prompt = f"""Tạo một thẻ học tiếng Việt cho du khách.
Loại câu: {phrase_type}

Trả về JSON:
{{"vietnamese": "câu tiếng Việt", "english": "English translation", "pronunciation": "phiên âm", "context": "ngữ cảnh sử dụng"}}

Chỉ trả về JSON."""

        response = await self._llm.generate(prompt, temperature=0.5)

        # Parse JSON from response
        import json
        import re

        try:
            json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(response)

            return LanguageCardResponse(
                phrase_type=phrase_type,
                vietnamese=data.get("vietnamese", "Xin chào"),
                english=data.get("english", "Hello"),
                pronunciation=data.get("pronunciation", "Sin chow"),
                context=data.get("context"),
            )
        except json.JSONDecodeError:
            # Fallback
            return LanguageCardResponse(
                phrase_type=phrase_type,
                vietnamese="Xin chào",
                english="Hello",
                pronunciation="Sin chow",
                context="Greeting",
            )

    async def generate_guide_content(
        self,
        place_id: str,
        place_name: str | None = None,
        content_types: list[str] | None = None,
    ) -> GuideContentResponse:
        """
        Generate all guide content for a place.

        Args:
            place_id: Place identifier
            place_name: Optional place name
            content_types: Optional list of content types to include

        Returns:
            GuideContentResponse with all content
        """
        types = content_types or ["facts", "tips", "phrases"]

        fun_fact = None
        tips = None
        phrases = None

        if "facts" in types:
            fact_response = await self.generate_fun_fact(place_id, place_name)
            fun_fact = fact_response.fact

        if "tips" in types:
            tips_response = await self.generate_local_tips(place_id, place_name)
            tips = tips_response.tips

        if "phrases" in types:
            phrases = []
            for phrase_type in ["greeting", "ordering"]:
                card = await self.generate_language_card(phrase_type)
                phrases.append(card)

        return GuideContentResponse(
            place_id=place_id,
            fun_fact=fun_fact,
            tips=tips,
            phrases=phrases,
        )


# Singleton instance
guide_agent = GuideAgent()
