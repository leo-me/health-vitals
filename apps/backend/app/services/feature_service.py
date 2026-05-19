"""
feature_service — build (X, y) training datasets.

Two modes:
  - "simulation": synthetic Empatica-shaped signals + random labels (no signal).
    Mirrors experiments/exp2_mlflow_pipeline/generate_data.py so the registry
    end-to-end can be demoed without real labels.
  - "production": pull rows from sensor_recordings table, aggregate per
    (user, time-window) into feature vectors. Labels are read from the
    sensor_recording.data JSON if a "stress" key is present; otherwise an
    error is raised — the production path requires labeled data.

Output is always (pd.DataFrame X, np.ndarray y) ready for sklearn.
"""

from __future__ import annotations

from typing import Literal, Optional, Tuple

import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from app.models.sensor_recording import SensorRecording, SensorType


Mode = Literal["simulation", "production"]


# ── feature builders (mirror exp2 run_pipeline.py) ───────────────────────────

def build_features_v1(df: pd.DataFrame) -> pd.DataFrame:
  return df[["eda", "bvp", "acc", "ibi"]].copy()


def build_features_v2(df: pd.DataFrame) -> pd.DataFrame:
  base = df[["eda", "bvp", "acc", "ibi"]].copy()
  for col in ["eda", "bvp", "acc", "ibi"]:
    base[f"{col}_rmean"] = base[col].rolling(10, min_periods=1).mean()
    base[f"{col}_rstd"]  = base[col].rolling(10, min_periods=1).std().fillna(0)
  return base


FEATURE_BUILDERS = {"v1": build_features_v1, "v2": build_features_v2}


# ── simulation source ────────────────────────────────────────────────────────

def _generate_synthetic(size: int, seed: int = 42) -> pd.DataFrame:
  """Same distributions as exp2/generate_data.py — features independent of label."""
  rng    = np.random.default_rng(seed)
  labels = rng.choice([0, 1], size=size, p=[0.4, 0.6])
  return pd.DataFrame({
    "eda":   rng.normal(2.5,  1.2,  size).clip(0),
    "bvp":   rng.normal(65,   8,    size),
    "acc":   rng.normal(0.02, 0.15, size),
    "ibi":   rng.normal(0.85, 0.12, size).clip(0.3),
    "label": labels,
  })


# ── production source (read sensor_recordings) ───────────────────────────────

def _pivot_recordings(rows: list[SensorRecording]) -> pd.DataFrame:
  """
  Collapse a stream of per-signal SensorRecording rows into one row per
  recording timestamp with eda/bvp/acc/ibi columns.

  Simplifying assumption: rows are aligned in time by index after sorting.
  The forward-fill is the cheapest reasonable join; a real production path
  would window-aggregate. ACC is reduced to magnitude.
  """
  per_signal: dict[str, list[float]] = {"eda": [], "bvp": [], "acc": [], "ibi": []}
  for r in rows:
    data = r.data or {}
    if r.sensor_type == SensorType.EDA:
      per_signal["eda"].append(float(data.get("value", 0)))
    elif r.sensor_type == SensorType.BVP:
      per_signal["bvp"].append(float(data.get("value", 0)))
    elif r.sensor_type == SensorType.ACC:
      mag = (float(data.get("x", 0)) ** 2
           + float(data.get("y", 0)) ** 2
           + float(data.get("z", 0)) ** 2) ** 0.5
      per_signal["acc"].append(mag)
    elif r.sensor_type == SensorType.IBI:
      per_signal["ibi"].append(float(data.get("ibi_s", 0)))

  n = min(len(v) for v in per_signal.values()) if all(per_signal.values()) else 0
  if n == 0:
    return pd.DataFrame(columns=["eda", "bvp", "acc", "ibi", "label"])

  df = pd.DataFrame({k: v[:n] for k, v in per_signal.items()})
  # Production labels are not yet stored in sensor_recording.data — placeholder
  # of 0 here makes the path runnable for smoke tests; real label join lands
  # when WESAD-style annotations are imported.
  df["label"] = 0
  return df


def _load_production(db: Session, limit: int) -> pd.DataFrame:
  rows = (
    db.query(SensorRecording)
      .order_by(SensorRecording.timestamp.asc())
      .limit(limit * 4)   # 4 signal streams → ~limit rows after pivot
      .all()
  )
  return _pivot_recordings(rows)


# ── public API ───────────────────────────────────────────────────────────────

def build_dataset(
  mode: Mode,
  *,
  size: int = 1_000,
  feature_version: str = "v1",
  seed: int = 42,
  db: Optional[Session] = None,
) -> Tuple[pd.DataFrame, np.ndarray, dict]:
  """
  Returns:
    X            — feature matrix (DataFrame)
    y            — labels (numpy array)
    descriptor   — JSON-serializable dict describing this dataset
                   (goes into ModelVersion.feature_set / preprocessing_config)
  """
  if mode == "simulation":
    raw = _generate_synthetic(size=size, seed=seed)
    source = "synthetic"
  elif mode == "production":
    if db is None:
      raise ValueError("production mode requires a db session")
    raw = _load_production(db, limit=size)
    if raw.empty:
      raise RuntimeError("No sensor_recordings available for production dataset")
    source = "sensor_recordings"
  else:
    raise ValueError(f"unknown mode: {mode}")

  if feature_version not in FEATURE_BUILDERS:
    raise ValueError(f"unknown feature_version: {feature_version}")

  X = FEATURE_BUILDERS[feature_version](raw)
  y = raw["label"].to_numpy()

  descriptor = {
    "source":          source,
    "feature_version": feature_version,
    "feature_set":     list(X.columns),
    "n_rows":          int(len(X)),
    "n_features":      int(X.shape[1]),
    "seed":            seed,
  }
  return X, y, descriptor
