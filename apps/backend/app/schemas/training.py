# schemas/training.py
from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


Mode = Literal["simulation", "production"]
JobStatus = Literal["pending", "running", "succeeded", "failed"]


class TrainingRequest(BaseModel):
  mode: Mode = "simulation"
  threshold: float = Field(0.50, ge=0.0, le=1.0)
  dataset_size: int = Field(1_000, ge=10, le=1_000_000)
  feature_version: Literal["v1", "v2"] = "v1"
  random_state: int = 42
  # Inject Gaussian noise on X before train/test split so the gate fails on
  # purpose — exp2 uses this to exercise the retrain-once branch.
  force_fail: bool = False
  model_name: Optional[str] = None
  description: Optional[str] = None

  # `model_*` would otherwise hit Pydantic v2's protected namespace warning.
  model_config = ConfigDict(protected_namespaces=())


class TrainingJobResponse(BaseModel):
  job_id: UUID
  status: JobStatus
  created_at: datetime
  finished_at: Optional[datetime] = None
  request: TrainingRequest
  result: Optional[dict] = None      # training_service.run_training summary
  error: Optional[str] = None
