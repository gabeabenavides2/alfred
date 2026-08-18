from abc import ABC, abstractmethod


class AIProvider(ABC):
    @abstractmethod
    async def generate_response(self, messages: list[dict]) -> str:
        pass

    @abstractmethod
    async def generate_raw_response(self, messages: list[dict]) -> str:
        pass