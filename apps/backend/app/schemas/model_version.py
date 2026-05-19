# schemas/model_version.py
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.model_version import ModelStage


class ModelVersionCreate(BaseModel):
  version_tag: Optional[str] = None
  stage: Optional[ModelStage] = None
  description: Optional[str] = None
  feature_set: Optional[list[str]] = None
  preprocessing_config: Optional[dict] = None
  record_count: Optional[int] = None
  train_ratio: Optional[float] = None
  val_ratio: Optional[float] = None
  test_ratio: Optional[float] = None


class ModelVersionResponse(BaseModel):
  id: UUID
  version_tag: Optional[str] = None
  stage: Optional[ModelStage] = None
  description: Optional[str] = None
  feature_set: Optional[list[str]] = None
  preprocessing_config: Optional[dict] = None
  record_count: Optional[int] = None
  train_ratio: Optional[float] = None
  val_ratio: Optional[float] = None
  test_ratio: Optional[float] = None
  created_at: datetime

  model_config = ConfigDict(from_attributes=True)
