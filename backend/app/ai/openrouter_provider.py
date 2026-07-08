from openai import AsyncOpenAI

from app.core.config import settings
from app.ai.base import AIProvider


class OpenRouterProvider(AIProvider):
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
            default_headers={
                "HTTP-Referer": settings.openrouter_site_url,
                "X-OpenRouter-Title": settings.openrouter_app_name,
            },
        )

        self.model = settings.openrouter_model

    async def generate_response(self, messages: list[dict]) -> str:
        final_messages = [
            {
                "role": "system",
                "content": settings.alfred_system_prompt,
            },
            *messages,
        ]

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=final_messages,
        )

        return response.choices[0].message.content or ""
    
    async def generate_raw_response(self, messages: list[dict]) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )

        return response.choices[0].message.content or ""