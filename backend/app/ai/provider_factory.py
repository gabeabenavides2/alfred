from app.ai.providers.base import AIProvider
from app.ai.providers.openrouter_provider import OpenRouterProvider


class ProviderFactoryError(Exception):
    pass


def get_ai_provider(
    provider_name: str,
    model: str,
) -> AIProvider:
    normalized_provider = provider_name.strip().lower()

    if not normalized_provider:
        raise ProviderFactoryError(
            "Provider name cannot be empty."
        )

    if not model.strip():
        raise ProviderFactoryError(
            f"No model was provided for provider '{provider_name}'."
        )

    if normalized_provider == "openrouter":
        return OpenRouterProvider(model=model)

    raise ProviderFactoryError(
        f"Unsupported AI provider: '{provider_name}'."
    )