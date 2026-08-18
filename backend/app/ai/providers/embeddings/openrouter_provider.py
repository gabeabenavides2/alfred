import httpx

from backend.app.ai.providers.embeddings.base import EmbeddingProvider
from app.core.config import settings


class OpenRouterEmbeddingProvider(EmbeddingProvider):
    @property
    def provider_name(self) -> str:
        return "openrouter"

    @property
    def model_name(self) -> str:
        return settings.embedding_model

    @property
    def dimensions(self) -> int:
        return settings.embedding_dimensions

    async def embed_text(self, text: str) -> list[float]:
        cleaned_text = text.strip()

        if not cleaned_text:
            raise ValueError("Cannot embed empty text")

        headers = {
            "Authorization": f"Bearer {settings.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": settings.openrouter_site_url,
            "X-OpenRouter-Title": settings.openrouter_app_name,
        }

        payload = {
            "model": self.model_name,
            "input": cleaned_text,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{settings.openrouter_base_url}/embeddings",
                headers=headers,
                json=payload,
            )

        response.raise_for_status()
        body = response.json()

        if not body.get("data"):
            raise RuntimeError(
                f"OpenRouter returned no embedding data: {body}"
            )

        vector = body["data"][0]["embedding"]

        if len(vector) != self.dimensions:
            raise ValueError(
                f"Embedding dimension mismatch: "
                f"expected {self.dimensions}, received {len(vector)}"
            )

        return vector