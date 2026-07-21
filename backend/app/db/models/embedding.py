import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import Integer
from app.core.config import settings

from app.db.database import Base


class Embedding(Base):
    __tablename__ = "embeddings"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    memory_id = Column(
        UUID(as_uuid=True),
        ForeignKey("memories.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    vector = Column(
        Vector(settings.embedding_dimensions),
        nullable=False,
    )

    embedding_provider = Column(String, nullable=False)
    embedding_model = Column(String, nullable=False)
    dimensions = Column(Integer, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    memory = relationship("Memory", back_populates="embedding")