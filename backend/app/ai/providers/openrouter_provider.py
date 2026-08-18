import httpx

from app.ai.providers.base import AIProvider
from app.core.config import settings


class OpenRouterProvider(AIProvider):
    def __init__(self, model: str) -> None:
        if not model.strip():
            raise ValueError("OpenRouter model cannot be empty.")

        self.url = (
            f"{settings.openrouter_base_url.rstrip('/')}"
            "/chat/completions"
        )

        self.model = model

        self.headers = {
            "Authorization": f"Bearer {settings.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": settings.openrouter_site_url,
            "X-OpenRouter-Title": settings.openrouter_app_name,
        }

    async def generate_response(
        self,
        messages: list[dict],
    ) -> str:
        final_messages = [
            {
                "role": "system",
                "content": settings.alfred_system_prompt,
            },
            *messages,
        ]

        return await self._complete(final_messages)

    async def generate_raw_response(
        self,
        messages: list[dict],
    ) -> str:
        return await self._complete(messages)

    async def _complete(
        self,
        messages: list[dict],
    ) -> str:
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.url,
                headers=self.headers,
                json=payload,
            )

        response.raise_for_status()

        data = response.json()
        choices = data.get("choices")

        if not choices:
            raise RuntimeError(
                "OpenRouter returned no choices. "
                f"Status: {response.status_code}. "
                f"Response: {data}"
            )

        content = (
            choices[0]
            .get("message", {})
            .get("content")
        )

        if not content:
            raise RuntimeError(
                f"OpenRouter returned empty content: {data}"
            )

        return content