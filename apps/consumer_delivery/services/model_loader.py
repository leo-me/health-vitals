"""
model_loader — discover and load the current production model.

Three-tier cache to keep inference latency low and adapt to promotion:

  1. Redis (TTL ~30s) holds the *metadata* of the active model row
     (run_id, feature_version, artifact_path). A promote() in backend
     therefore propagates to all consumer_delivery workers within 30 s
     without any cross-service push.

  2. Process-local `_MODELS: {run_id → sklearn_estimator}` holds the
     actual estimator. Loading from MLflow is expensive (network + pickle),
     so we do it once per run_id per process. When run_id changes
     (promotion), the new run_id misses, we pull, the old entry is left
     to age out — usage is tiny so we don't bother LRU-evicting.

  3. The HTTP-level prediction cache lives elsewhere (services/inference.py).

Failures are surfaced as exceptions; the API layer turns them into HTTP 503.
"""

from __future__ import annotations

import json
import logging
import os
import pickle
import threading
from dataclasses import dataclass
from typing import Any, Optional

import mlflow
import mlflow.sklearn
from sqlalchemy.orm import Session

from core.cache import get_redis
from models.model_registry import ModelRegistry, ModelStage, ModelVersion


log = logging.getLogger(__name__)

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
MODEL_NAME          = os.getenv("MLFLOW_MODEL_NAME", "SensorsCarePipeline")
METADATA_CACHE_TTL  = int(os.getenv("MODEL_META_TTL_SECONDS", "30"))
METADATA_CACHE_KEY  = f"model:current:{MODEL_NAME}"


@dataclass
class ActiveModelMeta:
  registry_id:     str
  version_id:      Optional[str]
  run_id:          str
  artifact_path:   str
  feature_version: str
  feature_set:     list[str]
  model_name:      str
  algorithm:       Optional[str]
  metrics:         dict


# ── in-process estimator cache ──────────────────────────────────────────────

_MODELS: dict[str, Any] = {}
_LOAD_LOCK = threading.Lock()


# ── metadata: Postgres → Redis ──────────────────────────────────────────────

def _load_metadata_from_db(db: Session) -> Optional[ActiveModelMeta]:
  row: Optional[ModelRegistry] = (
    db.query(ModelRegistry)
      .filter(
        ModelRegistry.model_name == MODEL_NAME,
        ModelRegistry.stage      == ModelStage.PRODUCTION,
      )
      .order_by(ModelRegistry.created_at.desc())
      .first()
  )
  if row is None or row.run_id is None:
    return None

  # Resolve feature_version via the linked ModelVersion (training-time choice).
  feature_version = "v1"
  feature_set: list[str] = []
  if row.version_id is not None:
    ver: Optional[ModelVersion] = (
      db.query(ModelVersion).filter(ModelVersion.id == row.version_id).first()
    )
    if ver is not None:
      pp = ver.preprocessing_config or {}
      feature_version = pp.get("feature_version", "v1")
      feature_set     = list(ver.feature_set or [])

  return ActiveModelMeta(
    registry_id     = str(row.id),
    version_id      = str(row.version_id) if row.version_id else None,
    run_id          = row.run_id,
    artifact_path   = row.artifact_path or f"runs:/{row.run_id}/model",
    feature_version = feature_version,
    feature_set     = feature_set,
    model_name      = row.model_name,
    algorithm       = row.algorithm,
    metrics         = dict(row.metrics or {}),
  )


def get_active_meta(db: Session) -> Optional[ActiveModelMeta]:
  """Returns the current production model's metadata, with a Redis cache."""
  try:
    raw = get_redis().get(METADATA_CACHE_KEY)
  except Exception:                          # noqa: BLE001 — degrade gracefully
    raw = None
  if raw:
    return ActiveModelMeta(**json.loads(raw))

  meta = _load_metadata_from_db(db)
  if meta is None:
    return None

  try:
    get_redis().setex(
      METADATA_CACHE_KEY,
      METADATA_CACHE_TTL,
      json.dumps(meta.__dict__, default=str),
    )
  except Exception:                          # noqa: BLE001
    pass
  return meta


# ── estimator: MLflow → in-memory ───────────────────────────────────────────

def _load_estimator(meta: ActiveModelMeta) -> Any:
  """Pull the sklearn model bytes from MLflow once per (run_id, process)."""
  with _LOAD_LOCK:
    if meta.run_id in _MODELS:
      return _MODELS[meta.run_id]

    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    log.info("Loading model artifact from %s", meta.artifact_path)
    # The MLflow Python API auto-resolves "runs:/<id>/model"; fall back to
    # raw pickle if someone stored the artifact under a non-MLflow path.
    try:
      estimator = mlflow.sklearn.load_model(meta.artifact_path)
    except Exception:
      with open(meta.artifact_path, "rb") as f:
        estimator = pickle.load(f)

    _MODELS[meta.run_id] = estimator
    return estimator


def get_active_model(db: Session) -> Optional[tuple[Any, ActiveModelMeta]]:
  meta = get_active_meta(db)
  if meta is None:
    return None
  return _load_estimator(meta), meta


def invalidate_metadata_cache() -> None:
  """Force the next call to re-read from Postgres (useful for ops & tests)."""
  try:
    get_redis().delete(METADATA_CACHE_KEY)
  except Exception:                          # noqa: BLE001
    pass
