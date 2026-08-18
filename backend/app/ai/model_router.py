from dataclasses import dataclass

from app.ai.model_routes import ModelRoute
from app.core.config import settings


class ModelRoutingError(Exception):
    """Raised when a model route is missing a valid configuration."""


@dataclass(frozen=True)
class ModelSelection:
    """
    The provider and model selected for an AI operation.
    """

    route: ModelRoute
    provider: str
    model: str


class ModelRouter:
    """
    Maps an AI capability to its configured provider and model.

    This class only selects a model. It does not call the provider
    or analyze the user's message.
    """

    def __init__(self) -> None:
        self._routes: dict[ModelRoute, tuple[str, str | None]] = {
            ModelRoute.CHAT: (
                settings.chat_provider,
                settings.chat_model,
            ),
            ModelRoute.REASONING: (
                settings.reasoning_provider,
                settings.reasoning_model,
            ),
            ModelRoute.EMBEDDING: (
                settings.embedding_provider,
                settings.embedding_model,
            ),
            ModelRoute.VISION: (
                settings.vision_provider,
                settings.vision_model,
            ),
            ModelRoute.WEB: (
                settings.web_provider,
                settings.web_model,
            ),
            ModelRoute.VIDEO: (
                settings.video_provider,
                settings.video_model,
            ),
            ModelRoute.STT: (
                settings.stt_provider,
                settings.stt_model,
            ),
            ModelRoute.TTS: (
                settings.tts_provider,
                settings.tts_model,
            ),
        }

    def select(self, route: ModelRoute) -> ModelSelection:
        """
        Return the configured provider and model for the requested route.
        """

        configuration = self._routes.get(route)

        if configuration is None:
            raise ModelRoutingError(
                f"No configuration exists for route '{route.value}'."
            )

        provider, model = configuration

        if not provider or not provider.strip():
            raise ModelRoutingError(
                f"No provider is configured for route '{route.value}'."
            )

        if not model or not model.strip():
            raise ModelRoutingError(
                f"No model is configured for route '{route.value}'."
            )

        return ModelSelection(
            route=route,
            provider=provider.strip(),
            model=model.strip(),
        )
    