import asyncio

from app.services.memory_extractor import MemoryExtractor


async def main() -> None:
    extractor = MemoryExtractor()

    test_messages = [
        "My rent is $690 per month.",
        "I want Alfred finished by August 15.",
        "I prefer dark mode.",
        "What is the capital of France?",
        "Thanks, that makes sense.",
        (
            "I work at Michigan Farm Bureau and want to become "
            "a DevOps engineer after graduation."
        ),
        (
            "My girlfriend's birthday is November 4, and I want "
            "to plan a nice dinner and hotel."
        ),
    ]

    for index, message in enumerate(test_messages, start=1):
        print("\n" + "=" * 70)
        print(f"TEST {index}")
        print("=" * 70)
        print(f"User message: {message}")

        try:
            result = await extractor.extract_memories(message)

            if not result.memories:
                print("Extracted memories: None")
                continue

            print("Extracted memories:")

            for memory in result.memories:
                print(
                    {
                        "content": memory.content,
                        "memory_type": memory.memory_type.value,
                        "importance_score": memory.importance_score,
                    }
                )

        except Exception as error:
            print(f"ERROR: {type(error).__name__}: {error}")


if __name__ == "__main__":
    asyncio.run(main())