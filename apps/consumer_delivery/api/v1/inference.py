from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.session import get_db
from services.inference import predict_stress
from services.model_loader import get_active_meta, invalidate_metadata_cache


router = APIRouter()


@router.get("/{user_id}")
def infer(user_id: UUID, db: Session = Depends(get_db)):
  result = predict_stress(db, user_id)
  if result is None:
    raise HTTPException(
      status_code=503,
      detail="No active model or insufficient sensor data for inference",
    )
  return result


@router.get("/")
def active_model(db: Session = Depends(get_db)):
  """Expose the active model meta so consumers can sanity-check what they hit."""
  meta = get_active_meta(db)
  if meta is None:
    raise HTTPException(status_code=503, detail="No active model registered")
  return meta.__dict__


@router.delete("/cache")
def drop_meta_cache():
  """Force the next request to re-read the current model from Postgres."""
  invalidate_metadata_cache()
  return {"status": "ok"}
