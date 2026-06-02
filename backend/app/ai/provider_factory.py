from app.core.config import settings
from app.ai.base import AIProvider
from app.ai.openrouter_provider import OpenRouterProvider


def get_ai_provider() -> AIProvider:
    if settings.ai_provider == "openrouter":
        return OpenRouterProvider()

    raise ValueError(f"Unsupported AI provider: {settings.ai_provider}")