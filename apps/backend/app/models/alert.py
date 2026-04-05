from sqlalchemy import Column, String, Integer ,DateTime, Float, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.db.base import Base


class Alert(Base):
  __tablename__ = "alerts"
  id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  recording_id = Column(UUID(as_uuid=True), ForeignKey("sensor_recordings.id"), nullable=False)
  user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
  content = Column(String, nullable=False)
  created_at = Column(DateTime, default=datetime.utcnow)
