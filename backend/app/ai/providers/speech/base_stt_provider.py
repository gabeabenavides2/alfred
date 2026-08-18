from abc import ABC, abstractmethod
from pathlib import Path


class STTProvider(ABC):
    """
    Base interface for speech-to-text providers.

    Implementations may run locally, on a VPS, on a phone,
    or through an external API.
    """

    @abstractmethod
    async def transcribe(
        self,
        audio_path: Path,
        model: str,
    ) -> str:
        """
        Convert an audio file into text.
        """