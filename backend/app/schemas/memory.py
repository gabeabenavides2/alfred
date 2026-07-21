from enum import Enum
from dataclasses import dataclass
from pydantic import BaseModel, Field
from uuid import UUID


class MemoryType(str, Enum):
    FACT = "fact"
    PREFERENCE = "preference"
    GOAL = "goal"
    REMINDER = "reminder"
    NOTE = "note"


class ExtractedMemory(BaseModel):
    content: str
    memory_type: MemoryType = MemoryType.FACT
    importance_score: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
    )


class MemoryExtractionResult(BaseModel):
    memories: list[ExtractedMemory] = Field(
        default_factory=list
    )

@dataclass
class RetrievedMemory:
    """
    A memory returned from semantic search.

    This is separate from the SQLAlchemy model because it includes
    calculated scores that are not stored in the database.
    """

    id: UUID
    content: str
    memory_type: str
    importance_score: float
    similarity_score: float
    ranking_score: float