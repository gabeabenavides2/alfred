import asyncio
import json
from dataclasses import dataclass
from typing import Any

# Use the same import you currently use in test_orchestrator_memory.py.
# Change this line only if your function has a different location or name.
from app.services.orchestrator_service import analyze_message


@dataclass
class RoutingTest:
    message: str
    expected: dict[str, Any]


TEST_CASES = [
    # ---------------------------------------------------------
    # Memory retrieval
    # ---------------------------------------------------------
    RoutingTest(
        message="How much is my rent?",
        expected={
            "retrieve_memories": True,
            "can_respond_directly": False,
        },
    ),
    RoutingTest(
        message="What food do I like?",
        expected={
            "retrieve_memories": True,
            "can_respond_directly": False,
        },
    ),
    RoutingTest(
        message="When is Charlie's birthday?",
        expected={
            "retrieve_memories": True,
            "can_respond_directly": False,
        },
    ),
    RoutingTest(
        message="Who is my girlfriend?",
        expected={
            "retrieve_memories": True,
            "can_respond_directly": False,
        },
    ),
    RoutingTest(
        message="When is Sarah's birthday?",
        expected={
            "retrieve_memories": True,
            "can_respond_directly": False,
        },
    ),
    RoutingTest(
        message="When do I graduate?",
        expected={
            "retrieve_memories": True,
            "can_respond_directly": False,
        },
    ),

    # ---------------------------------------------------------
    # File retrieval
    # ---------------------------------------------------------
    RoutingTest(
        message="Summarize my physiology notes.",
        expected={
            "retrieve_files": True,
            "can_respond_directly": False,
        },
    ),
    RoutingTest(
        message="Find my budget spreadsheet.",
        expected={
            "retrieve_files": True,
            "can_respond_directly": False,
        },
    ),
    RoutingTest(
        message="Open my chemistry study guide.",
        expected={
            "retrieve_files": True,
            "can_respond_directly": False,
        },
    ),

    # ---------------------------------------------------------
    # Note retrieval
    # ---------------------------------------------------------
    RoutingTest(
        message="What did I write in my notes about PostgreSQL?",
        expected={
            "retrieve_notes": True,
            "can_respond_directly": False,
        },
    ),

    # ---------------------------------------------------------
    # Tool routing
    # ---------------------------------------------------------
    RoutingTest(
        message="Email Sarah that I'll be 10 minutes late.",
        expected={
            "intent": "send_email",
            "tool_required": True,
            "can_respond_directly": False,
        },
    ),
    RoutingTest(
        message="Remind me tomorrow at 9 AM to call my mom.",
        expected={
            "intent": "create_reminder",
            "tool_required": True,
            "can_respond_directly": False,
        },
    ),
    RoutingTest(
        message="What's on my calendar today?",
        expected={
            "intent": "calendar_query",
            "tool_required": True,
            "can_respond_directly": False,
        },
    ),
    RoutingTest(
        message="Create a meeting with John for Friday.",
        expected={
            "tool_required": True,
            "can_respond_directly": False,
        },
    ),

    # ---------------------------------------------------------
    # Direct-response fast path
    # ---------------------------------------------------------
    RoutingTest(
        message="Hi",
        expected={
            "can_respond_directly": True,
            "tool_required": False,
            "retrieve_memories": False,
            "retrieve_files": False,
            "retrieve_notes": False,
        },
    ),
    RoutingTest(
        message="Thanks!",
        expected={
            "can_respond_directly": True,
            "tool_required": False,
            "retrieve_memories": False,
            "retrieve_files": False,
            "retrieve_notes": False,
        },
    ),
    RoutingTest(
        message="Good morning.",
        expected={
            "can_respond_directly": True,
            "tool_required": False,
            "retrieve_memories": False,
            "retrieve_files": False,
            "retrieve_notes": False,
        },
    ),
    RoutingTest(
        message="What is PostgreSQL?",
        expected={
            "can_respond_directly": True,
            "tool_required": False,
            "retrieve_memories": False,
            "retrieve_files": False,
            "retrieve_notes": False,
        },
    ),
    RoutingTest(
        message="What's 2 + 2?",
        expected={
            "can_respond_directly": True,
            "tool_required": False,
            "retrieve_memories": False,
            "retrieve_files": False,
            "retrieve_notes": False,
        },
    ),
    RoutingTest(
        message="Tell me a joke.",
        expected={
            "can_respond_directly": True,
            "tool_required": False,
            "retrieve_memories": False,
            "retrieve_files": False,
            "retrieve_notes": False,
        },
    ),
]


def convert_result_to_dict(result: Any) -> dict[str, Any]:
    """
    Convert the orchestrator result into a regular dictionary.

    Supports:
    - Pydantic v2 models
    - Pydantic v1 models
    - dataclasses or simple objects
    - dictionaries
    """

    if isinstance(result, dict):
        return result

    if hasattr(result, "model_dump"):
        return result.model_dump()

    if hasattr(result, "dict"):
        return result.dict()

    if hasattr(result, "__dict__"):
        return vars(result)

    raise TypeError(
        f"Unsupported orchestrator result type: {type(result).__name__}"
    )


def compare_result(
    actual: dict[str, Any],
    expected: dict[str, Any],
) -> list[str]:
    """
    Return a list containing every failed expectation.
    """

    failures = []

    for field, expected_value in expected.items():
        actual_value = actual.get(field)

        if actual_value != expected_value:
            failures.append(
                f"{field}: expected {expected_value!r}, "
                f"received {actual_value!r}"
            )

    return failures


async def run_test(test_number: int, test: RoutingTest) -> bool:
    print("\n" + "=" * 80)
    print(f"TEST {test_number}: {test.message}")
    print("=" * 80)

    try:
        # If your orchestrate function requires keyword arguments,
        # change this to:
        #
        # result = await orchestrate(user_message=test.message)
        #
        result = await analyze_message(test.message)

        actual = convert_result_to_dict(result)

        print("\nORCHESTRATOR RESULT:")
        print(json.dumps(actual, indent=2, default=str))

        failures = compare_result(actual, test.expected)

        print("\nEXPECTED FIELDS:")
        print(json.dumps(test.expected, indent=2, default=str))

        if failures:
            print("\n❌ FAILED")

            for failure in failures:
                print(f"  - {failure}")

            return False

        print("\n✅ PASSED")
        return True

    except Exception as error:
        print("\n💥 ERROR")
        print(f"{type(error).__name__}: {error}")
        return False


async def main() -> None:
    passed = 0
    failed = 0

    for index, test in enumerate(TEST_CASES, start=1):
        success = await run_test(index, test)

        if success:
            passed += 1
        else:
            failed += 1

    print("\n" + "=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)
    print(f"Total:  {len(TEST_CASES)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed == 0:
        print("\n✅ All routing tests passed. You can move on.")
    else:
        print(
            "\n⚠️ Review the failed cases before building the ContextBuilder."
        )


if __name__ == "__main__":
    asyncio.run(main())