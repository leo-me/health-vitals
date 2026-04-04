from sqlalchemy import Column, String, Integer ,DateTime, Float, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import enum
from app.db.base import Base

class UserTypeEnum(str, enum.Enum):
  PATIENT = "patient"
  CAREGIVER = "caregiver"
  ADMIN = 'admin'

class SexEnum(str, enum.Enum):
    male = "male"
    female = "female"
    intersex = "intersex"      # Intersex individuals, physiological level


class User(Base):
  __tablename__ = "users"
  id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  email = Column(String(30), nullable=False)
  password=Column(String(60), nullable=False)
  name = Column(String(40), nullable=True)
  sex = Column(Enum(SexEnum), nullable=True)
  age = Column(Integer, nullable=True)
  weight = Column(Float, nullable=True)
  illness_history = Column(String(200), nullable=True)
  user_type = Column(Enum(UserTypeEnum), nullable=True)
  caregiver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
  created_at = Column(DateTime, default=datetime.utcnow)