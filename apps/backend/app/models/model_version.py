# models/model_version.py
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, JSON, String, Integer, Float, DateTime, Enum
import uuid
import enum
from datetime import datetime
from app.db.base import Base


# mlflow lifecycle
class ModelStage(str, enum.Enum):
  DEV = 'develop'
  STAGING = 'staging'
  PRODUCTION = 'production'
  ARCHIVED = 'archived'


class ModelVersion(Base):
  __tablename__ = 'model_version'
  id = Column(UUID, primary_key=True, default=uuid.uuid4)
  version_tag = Column(String) # Readable version
  stage = Column(Enum(ModelStage)) # Lifecycle stage
  description = Column(String) # Optional notes about this version
  feature_set = Column(JSON) # List of feature used, eg: ['eda', 'ibi', 'hrv']
  preprocessing_config = Column(JSON) # Processing rules for raw data
  record_count = Column(Integer) # total number of data available for training after processing and  cleaning
  train_ratio = Column(Float) # Proportion used for training
  val_ratio = Column(Float) # Proportion used for validation and hyperparameter tunning
  test_ratio = Column(Float) # Proportion for final evaluation
  created_at = Column(DateTime, default=datetime.utcnow)
