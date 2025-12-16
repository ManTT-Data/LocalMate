"""MegaLLM client using OpenAI-compatible API with retry logic."""

import httpx

from app.core.config import settings

# Timeout configuration for DeepSeek reasoning models (can take longer)
REQUEST_TIMEOUT = httpx.Timeout(
    connect=30.0,      # Connection timeout
    read=300.0,        # Read timeout (5 minutes for reasoning models)
    write=30.0,        # Write timeout
    pool=30.0,         # Pool timeout
)


class MegaLLMClient:
    """Client for MegaLLM (OpenAI-compatible API) operations."""

    def __init__(self, model: str | None = None):
        """Initialize with optional model override."""
        self.model = model or settings.default_megallm_model
        self.api_key = settings.megallm_api_key
        self.base_url = settings.megallm_base_url

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        system_instruction: str | None = None,
        max_retries: int = 2,
    ) -> str:
        """
        Generate text using MegaLLM (OpenAI-compatible API).

        Args:
            prompt: Text prompt
            temperature: Sampling temperature
            system_instruction: Optional system prompt
            max_retries: Number of retries on timeout

        Returns:
            Generated text
        """
        if not self.api_key:
            raise ValueError("MEGALLM_API_KEY is not configured")

        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        last_error = None
        for attempt in range(max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "model": self.model,
                            "messages": messages,
                            "temperature": temperature,
                        },
                    )
                    response.raise_for_status()
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
            except httpx.ReadTimeout as e:
                last_error = e
                if attempt < max_retries:
                    continue  # Retry
                raise
            except Exception as e:
                last_error = e
                raise

        # This shouldn't be reached, but just in case
        raise last_error if last_error else RuntimeError("Unknown error")

    async def chat(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        system_instruction: str | None = None,
    ) -> str:
        """
        Generate chat completion using MegaLLM.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            system_instruction: Optional system prompt

        Returns:
            Generated text response
        """
        if not self.api_key:
            raise ValueError("MEGALLM_API_KEY is not configured")

        chat_messages = []
        if system_instruction:
            chat_messages.append({"role": "system", "content": system_instruction})

        # Convert messages to OpenAI format
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content") or msg.get("parts", [""])[0]
            chat_messages.append({"role": role, "content": content})

        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": chat_messages,
                    "temperature": temperature,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]


def get_megallm_client(model: str | None = None) -> MegaLLMClient:
    """Factory function to create MegaLLM client with specified model."""
    return MegaLLMClient(model=model)
