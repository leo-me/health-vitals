from sqlalchemy import Column, String, Integer ,DateTime, Float, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import enum
from app.db.base import Base

class UserTypeEnum(enum.Enum):
  PATIENT = "patient"
  CAREGIVER = "caregiver"
  ADMIN = 'admin'


class User(Base):
  __tablename__ = "users"
  id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  name = Column(String(40), nullable=False)
  sex = Column(String(10), nullable=True)
  age = Column(Integer, nullable=True)
  weight = Column(Float, default=0)
  illness_history = Column(String(200), nullable=True)
  user_type = Column(Enum(UserTypeEnum), nullable=False)
  caregiver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
  created_at = Column(DateTime, default=datetime.utcnow)