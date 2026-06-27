import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)

    name = Column(String, nullable=False, index=True)
    preferred_name = Column(String, nullable=True, index=True)
    timezone = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    conversations = relationship("Conversation", back_populates="user", cascade="all, delete")
    memories = relationship("Memory", back_populates="user", cascade="all, delete")
    files = relationship("File", back_populates="user", cascade="all, delete")