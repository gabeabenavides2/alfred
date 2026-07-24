"""
Live integration tests for Alfred's orchestrator.

These tests call the real configured LLM provider. They verify that the
orchestrator correctly decides when memory retrieval is needed and creates
focused memory queries.

Run from the backend directory with:

    python -m pytest test_orchestrator_multi_query.py -v -s

Because these tests call a real LLM:
- Your provider API key must be configured.
- Internet access is required.
- The exact query wording may vary.
- The tests check behavior rather than exact output text.
"""

import pytest

# Change this import only if analyze_message is stored in a different file.
from app.services.orchestrator_service import analyze_message


def print_result(message: str, result) -> None:
    """
    Print the orchestrator result so it can be inspected during testing.
    """

    print("\n")
    print("=" * 70)
    print("USER MESSAGE")
    print(message)
    print("-" * 70)
    print("ORCHESTRATOR RESULT")
    print(f"Intent:                {result.intent}")
    print(f"Can respond directly:  {result.can_respond_directly}")
    print(f"Direct response:       {result.direct_response}")
    print(f"Tool required:         {result.tool_required}")
    print(f"Tools:                 {result.tools}")
    print(f"Retrieve memories:     {result.retrieve_memories}")
    print(f"Memory queries:        {result.memory_queries}")
    print(f"Retrieve files:        {result.retrieve_files}")
    print(f"Memories to store:     {result.memories}")
    print("=" * 70)


@pytest.mark.asyncio
async def test_generates_two_queries_for_two_memory_needs():
    """
    A question about two unrelated personal facts should produce at least
    two focused memory queries.
    """

    message = (
        "How much is my monthly rent, and when do I want Alfred completed?"
    )

    result = await analyze_message(message)

    print_result(message, result)

    assert result.retrieve_memories is True
    assert len(result.memory_queries) >= 2

    combined_queries = " ".join(result.memory_queries).lower()

    assert "rent" in combined_queries
    assert "alfred" in combined_queries

    assert result.can_respond_directly is False
    assert result.direct_response is None
    assert result.retrieve_files is False


@pytest.mark.asyncio
async def test_generates_one_query_for_one_memory_need():
    """
    A question about one personal fact should produce at least one focused
    memory query.
    """

    message = "How much is my monthly rent?"

    result = await analyze_message(message)

    print_result(message, result)

    assert result.retrieve_memories is True
    assert len(result.memory_queries) >= 1

    combined_queries = " ".join(result.memory_queries).lower()

    assert "rent" in combined_queries
    assert result.can_respond_directly is False
    assert result.direct_response is None


@pytest.mark.asyncio
async def test_does_not_retrieve_memory_for_general_question():
    """
    A general knowledge question should not require personal memory.
    """

    message = "Explain how semantic search works."

    result = await analyze_message(message)

    print_result(message, result)

    assert result.retrieve_memories is False
    assert result.memory_queries == []
    assert result.retrieve_files is False


@pytest.mark.asyncio
async def test_does_not_retrieve_memory_for_simple_chat():
    """
    A greeting should not trigger memory retrieval.
    """

    message = "Hello Alfred."

    result = await analyze_message(message)

    print_result(message, result)

    assert result.retrieve_memories is False
    assert result.memory_queries == []
    assert result.retrieve_files is False


@pytest.mark.asyncio
async def test_detects_file_retrieval():
    """
    A request that clearly refers to a stored document should request
    file retrieval rather than memory retrieval.
    """

    message = (
        "Look at my uploaded Alfred build plan and tell me what I am "
        "supposed to work on Friday."
    )

    result = await analyze_message(message)

    print_result(message, result)

    assert result.retrieve_files is True
    assert result.can_respond_directly is False
    assert result.direct_response is None


@pytest.mark.asyncio
async def test_new_information_is_stored_without_unnecessary_retrieval():
    """
    New durable user information should be extracted as memory, but storing
    it should not automatically trigger existing-memory retrieval.
    """

    message = (
        "My monthly rent is $690, and I want Alfred completed by "
        "August 15, 2026."
    )

    result = await analyze_message(message)

    print_result(message, result)

    assert result.retrieve_memories is False
    assert result.memory_queries == []
    assert len(result.memories) >= 2

    stored_content = " ".join(
        memory.content for memory in result.memories
    ).lower()

    assert "690" in stored_content
    assert "alfred" in stored_content
    assert "august 15" in stored_content


@pytest.mark.asyncio
async def test_multiple_personal_topics_create_focused_queries():
    """
    Several separate personal information needs should be divided into
    focused queries rather than copied as one long user message.
    """

    message = (
        "What programming language do I prefer, how much is my rent, "
        "and what is my target completion date for Alfred?"
    )

    result = await analyze_message(message)

    print_result(message, result)

    assert result.retrieve_memories is True
    assert len(result.memory_queries) >= 3

    combined_queries = " ".join(result.memory_queries).lower()

    assert (
        "programming" in combined_queries
        or "language" in combined_queries
    )
    assert "rent" in combined_queries
    assert "alfred" in combined_queries

    normalized_message = " ".join(message.lower().split())

    for query in result.memory_queries:
        normalized_query = " ".join(query.lower().split())

        # A generated query should not simply copy the entire user message.
        assert normalized_query != normalized_message


@pytest.mark.asyncio
async def test_memory_queries_do_not_contain_search_commands():
    """
    Queries should describe the needed information rather than containing
    commands such as 'find' or 'search for'.
    """

    message = (
        "What is my rent and what deadline did I set for Alfred?"
    )

    result = await analyze_message(message)

    print_result(message, result)

    assert result.retrieve_memories is True
    assert len(result.memory_queries) >= 2

    forbidden_phrases = [
        "find ",
        "search for",
        "retrieve ",
        "look up",
    ]

    for query in result.memory_queries:
        lowered_query = query.lower()

        for phrase in forbidden_phrases:
            assert phrase not in lowered_query