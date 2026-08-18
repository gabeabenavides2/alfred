import asyncio

from backend.app.ai.providers.embeddings.provider_factory import get_embedding_provider


async def main() -> None:
    provider = get_embedding_provider()

    vector = await provider.embed_text(
        "Rent is $690 per month."
    )

    print("Provider:", provider.provider_name)
    print("Model:", provider.model_name)
    print("Configured dimensions:", provider.dimensions)
    print("Actual dimensions:", len(vector))
    print("First five values:", vector[:5])


if __name__ == "__main__":
    asyncio.run(main())