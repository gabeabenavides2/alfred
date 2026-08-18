from app.ai.providers.speech.base_stt_provider import STTProvider
from app.ai.providers.speech.base_tts_provider import TTSProvider


class UnsupportedSpeechProviderError(ValueError):
    """Raised when a configured speech provider is unsupported."""


def get_stt_provider(provider_name: str) -> STTProvider:
    normalized_name = provider_name.strip().lower()

    if normalized_name == "openrouter":
        from app.ai.providers.openrouter_stt_provider import (
            OpenRouterSTTProvider,
        )

        return OpenRouterSTTProvider()

    if normalized_name == "local_whisper":
        from app.ai.providers.local_whisper_provider import (
            LocalWhisperProvider,
        )

        return LocalWhisperProvider()

    raise UnsupportedSpeechProviderError(
        f"Unsupported STT provider: '{provider_name}'."
    )


def get_tts_provider(provider_name: str) -> TTSProvider:
    normalized_name = provider_name.strip().lower()

    if normalized_name == "openrouter":
        from app.ai.providers.openrouter_tts_provider import (
            OpenRouterTTSProvider,
        )

        return OpenRouterTTSProvider()

    if normalized_name == "local_piper":
        from app.ai.providers.local_piper_provider import (
            LocalPiperProvider,
        )

        return LocalPiperProvider()

    raise UnsupportedSpeechProviderError(
        f"Unsupported TTS provider: '{provider_name}'."
    )