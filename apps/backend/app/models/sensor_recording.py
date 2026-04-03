from sqlalchemy import Column, String, Integer ,DateTime, Float, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from datetime import datetime
import enum
from app.db.base import Base

class SensorType(enum.Enum):
  HEART_RATE = 'heart_rate'
  EDA = 'EDA'
  ACCELEROMETER = 'accelerometer'


class SensorRecording(Base):
  __tablename__ = "sensor_recordings"
  id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  device_id = Column(UUID(as_uuid=True), ForeignKey("devices.id"), nullable=True)
  user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
  timestamp = Column(DateTime, default=datetime.utcnow)
  sensor_type = Column(Enum(SensorType), nullable=False)
  data = Column(JSONB, nullable=False)
