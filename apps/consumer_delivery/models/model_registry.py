"""
ORM mirrors of the backend's model_version / model_registry tables.

consumer_delivery owns its own SQLAlchemy `Base`, so we redeclare the rows
here in read-only fashion — same pattern as models/sensor_recording.py.
The tables are owned by the backend's Alembic migrations; we never write.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, JSON, String, Integer, Float
from sqlalchemy.dialects.postgresql import UUID

from db.session import Base


class ModelStage(str, enum.Enum):
  DEV        = 'develop'
  STAGING    = 'staging'
  PRODUCTION = 'production'
  ARCHIVED   = 'archived'


class ModelVersion(Base):
  __tablename__ = 'model_version'
  id                   = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  version_tag          = Column(String)
  stage                = Column(Enum(ModelStage, name='modelstage'))
  description          = Column(String)
  feature_set          = Column(JSON)
  preprocessing_config = Column(JSON)
  record_count         = Column(Integer)
  train_ratio          = Column(Float)
  val_ratio            = Column(Float)
  test_ratio           = Column(Float)
  created_at           = Column(DateTime, default=datetime.utcnow)


class ModelRegistry(Base):
  __tablename__ = 'model_registry'
  id             = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  model_name     = Column(String, nullable=False)
  version_id     = Column(UUID(as_uuid=True), ForeignKey('model_version.id'))
  description    = Column(String)
  algorithm      = Column(String)
  stage          = Column(Enum(ModelStage, name='modelstage'))
  hyperparameter = Column(JSON)
  run_id         = Column(String)
  metrics        = Column(JSON)
  artifact_path  = Column(String)
  created_at     = Column(DateTime, default=datetime.utcnow)
