"""Gemini client for LLM operations using Google GenAI."""

import json
import re

from google import genai

from app.core.config import settings

# Initialize Google GenAI client
client = genai.Client(api_key=settings.google_api_key)


class GeminiClient:
    """Client for Gemini LLM operations."""

    def __init__(self, model: str | None = None):
        """Initialize with optional model override."""
        self.model = model or settings.default_gemini_model

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
        system_instruction: str | None = None,
    ) -> str:
        """
        Simple text generation.

        Args:
            prompt: Text prompt
            temperature: Sampling temperature
            system_instruction: Optional system prompt

        Returns:
            Generated text
        """
        config = {"temperature": temperature}
        if system_instruction:
            config["system_instruction"] = system_instruction

        response = client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=config,
        )
        return response.text

    async def parse_tool_calls(self, user_message: str, available_tools: list[dict]) -> dict:
        """
        Parse user message to determine which MCP tools to call.

        Args:
            user_message: User's natural language query
            available_tools: List of available tool definitions

        Returns:
            Dict with tool_name and arguments
        """
        tools_desc = "\n".join([
            f"- {t['name']}: {t['description']}" for t in available_tools
        ])

        prompt = f'''Bạn là AI assistant phân tích intent. Xác định công cụ cần gọi.

Các công cụ có sẵn:
{tools_desc}

Query của người dùng: "{user_message}"

Trả về JSON (chỉ JSON, không giải thích):
{{
    "tool_name": "tên_tool_cần_gọi",
    "arguments": {{...}},
    "reasoning": "lý do chọn tool này"
}}

Nếu không cần gọi tool, trả về:
{{"tool_name": null, "arguments": {{}}, "reasoning": "..."}}'''

        response = await self.generate(prompt, temperature=0.3)

        try:
            json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return json.loads(response)
        except json.JSONDecodeError:
            return {"tool_name": None, "arguments": {}, "reasoning": "Failed to parse"}


def get_gemini_client(model: str | None = None) -> GeminiClient:
    """Factory function to create Gemini client with specified model."""
    return GeminiClient(model=model)


# Global Gemini client instance (with default model)
gemini_client = GeminiClient()

