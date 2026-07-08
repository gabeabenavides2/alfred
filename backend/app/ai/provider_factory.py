from app.core.config import settings
from app.ai.base import AIProvider
from app.ai.openrouter_provider import OpenRouterProvider


AI_PROVIDER_REGISTRY = {
    "openrouter": OpenRouterProvider,
}

def get_ai_provider() -> AIProvider:
    provider_class = AI_PROVIDER_REGISTRY.get(settings.llm_provider)
    if provider_class is None:
        raise ValueError(f"Unsupported AI provider: {settings.llm_provider}")
    
    return provider_class()
