from uuid import UUID
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.ai.providers.embeddings.provider_factory import get_embedding_provider
from app.db.models.embedding import Embedding
from app.db.models.memory import Memory
from app.schemas.memory import RetrievedMemory





class MemoryManager:
    """
    Handles Alfred's long-term memory operations.

    Responsibilities:
    - Create memories
    - Generate and store embeddings
    - Detect duplicate memories
    - Search memories semantically
    - Rank retrieved memories
    - Update memories
    - Delete memories
    """

    def __init__(self, db: Session):
        self.db = db
        self.embedding_provider = get_embedding_provider()

    async def create_memory(
        self,
        user_id: UUID,
        content: str,
        memory_type: str = "fact",
        importance_score: float = 0.5,
        source_message_id: UUID | None = None,
    ) -> Memory | None:
        """
        Create a memory and its vector embedding.

        Returns:
            The newly created Memory.

            Returns None when the memory is empty or is considered
            a semantic duplicate of an existing memory.
        """

        cleaned_content = self._clean_content(content)

        if not cleaned_content:
            return None

        validated_importance = self._validate_importance_score(
            importance_score
        )

        memory_embedding = await self._generate_embedding(
            cleaned_content
        )

        duplicate = await self.find_duplicate_memory(
            user_id=user_id,
            embedding_vector=memory_embedding,
        )

        if duplicate is not None:
            return None

        memory = Memory(
            user_id=user_id,
            source_message_id=source_message_id,
            content=cleaned_content,
            memory_type=memory_type,
            importance_score=validated_importance,
        )

        self.db.add(memory)

        # Flush sends the insert to PostgreSQL without committing.
        # This gives us memory.id so the embedding can reference it.
        self.db.flush()

        embedding = Embedding(
            memory_id=memory.id,
            vector=memory_embedding,
            embedding_provider=self.embedding_provider.provider_name,
            embedding_model=self.embedding_provider.model_name,
            dimensions=self.embedding_provider.dimensions,
        )

        self.db.add(embedding)

        return memory

    async def search_memories(
        self,
        user_id: UUID,
        query: str,
        limit: int = 5,
        similarity_threshold: float = 0.25,
    ) -> list[RetrievedMemory]:
        """
        Search a user's memories using cosine similarity.

        The similarity threshold is hardcoded to 0.55 for now.

        A similarity score closer to 1 means the memory is more
        semantically related to the query.
        """

        cleaned_query = self._clean_content(query)

        if not cleaned_query:
            return []

        if limit <= 0:
            return []

        query_embedding = await self._generate_embedding(
            cleaned_query
        )

        distance = Embedding.vector.cosine_distance(
            query_embedding
        ).label("distance")

        # Pull more candidates than we ultimately return so ranking
        # has a larger group of memories to evaluate.
        candidate_limit = max(limit * 3, limit)

        statement = (
            select(
                Memory,
                distance,
            )
            .join(
                Embedding,
                Embedding.memory_id == Memory.id,
            )
            .where(
                Memory.user_id == user_id,
                Embedding.vector.is_not(None),
            )
            .order_by(distance.asc())
            .limit(candidate_limit)
        )

        result = self.db.execute(statement)
        rows = result.all()

        retrieved_memories: list[RetrievedMemory] = []

        for memory, cosine_distance in rows:
            if cosine_distance is None:
                continue

            cosine_distance = float(cosine_distance)
            similarity_score = 1.0 - cosine_distance

            print(
                f"Candidate: {memory.content}\n"
                f"Distance: {cosine_distance:.4f}\n"
                f"Similarity: {similarity_score:.4f}\n"
            )

            if similarity_score < similarity_threshold:
                print(
                    f"Rejected: below threshold "
                    f"{similarity_threshold:.4f}\n"
                )
                continue

            ranking_score = (
                similarity_score * 0.85
                + float(memory.importance_score) * 0.15
            )

            retrieved_memories.append(
                RetrievedMemory(
                    id=memory.id,
                    content=memory.content,
                    memory_type=memory.memory_type,
                    importance_score=float(
                        memory.importance_score
                    ),
                    similarity_score=similarity_score,
                    ranking_score=ranking_score,
                )
            )

        retrieved_memories.sort(
            key=lambda memory: memory.ranking_score,
            reverse=True,
        )

        return retrieved_memories[:limit]

    async def find_duplicate_memory(
        self,
        user_id: UUID,
        embedding_vector: list[float],
        similarity_threshold: float = 0.90,
    ) -> Memory | None:
        """
        Find an existing memory that is semantically almost identical
        to a new memory.

        This prevents Alfred from repeatedly storing memories such as:

            "My rent is $690."
            "I pay $690 in rent."
            "Rent costs me $690."

        The duplicate threshold is intentionally higher than the
        normal retrieval threshold.
        """

        distance = Embedding.vector.cosine_distance(
            embedding_vector
        ).label("distance")

        statement = (
            select(
                Memory,
                distance,
            )
            .join(
                Embedding,
                Embedding.memory_id == Memory.id,
            )
            .where(
                Memory.user_id == user_id,
                Embedding.vector.is_not(None),
            )
            .order_by(distance.asc())
            .limit(1)
        )

        result = self.db.execute(statement)
        row = result.first()

        if row is None:
            return None

        memory, cosine_distance = row

        if cosine_distance is None:
            return None

        similarity_score = 1.0 - float(cosine_distance)

        if similarity_score >= similarity_threshold:
            return memory

        return None

    async def get_memory(
        self,
        user_id: UUID,
        memory_id: UUID,
    ) -> Memory | None:
        """
        Get one memory while ensuring it belongs to the current user.
        """

        statement = select(Memory).where(
            Memory.id == memory_id,
            Memory.user_id == user_id,
        )

        result = self.db.execute(statement)

        return result.scalar_one_or_none()

    async def get_all_memories(
        self,
        user_id: UUID,
        limit: int = 100,
    ) -> list[Memory]:
        """
        Return a user's most recently created memories.
        """

        if limit <= 0:
            return []

        statement = (
            select(Memory)
            .where(Memory.user_id == user_id)
            .order_by(Memory.created_at.desc())
            .limit(limit)
        )

        result = self.db.execute(statement)

        return list(result.scalars().all())

    async def update_memory(
        self,
        user_id: UUID,
        memory_id: UUID,
        content: str | None = None,
        memory_type: str | None = None,
        importance_score: float | None = None,
    ) -> Memory | None:
        """
        Update a memory.

        When the memory content changes, its embedding is replaced
        with a newly generated embedding.
        """

        memory = await self.get_memory(
            user_id=user_id,
            memory_id=memory_id,
        )

        if memory is None:
            return None

        content_changed = False

        if content is not None:
            cleaned_content = self._clean_content(content)

            if not cleaned_content:
                raise ValueError(
                    "Memory content cannot be empty."
                )

            if cleaned_content != memory.content:
                memory.content = cleaned_content
                content_changed = True

        if memory_type is not None:
            memory.memory_type = memory_type

        if importance_score is not None:
            memory.importance_score = (
                self._validate_importance_score(
                    importance_score
                )
            )

        if content_changed:
            new_embedding = await self._generate_embedding(
                memory.content
            )

            statement = select(Embedding).where(
                Embedding.memory_id == memory.id
            )

            result = self.db.execute(statement)
            embedding_record = result.scalar_one_or_none()

            if embedding_record is None:
                embedding_record = Embedding(
                    memory_id=memory.id,
                    vector=new_embedding,
                    embedding_provider=(
                        self.embedding_provider.provider_name
                    ),
                    embedding_model=(
                        self.embedding_provider.model_name
                    ),
                    dimensions=self.embedding_provider.dimensions,
                )

                self.db.add(embedding_record)
            else:
                embedding_record.vector = new_embedding
                embedding_record.embedding_provider = (
                    self.embedding_provider.provider_name
                )
                embedding_record.embedding_model = (
                    self.embedding_provider.model_name
                )
                embedding_record.dimensions = (
                    self.embedding_provider.dimensions
                )

        self.db.flush()

        return memory

    async def delete_memory(
        self,
        user_id: UUID,
        memory_id: UUID,
    ) -> bool:
        """
        Delete a memory belonging to the current user.

        The embedding should be removed automatically through
        ON DELETE CASCADE on Embedding.memory_id.
        """

        memory = await self.get_memory(
            user_id=user_id,
            memory_id=memory_id,
        )

        if memory is None:
            return False

        self.db.delete(memory)

        return True

    async def format_memories_for_prompt(
        self,
        memories: list[RetrievedMemory],
    ) -> str:
        """
        Convert retrieved memories into text that can be injected into
        Alfred's system prompt.
        """

        if not memories:
            return "No relevant long-term memories were found."

        formatted_memories: list[str] = []

        for memory in memories:
            formatted_memories.append(
                f"- [{memory.memory_type}] {memory.content}"
            )

        return "\n".join(formatted_memories)

    async def _generate_embedding(
        self,
        text: str,
    ) -> list[float]:
        """
        Generate an embedding while validating the provider response.
        """

        embedding = await self.embedding_provider.embed_text(
            text
        )

        if not embedding:
            raise ValueError(
                "The embedding provider returned an empty embedding."
            )

        return embedding

    @staticmethod
    def _clean_content(content: str) -> str:
        """
        Normalize memory text before saving or searching.
        """

        return " ".join(content.strip().split())

    @staticmethod
    def _validate_importance_score(
        importance_score: float,
    ) -> float:
        """
        Ensure importance remains between 0.0 and 1.0.
        """

        return max(
            0.0,
            min(float(importance_score), 1.0),
        )