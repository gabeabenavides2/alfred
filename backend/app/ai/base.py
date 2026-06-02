from abc import ABC, abstractmethod


class AIProvider(ABC):
    @abstractmethod
    async def generate_response(self, message: str) -> str:
        pass