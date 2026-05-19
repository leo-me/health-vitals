"""
/train endpoints — kick off a training cycle and poll its result.

Training is non-trivially CPU-bound (sklearn fit), so we run it in a
BackgroundTask rather than inline in the HTTP request. The job's status
and final summary are kept in-memory by training_jobs.

Auth: admin-only — training writes new rows into model_version /
model_registry and consumes MLflow run slots.
"""

from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal, get_db
from app.dependencies import require_admin
from app.models.user import User
from app.schemas.training import TrainingJobResponse, TrainingRequest
from app.services import training_jobs
from app.services.training_service import run_training


router = APIRouter(prefix="/train", tags=["training"])


# ── worker -------------------------------------------------------------------

def _execute(job_id: UUID, request: TrainingRequest) -> None:
  """
  Runs in a BackgroundTask thread. The HTTP-request DB session has already
  been closed by FastAPI by the time this runs, so we open our own.
  """
  training_jobs.mark_running(job_id)
  db: Session = SessionLocal()
  try:
    summary = run_training(
      db,
      mode            = request.mode,
      threshold       = request.threshold,
      dataset_size    = request.dataset_size,
      feature_version = request.feature_version,
      random_state    = request.random_state,
      model_name      = request.model_name,
      description     = request.description,
    )
    training_jobs.mark_succeeded(job_id, summary)
  except Exception as exc:                            # noqa: BLE001 — surface to API
    training_jobs.mark_failed(job_id, f"{type(exc).__name__}: {exc}")
  finally:
    db.close()


# ── endpoints ----------------------------------------------------------------

@router.post("/", response_model=TrainingJobResponse, status_code=202)
def trigger_training(
  request: TrainingRequest,
  background: BackgroundTasks,
  _: User = Depends(require_admin),
  db: Session = Depends(get_db),  # touch the dep so failures surface early
):
  """
  Kick off a training cycle. Returns 202 + a job_id immediately;
  poll GET /train/{job_id} for the summary.
  """
  job = training_jobs.create_job(request)
  background.add_task(_execute, job.job_id, request)
  return job


@router.get("/", response_model=list[TrainingJobResponse])
def list_training_jobs(
  limit: int = 50,
  _: User = Depends(require_admin),
):
  return training_jobs.list_jobs(limit=limit)


@router.get("/{job_id}", response_model=TrainingJobResponse)
def get_training_job(
  job_id: UUID,
  _: User = Depends(require_admin),
):
  job = training_jobs.get_job(job_id)
  if job is None:
    raise HTTPException(status_code=404, detail="Training job not found")
  return job
