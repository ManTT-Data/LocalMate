"""
LLM Client

Unified interface cho OpenAI, Anthropic, Google Gemini
"""

from typing import List, Dict, Any, Optional, Literal
from app.config import settings
from app.shared.core.logging import get_logger

logger = get_logger(__name__)

LLMProvider = Literal["openai", "anthropic", "google"]


class LLMClient:
    """Unified LLM client supporting multiple providers"""
    
    def __init__(self, provider: LLMProvider = "openai"):
        self.provider = provider
        self._client = None
    
    def _get_client(self):
        """Lazy load the appropriate LLM client"""
        if self._client:
            return self._client
        
        if self.provider == "openai":
            import openai
            self._client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        elif self.provider == "anthropic":
            import anthropic
            self._client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        elif self.provider == "google":
            import google.generativeai as genai
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            self._client = genai
        
        return self._client
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> str:
        """
        Generate chat completion
        
        Args:
            messages: List of messages [{"role": "user", "content": "..."}]
            model: Model name (provider specific)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text response
        """
        client = self._get_client()
        
        if self.provider == "openai":
            model = model or "gpt-4o-mini"
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        
        elif self.provider == "anthropic":
            model = model or "claude-3-5-sonnet-20241022"
            # Convert messages format
            system_msg = next((m["content"] for m in messages if m["role"] == "system"), None)
            user_messages = [m for m in messages if m["role"] != "system"]
            
            response = await client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_msg,
                messages=user_messages,
            )
            return response.content[0].text
        
        elif self.provider == "google":
            model = model or "gemini-2.0-flash-exp"
            # Simple implementation for Google
            model_instance = client.GenerativeModel(model)
            prompt = "\n".join([m["content"] for m in messages])
            response = model_instance.generate_content(prompt)
            return response.text
        
        raise ValueError(f"Unsupported provider: {self.provider}")
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate text embedding
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        if self.provider == "openai":
            client = self._get_client()
            response = await client.embeddings.create(
                model="text-embedding-3-small",
                input=text,
            )
            return response.data[0].embedding
        
        # TODO: Implement for other providers
        raise NotImplementedError(f"Embeddings not implemented for {self.provider}")


# Global instance
llm_client = LLMClient(provider="openai")
