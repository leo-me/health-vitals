from sqlalchemy import Column, String, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import enum
from app.db.base import Base

class DeviceType(enum.Enum):
  PHONE = 'phone'
  SENSOR = 'sensor'
  WATCH = 'watch'



class Device(Base):
  __tablename__ = "devices"
  id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  serial_number = Column(String, unique=True, nullable=True)
  user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
  type = Column(Enum(DeviceType), nullable=False) # sensor watch 或者 手机
  push_token = Column(String, nullable=True)  # push 路径 不确定这样定义对不对 理论上只有watch 和手机可以退送
  created_at = Column(DateTime, default=datetime.utcnow)

