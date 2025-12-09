"""Gemini client for LLM operations using Google GenAI."""

import json
import re

from google import genai

from app.core.config import settings

# Initialize Google GenAI client
client = genai.Client(api_key=settings.google_api_key)


class GeminiClient:
    """Client for Gemini 2.5 Flash LLM operations."""

    def __init__(self, model: str | None = None):
        """Initialize with optional model override."""
        self.model = model or settings.gemini_model

    async def chat(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        system_instruction: str | None = None,
    ) -> str:
        """
        Generate chat completion using Gemini.

        Args:
            messages: List of message dicts with 'role' and 'parts'
            temperature: Sampling temperature (0.0 - 1.0)
            system_instruction: Optional system prompt

        Returns:
            Generated text response
        """
        config = {"temperature": temperature}
        if system_instruction:
            config["system_instruction"] = system_instruction

        response = client.models.generate_content(
            model=self.model,
            contents=messages,
            config=config,
        )
        return response.text

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
    ) -> str:
        """
        Simple text generation.

        Args:
            prompt: Text prompt
            temperature: Sampling temperature

        Returns:
            Generated text
        """
        response = client.models.generate_content(
            model=self.model,
            contents=prompt,
            config={"temperature": temperature},
        )
        return response.text

    async def parse_intent(self, user_query: str) -> dict:
        """
        Parse natural language query into structured intent.

        Args:
            user_query: User's natural language query

        Returns:
            Structured intent dict with categories, specialty, near, etc.
        """
        prompt = f'''Bạn là một AI parser. Phân tích query du lịch và trả về JSON.

Query: "{user_query}"

Trả về JSON với format sau (chỉ trả về JSON, không giải thích):
{{
    "categories": ["restaurant", "beach", "cafe", ...],  // loại địa điểm
    "specialty": ["seafood", "coffee", ...],  // đặc trưng
    "near": "My Khe" hoặc null,  // gần vị trí nào
    "min_rating": 4.0,  // rating tối thiểu (default 4.0)
    "budget": "low/medium/high" hoặc null,
    "time_of_day": "morning/afternoon/evening/night" hoặc null
}}'''

        response = await self.generate(prompt, temperature=0.3)
        
        # Extract JSON from response
        try:
            # Try to find JSON in response
            json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return json.loads(response)
        except json.JSONDecodeError:
            # Return default intent
            return {
                "categories": [],
                "specialty": [],
                "near": None,
                "min_rating": 4.0,
                "budget": None,
                "time_of_day": None,
            }

    async def generate_itinerary_title(
        self,
        duration_days: int,
        interests: list[str] | None = None,
    ) -> str:
        """Generate an attractive title for an itinerary."""
        interests_str = ", ".join(interests) if interests else "khám phá"
        prompt = f"""Tạo tiêu đề ngắn gọn (dưới 10 từ) cho lịch trình du lịch Đà Nẵng {duration_days} ngày với sở thích: {interests_str}.
Chỉ trả về tiêu đề, không giải thích."""
        
        response = await self.generate(prompt, temperature=0.8)
        return response.strip().strip('"')

    async def generate_stop_description(
        self,
        place_name: str,
        category: str,
    ) -> str:
        """Generate a short description for a stop."""
        prompt = f"""Viết mô tả ngắn (1-2 câu) cho địa điểm "{place_name}" ({category}) ở Đà Nẵng.
Chỉ trả về mô tả, không giải thích."""
        
        response = await self.generate(prompt, temperature=0.7)
        return response.strip()


# Global Gemini client instance
gemini_client = GeminiClient()
