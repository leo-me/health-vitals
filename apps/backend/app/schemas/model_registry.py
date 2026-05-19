# schemas/model_registry.py
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.model_version import ModelStage


class ModelRegistryCreate(BaseModel):
  model_name: str
  version_id: Optional[UUID] = None
  description: Optional[str] = None
  algorithm: Optional[str] = None
  stage: Optional[ModelStage] = None
  hyperparameter: Optional[dict] = None
  run_id: Optional[str] = None
  metrics: Optional[dict] = None
  artifact_path: Optional[str] = None

  # `model_*` would otherwise hit Pydantic v2's protected namespace warning.
  model_config = ConfigDict(protected_namespaces=())


class ModelRegistryResponse(BaseModel):
  id: UUID
  model_name: str
  version_id: Optional[UUID] = None
  description: Optional[str] = None
  algorithm: Optional[str] = None
  stage: Optional[ModelStage] = None
  hyperparameter: Optional[dict] = None
  run_id: Optional[str] = None
  metrics: Optional[dict] = None
  artifact_path: Optional[str] = None
  created_at: datetime

  model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class ModelRegistryStageUpdate(BaseModel):
  stage: ModelStage
