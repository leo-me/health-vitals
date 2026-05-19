"""
training_jobs — tiny in-memory registry for background training jobs.

This is intentionally minimal: a process-local dict, no persistence, no
locks beyond the GIL-safe dict ops we use. It is enough for a single-uvicorn
demo of "POST /train → poll GET /train/{job_id} → see succeeded". When the
load justifies it, swap this for Celery/RQ + Redis; the public surface
(create_job / get_job / mark_running / mark_succeeded / mark_failed) stays
the same.
"""

from __future__ import annotations

import threading
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from app.schemas.training import JobStatus, TrainingJobResponse, TrainingRequest


_JOBS: dict[UUID, TrainingJobResponse] = {}
_LOCK = threading.Lock()


def create_job(request: TrainingRequest) -> TrainingJobResponse:
  job = TrainingJobResponse(
    job_id     = uuid4(),
    status     = "pending",
    created_at = datetime.utcnow(),
    request    = request,
  )
  with _LOCK:
    _JOBS[job.job_id] = job
  return job


def get_job(job_id: UUID) -> Optional[TrainingJobResponse]:
  return _JOBS.get(job_id)


def list_jobs(limit: int = 50) -> list[TrainingJobResponse]:
  with _LOCK:
    items = list(_JOBS.values())
  items.sort(key=lambda j: j.created_at, reverse=True)
  return items[:limit]


def _update(job_id: UUID, *, status: JobStatus, **fields) -> None:
  with _LOCK:
    job = _JOBS.get(job_id)
    if job is None:
      return
    _JOBS[job_id] = job.model_copy(update={"status": status, **fields})


def mark_running(job_id: UUID) -> None:
  _update(job_id, status="running")


def mark_succeeded(job_id: UUID, result: dict) -> None:
  _update(job_id, status="succeeded", result=result, finished_at=datetime.utcnow())


def mark_failed(job_id: UUID, error: str) -> None:
  _update(job_id, status="failed", error=error, finished_at=datetime.utcnow())
