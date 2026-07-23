from pydantic import BaseModel, Field

from app.schemas.memory import RetrievedMemory


class ContextMessage(BaseModel):
    """
    A conversation message included in the final LLM context.
    """

    role: str
    content: str


class BuiltContext(BaseModel):
    """
    Information retrieved and assembled for Alfred's final response.

    This schema contains raw context data. It does not format the
    final prompt or call the AI provider.
    """

    memories: list[RetrievedMemory] = Field(default_factory=list)
    conversation_messages: list[ContextMessage] = Field(default_factory=list)