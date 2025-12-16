"""Embedding client for text and image embeddings."""

import httpx
from google import genai

from app.core.config import settings

# Initialize Google GenAI client
client = genai.Client(api_key=settings.google_api_key)


class EmbeddingClient:
    """Client for generating text and image embeddings."""

    def __init__(self):
        """Initialize embedding client."""
        self.text_model = settings.embedding_model
        self.hf_api_key = settings.huggingface_api_key

    async def embed_text(self, text: str) -> list[float]:
        """
        Generate text embedding using text-embedding-004.

        Args:
            text: Text to embed

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
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        response = client.models.embed_content(
            model=self.text_model,
            contents=texts,
        )
        return [emb.values for emb in response.embeddings]

    async def embed_image(self, image_url: str) -> list[float] | None:
        """
        Generate image embedding using CLIP via HuggingFace.

        Args:
            image_url: URL of the image

        Returns:
            512-dimensional embedding vector, or None if failed
        """
        if not self.hf_api_key:
            return None

        try:
            async with httpx.AsyncClient() as http_client:
                # Use CLIP model via HuggingFace Inference API
                response = await http_client.post(
                    "https://api-inference.huggingface.co/models/openai/clip-vit-base-patch32",
                    headers={"Authorization": f"Bearer {self.hf_api_key}"},
                    json={"inputs": {"image": image_url}},
                    timeout=30.0,
                )
                if response.status_code == 200:
                    return response.json()
                return None
        except Exception:
            return None


# Global embedding client instance
embedding_client = EmbeddingClient()
