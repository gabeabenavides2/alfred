import asyncio

from app.services.orchestrator_service import analyze_message


TEST_MESSAGES = [
    "Hello, how are you?",
    "Explain how binary search works.",
    "Help me debug a FastAPI endpoint that returns a 500 error.",
    "Compare running Alfred on a VPS versus locally.",
    "What is the weather in Detroit today?",
]


async def main() -> None:
    for message in TEST_MESSAGES:
        print("\n" + "=" * 70)
        print(f"USER: {message}")

        try:
            result = await analyze_message(message)

            print(f"\nIntent: {result.intent}")
            print(f"Model route: {result.model_route.value}")
            print(
                f"Direct response: "
                f"{result.can_respond_directly}"
            )
            print(
                f"Retrieve memories: "
                f"{result.retrieve_memories}"
            )
            print(
                f"Retrieve files: "
                f"{result.retrieve_files}"
            )
            print(
                f"Tools required: "
                f"{result.tool_required}"
            )

        except Exception as exc:
            print("\nORCHESTRATOR REQUEST FAILED")
            print(f"Error: {exc}")
            print("Continuing to the next test message...")


if __name__ == "__main__":
    asyncio.run(main())