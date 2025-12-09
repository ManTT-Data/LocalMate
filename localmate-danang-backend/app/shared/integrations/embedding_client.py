"""Embedding client for text and image embeddings."""

import httpx
from google import genai

from app.core.config import settings

# Initialize Google GenAI client for embeddings
client = genai.Client(api_key=settings.google_api_key)


class EmbeddingClient:
    """
    Client for generating embeddings.

    - Text: Google text-embedding-004 (768 dimensions)
    - Image: CLIP via HuggingFace Inference API (512 dimensions)
    """

    def __init__(self):
        """Initialize embedding client."""
        self.text_model = settings.embedding_model

    async def embed_text(self, text: str) -> list[float]:
        """
        Generate text embedding using text-embedding-004.

        Args:
            text: Input text to embed

        Returns:
            768-dimensional embedding vector
        """
        response = client.models.embed_content(
            model=self.text_model,
            contents=text,
        )
        return response.embeddings[0].values

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """
        Batch embed multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        response = client.models.embed_content(
            model=self.text_model,
            contents=texts,
        )
        return [e.values for e in response.embeddings]

    async def embed_image(self, image_url: str) -> list[float] | None:
        """
        Generate image embedding using CLIP via HuggingFace.

        Args:
            image_url: URL of image to embed

        Returns:
            512-dimensional embedding vector, or None if failed
        """
        if not settings.huggingface_api_key:
            return None

        async with httpx.AsyncClient() as http:
            try:
                response = await http.post(
                    "https://api-inference.huggingface.co/models/openai/clip-vit-base-patch32",
                    headers={"Authorization": f"Bearer {settings.huggingface_api_key}"},
                    json={"inputs": image_url},
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
            except Exception:
                return None


# Global embedding client instance
embedding_client = EmbeddingClient()
