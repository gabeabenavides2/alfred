from app.ai.embeddings.base import EmbeddingProvider
from app.ai.embeddings.openrouter_provider import (
    OpenRouterEmbeddingProvider,
)
from app.core.config import settings


EMBEDDING_PROVIDER_REGISTRY: dict[
    str,
    type[EmbeddingProvider],
] = {
    "openrouter": OpenRouterEmbeddingProvider,
}


def get_embedding_provider() -> EmbeddingProvider:
    provider_class = EMBEDDING_PROVIDER_REGISTRY.get(
        settings.embedding_provider.lower()
    )

    if provider_class is None:
        raise ValueError(
            f"Unsupported embedding provider: "
            f"{settings.embedding_provider}"
        )

    return provider_class()