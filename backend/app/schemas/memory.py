from pydantic import BaseModel, Field


class ExtractedMemory(BaseModel):
    content: str
    memory_type: str = Field(default="fact")
    importance_score: float = Field(default=0.5, ge=0.0, le=1.0)


class MemoryExtractionResult(BaseModel):
    should_store: bool
    memories: list[ExtractedMemory] = []