"""
inference — build a feature vector from the latest sensor readings and
score it with the currently-active model.

The feature_version on the active ModelVersion row dictates which builder
(v1 = raw 4 features; v2 = raw + rolling stats over a 10-sample window).
For v2 we draw a small window of recent readings instead of just the last
one, so that the rolling-window features are not degenerate.
"""

from __future__ import annotations

import math
from datetime import datetime
from typing import Optional
from uuid import UUID

import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from core.cache import cache_get, cache_set
from models.sensor_recording import SensorRecording, SensorType
from services.model_loader import ActiveModelMeta, get_active_model


PREDICTION_CACHE_TTL = 5   # short: a user's most-recent reading changes fast
WINDOW_SIZE          = 10  # matches the rolling window used at training time


# ── feature builders (mirror backend.services.feature_service) ───────────────

def _v1(df: pd.DataFrame) -> pd.DataFrame:
  return df[["eda", "bvp", "acc", "ibi"]].copy()


def _v2(df: pd.DataFrame) -> pd.DataFrame:
  base = df[["eda", "bvp", "acc", "ibi"]].copy()
  for col in ["eda", "bvp", "acc", "ibi"]:
    base[f"{col}_rmean"] = base[col].rolling(WINDOW_SIZE, min_periods=1).mean()
    base[f"{col}_rstd"]  = base[col].rolling(WINDOW_SIZE, min_periods=1).std().fillna(0)
  return base


_BUILDERS = {"v1": _v1, "v2": _v2}


# ── DB pulls ─────────────────────────────────────────────────────────────────

def _recent(
  db: Session, user_id: UUID, sensor_type: SensorType, n: int
) -> list[SensorRecording]:
  return (
    db.query(SensorRecording)
      .filter(
        SensorRecording.user_id     == user_id,
        SensorRecording.sensor_type == sensor_type,
      )
      .order_by(SensorRecording.timestamp.desc())
      .limit(n)
      .all()
  )


def _frame(db: Session, user_id: UUID, n: int) -> Optional[pd.DataFrame]:
  """Build a (n × 4) frame of recent EDA/BVP/ACC/IBI in chronological order."""
  streams = {
    "eda": _recent(db, user_id, SensorType.EDA, n),
    "bvp": _recent(db, user_id, SensorType.BVP, n),
    "acc": _recent(db, user_id, SensorType.ACC, n),
    "ibi": _recent(db, user_id, SensorType.IBI, n),
  }
  if any(len(v) == 0 for v in streams.values()):
    return None

  # Per-stream extraction (ACC → magnitude), then trim to min length and
  # reverse to chronological order so rolling stats run forward in time.
  per_stream: dict[str, list[float]] = {}
  for sig in ("eda", "bvp", "ibi"):
    rows = streams[sig]
    key  = "ibi_s" if sig == "ibi" else "value"
    per_stream[sig] = [float((r.data or {}).get(key, 0)) for r in rows][::-1]

  acc_rows = streams["acc"]
  per_stream["acc"] = [
    math.sqrt(
      float((r.data or {}).get("x", 0)) ** 2
      + float((r.data or {}).get("y", 0)) ** 2
      + float((r.data or {}).get("z", 0)) ** 2
    )
    for r in acc_rows
  ][::-1]

  m = min(len(v) for v in per_stream.values())
  return pd.DataFrame({k: v[-m:] for k, v in per_stream.items()})


# ── public API ───────────────────────────────────────────────────────────────

def predict_stress(db: Session, user_id: UUID) -> Optional[dict]:
  cache_key = f"inference:{user_id}"
  cached = cache_get(cache_key)
  if cached is not None:
    return cached

  loaded = get_active_model(db)
  if loaded is None:
    return None
  model, meta = loaded

  n = WINDOW_SIZE if meta.feature_version == "v2" else 1
  frame = _frame(db, user_id, n)
  if frame is None or frame.empty:
    return None

  builder = _BUILDERS.get(meta.feature_version, _v1)
  X = builder(frame)
  # The model was trained on the same column layout, but a v2 model
  # promoted while we still see v1 expectations would mis-shape; guard.
  if hasattr(model, "n_features_in_") and X.shape[1] != model.n_features_in_:
    return None

  # Score the most-recent row only.
  row = X.iloc[[-1]]
  y_pred = int(model.predict(row)[0])
  proba: Optional[list[float]] = None
  if hasattr(model, "predict_proba"):
    proba = [float(p) for p in model.predict_proba(row)[0].tolist()]

  result = {
    "user_id":         str(user_id),
    "timestamp":       datetime.utcnow().isoformat(),
    "prediction":      y_pred,
    "label":           "stress" if y_pred == 1 else "non_stress",
    "probabilities":   proba,
    "model": {
      "registry_id":     meta.registry_id,
      "run_id":          meta.run_id,
      "model_name":      meta.model_name,
      "algorithm":       meta.algorithm,
      "feature_version": meta.feature_version,
      "metrics":         meta.metrics,
    },
  }
  cache_set(cache_key, result, ttl_seconds=PREDICTION_CACHE_TTL)
  return result
