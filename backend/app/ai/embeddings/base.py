from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        pass

    @property
    @abstractmethod
    def dimensions(self) -> int:
        pass

    @abstractmethod
    async def embed_text(self, text: str) -> list[float]:
        pass

    async def embed_many(self, texts: list[str]) -> list[list[float]]:
        return [await self.embed_text(text) for text in texts]