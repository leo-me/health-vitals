import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from db.session import Base


class SensorType(enum.Enum):
    HEART_RATE = 'heart_rate'
    EDA = 'EDA'
    ACCELEROMETER = 'accelerometer'


class SensorRecording(Base):
    __tablename__ = "sensor_recordings"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(UUID(as_uuid=True), ForeignKey("devices.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    sensor_type = Column(Enum(SensorType, name="sensortype"), nullable=False)
    data = Column(JSONB, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
