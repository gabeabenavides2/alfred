import asyncio
from uuid import UUID

from sqlalchemy import select

from app.db.database import SessionLocal
from app.db.models.embedding import Embedding
from app.db.models.memory import Memory
from app.services.memory_pipeline import MemoryPipeline


TEST_USER_ID = UUID("852878e3-cb71-441a-8294-aa04e79d2c86")


async def main() -> None:
    db = SessionLocal()

    try:
        pipeline = MemoryPipeline(db)

        stored = await pipeline.process_message(
            user_id=TEST_USER_ID,
            user_message=(
                "My birthday is feb 17th"
                "I want Alfred finished by August 15."
            ),
        )

        db.commit()

        print("\nStored memories:")

        for memory in stored:
            print(
                {
                    "id": str(memory.id),
                    "content": memory.content,
                    "memory_type": memory.memory_type,
                    "importance_score": memory.importance_score,
                }
            )

        memories = db.execute(
            select(Memory).where(
                Memory.user_id == TEST_USER_ID
            )
        ).scalars().all()

        embeddings = db.execute(
            select(Embedding)
        ).scalars().all()

        print(f"\nTotal user memories: {len(memories)}")
        print(f"Total embeddings: {len(embeddings)}")

        retrieved = await pipeline.manager.search_memories(
            user_id=TEST_USER_ID,
            query="How much do I pay for my apartment?",
            limit=5,
        )

        print("\nRetrieved memories:")

        for memory in retrieved:
            print(
                {
                    "content": memory.content,
                    "similarity": round(
                        memory.similarity_score,
                        4,
                    ),
                    "importance": memory.importance_score,
                    "ranking": round(
                        memory.ranking_score,
                        4,
                    ),
                }
            )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())