import json

from app.ai.provider_factory import get_ai_provider
from app.schemas.orchestrator import OrchestratorResult


ORCHESTRATOR_SYSTEM_PROMPT = """
You are Alfred's orchestrator.

Your job is to analyze the user's message and return ONLY valid JSON.

Decide:
1. The user's intent
2. Whether Alfred can respond directly
3. Any long-term memories to store
4. Whether tools are needed
5. Whether memory/file/note retrieval is needed

Allowed intents:
chat, question, store_information, create_reminder, search_memory, search_files, send_email, calendar_query, task_request, unknown

Return exactly this JSON shape:
{
  "intent": "chat",
  "can_respond_directly": true,
  "direct_response": "A short response Alfred can say now, or null",
  "memories": [
    {
      "content": "Clean long-term memory sentence.",
      "memory_type": "fact",
      "importance_score": 0.8
    }
  ],
  "tool_required": false,
  "tools": [],
  "retrieve_memories": false,
  "retrieve_files": false,
  "retrieve_notes": false
}

Memory rules:
- Store personal facts, preferences, goals, deadlines, responsibilities, projects, school/work info, finances, relationships.
- Do not store small talk, generic questions, temporary phrasing, or assistant responses.
- Allowed memory_type values: fact, preference, goal, reminder, note.

Direct response rules:
- If the message only needs acknowledgement or simple chat, set can_respond_directly true.
- If the message requires memory retrieval, file retrieval, or tools, set can_respond_directly false.
- If can_respond_directly is false, direct_response must be null.
"""


async def analyze_message(message: str) -> OrchestratorResult:
    provider = get_ai_provider()

    messages = [
        {
            "role": "system",
            "content": ORCHESTRATOR_SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": message,
        },
    ]

    raw_response = await provider.generate_raw_response(messages)

    try:
        parsed = json.loads(raw_response)
        print("\n========== ORCHESTRATOR ==========")
        print(json.dumps(parsed, indent=2))
        print("==================================\n")
        return OrchestratorResult(**parsed)

    except Exception:
        return OrchestratorResult(
            intent="unknown",
            can_respond_directly=False,
            direct_response=None,
            memories=[],
            tool_required=False,
            tools=[],
            retrieve_memories=False,
            retrieve_files=False,
            retrieve_notes=False,
        )