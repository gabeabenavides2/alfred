from pydantic import BaseModel
from uuid import UUID

class ChatRequest(BaseModel):
    message: str
    conversation_id: UUID | None = None


class ChatResponse(BaseModel):
    response: str
    conversation_id: UUID 