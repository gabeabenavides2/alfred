import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class Memory(Base):
    __tablename__ = "memories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    source_message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id"), nullable=True, index=True)

    content = Column(Text, nullable=False)
    memory_type = Column(String, default="fact")  # fact, preference, goal, reminder, note
    importance_score = Column(Float, default=0.5)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="memories")
    source_message = relationship("Message", back_populates="memories")