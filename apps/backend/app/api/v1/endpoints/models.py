from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.crud import crud_model_registry as crud
from app.db.session import get_db
from app.dependencies import get_current_user, require_admin
from app.models.model_version import ModelStage
from app.models.user import User
from app.schemas.model_registry import (
  ModelRegistryResponse,
  ModelRegistryStageUpdate,
)


router = APIRouter(prefix="/models", tags=["models"])


@router.get("/", response_model=list[ModelRegistryResponse])
def list_models(
  model_name: Optional[str] = Query(None, description="Filter by model_name"),
  stage: Optional[ModelStage] = Query(None, description="Filter by lifecycle stage"),
  limit: int = Query(100, ge=1, le=500),
  current_user: User = Depends(get_current_user),
  db: Session = Depends(get_db),
):
  return crud.list_model_registries(db, model_name=model_name, stage=stage, limit=limit)


@router.get("/current", response_model=ModelRegistryResponse)
def get_current_model(
  model_name: Optional[str] = Query(None, description="Filter by model_name"),
  current_user: User = Depends(get_current_user),
  db: Session = Depends(get_db),
):
  """
  Returns the most recently registered model row whose stage = production.
  This is the endpoint consumer_delivery polls (or caches in Redis) to know
  which artifact to load.
  """
  registry = crud.get_current_production(db, model_name=model_name)
  if not registry:
    raise HTTPException(status_code=404, detail="No production model registered")
  return registry


@router.get("/{registry_id}", response_model=ModelRegistryResponse)
def get_model(
  registry_id: UUID,
  current_user: User = Depends(get_current_user),
  db: Session = Depends(get_db),
):
  registry = crud.get_model_registry(db, registry_id)
  if not registry:
    raise HTTPException(status_code=404, detail="Model not found")
  return registry


@router.post("/{registry_id}/promote", response_model=ModelRegistryResponse)
def promote_model(
  registry_id: UUID,
  data: ModelRegistryStageUpdate,
  _: User = Depends(require_admin),
  db: Session = Depends(get_db),
):
  """
  Move a registry row between lifecycle stages (dev → staging → production →
  archived). Admin only. Note: this only flips the catalog row's stage; the
  artifact in MLflow is not moved — the model_registry row IS the application
  source of truth.
  """
  registry = crud.update_stage(db, registry_id, data.stage)
  if not registry:
    raise HTTPException(status_code=404, detail="Model not found")
  return registry
