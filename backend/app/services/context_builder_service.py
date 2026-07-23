from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.message import Message
from app.schemas.context import BuiltContext, ContextMessage
from app.schemas.orchestrator import OrchestratorResult
from app.services.memory_manager import MemoryManager


class ContextBuilder:
    """
    Retrieves and assembles the context Alfred needs before
    generating the final response.

    Responsibilities:
    - Retrieve relevant long-term memories
    - Retrieve recent conversation messages
    - Return structured context data

    This service does not format the final LLM prompt and does
    not call the AI provider.
    """

    def __init__(self, db: Session):
        self.db = db
        self.memory_manager = MemoryManager(db)

    async def build_context(
        self,
        user_id: UUID,
        conversation_id: UUID,
        user_message: str,
        analysis: OrchestratorResult,
        conversation_limit: int = 20,
        memory_limit: int = 5,
    ) -> BuiltContext:
        """
        Build the context needed for Alfred's final response.
        """

        memories = []

        if analysis.retrieve_memories:
            memories = await self.memory_manager.search_memories(
                user_id=user_id,
                query=user_message,
                limit=memory_limit,
            )

        conversation_messages = self._get_conversation_messages(
            conversation_id=conversation_id,
            limit=conversation_limit,
        )

        return BuiltContext(
            memories=memories,
            conversation_messages=conversation_messages,
        )

    def _get_conversation_messages(
        self,
        conversation_id: UUID,
        limit: int,
    ) -> list[ContextMessage]:
        """
        Return the most recent conversation messages in
        chronological order.
        """

        if limit <= 0:
            return []

        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )

        result = self.db.execute(statement)
        messages = list(result.scalars().all())

        messages.reverse()

        return [
            ContextMessage(
                role=message.role,
                content=message.content,
            )
            for message in messages
        ]