import json

from pydantic import ValidationError

from app.ai.provider_factory import get_ai_provider
from app.schemas.memory import MemoryExtractionResult


MEMORY_EXTRACTION_SYSTEM_PROMPT = """
You are Alfred's long-term memory extraction system.

Analyze the user's message and extract only information that would be useful
in future conversations.

Store information such as:
- Stable personal facts
- Preferences
- Long-term goals
- Important plans
- Deadlines
- Recurring responsibilities
- Useful notes the user may want recalled later

Do not store:
- Casual conversation
- Temporary emotions
- General questions
- Information already presented as hypothetical
- Assistant responses
- Commands that contain no lasting information
- Trivial details unlikely to matter later

Allowed memory types:
- fact
- preference
- goal
- reminder
- note

Importance score guide:
- 0.1 to 0.3: minor but potentially useful
- 0.4 to 0.6: useful general information
- 0.7 to 0.8: important long-term information
- 0.9 to 1.0: critical goal, deadline, obligation, or safety-related information

Formatting rules:
- Refer to the person as "The user."
- Include an explicit subject.
- Include ending punctuation.
- Preserve important dates, amounts, organizations, and relationships.
- Do not use sentence fragments.

Return valid JSON only, using this exact format:

{
  "memories": [
    {
      "content": "Standalone memory statement",
      "memory_type": "fact",
      "importance_score": 0.5
    }
  ]
}

If nothing should be remembered, return:

{
  "memories": []
}
""".strip()


class MemoryExtractor:
    """
    Uses an LLM to identify long-term memories in a user's message.

    This class only extracts and validates memory candidates.
    MemoryManager is responsible for deduplication, embeddings, and storage.
    """

    def __init__(self):
        self.ai_provider = get_ai_provider()

    async def extract_memories(
        self,
        user_message: str,
    ) -> MemoryExtractionResult:
        cleaned_message = user_message.strip()

        if not cleaned_message:
            return MemoryExtractionResult()

        messages = [
            {
                "role": "system",
                "content": MEMORY_EXTRACTION_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": cleaned_message,
            },
        ]

        raw_response = await self.ai_provider.generate_response(
            messages
        )

        parsed_response = self._parse_json_response(raw_response)

        try:
            return MemoryExtractionResult.model_validate(
                parsed_response
            )
        except ValidationError as error:
            raise ValueError(
                "The memory extractor returned an invalid response."
            ) from error

    @staticmethod
    def _parse_json_response(
        raw_response: str,
    ) -> dict:
        """
        Parse the LLM response while tolerating Markdown JSON fences.
        """

        cleaned_response = raw_response.strip()

        if cleaned_response.startswith("```"):
            cleaned_response = (
                cleaned_response
                .removeprefix("```json")
                .removeprefix("```")
                .removesuffix("```")
                .strip()
            )

        try:
            parsed_response = json.loads(cleaned_response)
        except json.JSONDecodeError as error:
            raise ValueError(
                "The memory extractor did not return valid JSON."
            ) from error

        if not isinstance(parsed_response, dict):
            raise ValueError(
                "The memory extractor response must be a JSON object."
            )

        return parsed_response