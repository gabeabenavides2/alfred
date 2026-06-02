from openai import AsyncOpenAI

from app.core.config import settings
from app.ai.base import AIProvider

class OpenRouterProvider(AIProvider):
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
            default_headers={
                "HTTP-Referer": "http://localhost:3000",
                "X-OpenRouter-Title": "Alfred",
            },
        )

        self.model = settings.openrouter_model

    async def generate_response(self, message: str) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are Alfred, a helpful personal AI assistant.",
                },
                {
                    "role": "user",
                    "content": message,
                },
            ],
        )

        return response.choices[0].message.content or ""