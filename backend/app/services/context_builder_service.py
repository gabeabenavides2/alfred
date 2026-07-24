from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.message import Message
from app.schemas.context import BuiltContext, ContextMessage
from app.schemas.memory import RetrievedMemory
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
        results_per_query: int = 5,
    ) -> BuiltContext:
        """
        Build the context needed for Alfred's final response.
        """

        memories: list[RetrievedMemory] = []

        if analysis.retrieve_memories:
            memory_queries = [
                query.strip()
                for query in analysis.memory_queries
                if query.strip()
            ]

            # Safety fallback in case the orchestrator requests
            # retrieval but fails to generate a query.
            if not memory_queries:
                memory_queries = [user_message]

            memories = await self._retrieve_memories_for_queries(
                user_id=user_id,
                queries=memory_queries,
                results_per_query=results_per_query,
                final_limit=memory_limit,
            )

        conversation_messages = self._get_conversation_messages(
            conversation_id=conversation_id,
            limit=conversation_limit,
        )

        return BuiltContext(
            memories=memories,
            conversation_messages=conversation_messages,
        )

    async def _retrieve_memories_for_queries(
        self,
        user_id: UUID,
        queries: list[str],
        results_per_query: int,
        final_limit: int,
    ) -> list[RetrievedMemory]:
        """
        Search memories using multiple focused queries.

        Duplicate memories are removed by ID. If the same memory
        appears in multiple searches, the version with the highest
        ranking score is retained.
        """

        unique_memories: dict[UUID, RetrievedMemory] = {}

        for query in queries:
            results = await self.memory_manager.search_memories(
                user_id=user_id,
                query=query,
                limit=results_per_query,
            )

            for memory in results:
                existing = unique_memories.get(memory.id)

                if (
                    existing is None
                    or memory.ranking_score > existing.ranking_score
                ):
                    unique_memories[memory.id] = memory

        ranked_memories = sorted(
            unique_memories.values(),
            key=lambda memory: memory.ranking_score,
            reverse=True,
        )

        return ranked_memories[:final_limit]

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