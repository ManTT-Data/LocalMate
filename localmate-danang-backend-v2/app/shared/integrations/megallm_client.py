"""MegaLLM client using OpenAI-compatible API with retry logic and key rotation."""

import asyncio
import logging

import httpx

from app.core.config import settings
from app.shared.integrations.key_rotator import megallm_key_rotator

logger = logging.getLogger(__name__)

# Timeout configuration for DeepSeek reasoning models (can take longer)
REQUEST_TIMEOUT = httpx.Timeout(
    connect=30.0,      # Connection timeout
    read=300.0,        # Read timeout (5 minutes for reasoning models)
    write=30.0,        # Write timeout
    pool=30.0,         # Pool timeout
)

# Rate limit configuration
MAX_429_RETRIES = 3
INITIAL_BACKOFF_SECONDS = 2


class MegaLLMClient:
    """Client for MegaLLM (OpenAI-compatible API) operations with key rotation."""

    def __init__(self, model: str | None = None):
        """Initialize with optional model override."""
        self.model = model or settings.default_megallm_model
        self.base_url = settings.megallm_base_url
        
    def _get_api_key(self) -> str:
        """Get API key using rotation or fallback to settings."""
        if megallm_key_rotator:
            return megallm_key_rotator.get_next_key()
        # Fallback to settings (backward compatibility)
        if settings.megallm_api_key:
            return settings.megallm_api_key
        raise ValueError("No MegaLLM API keys configured")

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
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        last_error = None
        rate_limit_retries = 0
        
        # Total attempts = max_retries + 1 (for timeout) + MAX_429_RETRIES (for rate limits)
        total_attempts = max_retries + 1 + MAX_429_RETRIES
        
        for attempt in range(total_attempts):
            # Get rotated API key (get new key on each attempt)
            api_key = self._get_api_key()
            
            try:
                async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "model": self.model,
                            "messages": messages,
                            "temperature": temperature,
                        },
                    )
                    
                    # Handle 429 Rate Limit with exponential backoff
                    if response.status_code == 429:
                        rate_limit_retries += 1
                        if rate_limit_retries <= MAX_429_RETRIES:
                            wait_time = INITIAL_BACKOFF_SECONDS * (2 ** (rate_limit_retries - 1))
                            logger.warning(
                                f"[MegaLLM] 429 Rate Limit hit, retry {rate_limit_retries}/{MAX_429_RETRIES} "
                                f"after {wait_time}s"
                            )
                            await asyncio.sleep(wait_time)
                            continue  # Try again with a new key
                        else:
                            # Max 429 retries exceeded - raise HTTPStatusError
                            logger.error(f"[MegaLLM] Max 429 retries exceeded ({MAX_429_RETRIES})")
                            response.raise_for_status()
                    
                    response.raise_for_status()
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                    
            except httpx.ReadTimeout as e:
                last_error = e
                if attempt < max_retries:
                    logger.warning(f"[MegaLLM] Timeout, retry {attempt + 1}/{max_retries}")
                    continue
                # After max timeout retries, raise the error
                raise
            except httpx.HTTPStatusError:
                # Re-raise HTTP errors (including 429 after max retries)
                # This allows react_agent to catch and handle gracefully
                raise
            except Exception as e:
                last_error = e
                raise

        # If we exit the loop without returning, something went wrong
        if last_error:
            raise last_error
        raise RuntimeError("Max retries exceeded")

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
        # Get rotated API key
        api_key = self._get_api_key()

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
                    "Authorization": f"Bearer {api_key}",
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
