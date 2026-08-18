from abc import ABC, abstractmethod


class TTSProvider(ABC):
    """
    Base interface for text-to-speech providers.

    Implementations may run locally, on a VPS, on a phone,
    or through an external API.
    """

    @abstractmethod
    async def synthesize(
        self,
        text: str,
        model: str,
    ) -> bytes:
        """
        Convert text into encoded audio bytes.
        """