from typing import Any

from pydantic import BaseModel, Field

from app.schemas.memory import ExtractedMemory
from app.ai.model_routes import ModelRoute

class ToolRequest(BaseModel):
    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class OrchestratorResult(BaseModel):
    intent: str

    can_respond_directly: bool
    direct_response: str | None = None

    memories: list[ExtractedMemory] = Field(default_factory=list)

    tool_required: bool = False
    tools: list[str] = Field(default_factory=list)

    retrieve_memories: bool = False
    retrieve_files: bool = False
    memory_queries: list[str] = Field(
        default_factory=list,
        max_length=4,
    )

    model_route: ModelRoute = ModelRoute.CHAT