from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models.memory import Memory
from app.services.memory_extractor import MemoryExtractor
from app.services.memory_manager import MemoryManager


class MemoryPipeline:
    """
    Coordinates memory extraction and storage.

    MemoryExtractor decides what should be remembered.
    MemoryManager validates, deduplicates, embeds, and stores it.
    """

    def __init__(self, db: Session):
        self.extractor = MemoryExtractor()
        self.manager = MemoryManager(db)

    async def process_message(
        self,
        user_id: UUID,
        user_message: str,
        source_message_id: UUID | None = None,
    ) -> list[Memory]:
        extraction_result = await self.extractor.extract_memories(
            user_message
        )

        stored_memories: list[Memory] = []

        for candidate in extraction_result.memories:
            memory = await self.manager.create_memory(
                user_id=user_id,
                content=candidate.content,
                memory_type=candidate.memory_type.value,
                importance_score=candidate.importance_score,
                source_message_id=source_message_id,
            )

            if memory is not None:
                stored_memories.append(memory)

        return stored_memories
