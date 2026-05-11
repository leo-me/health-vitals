# models/model_registry.py

from sqlalchemy import Column, JSON, String, ForeignKey, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

from app.db.base import Base


from app.models.model_version import ModelStage


class ModelRegistry(Base):
  __tablename__ = 'model_registry'
  id = Column(UUID, primary_key=True, default=uuid.uuid4)
  model_name = Column(String, nullable=False) 
  version_id = Column(UUID, ForeignKey('model_version.id')) # model version id
  description = Column(String) # Optional model registry info
  algorithm = Column(String) # algorithm name
  stage = Column(Enum(ModelStage)) # current stage of model
  hyperparameter = Column(JSON) # Training configuration before training, eg: {"n_estimators": 100, "max_depth": 5}
  run_id = Column(String) # mlflow run_id
  metrics=Column(JSON) # evaluation metrics ,eg: {"accuracy": 0.87, "precision": 0.84, "recall": 0.91}
  artifact_path = Column(String) # model file path
  created_at = Column(DateTime, default=datetime.utcnow)