import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class File(Base):
    __tablename__ = "files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    file_name = Column(String, nullable=False)
    file_type = Column(String, nullable=True)
    storage_path = Column(String, nullable=False)

    file_metadata = Column(JSON, default={})

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="files")