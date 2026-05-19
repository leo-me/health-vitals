"""
training_service — orchestrate one train → evaluate → register cycle.

Ported from experiments/exp2_mlflow_pipeline/run_pipeline.py with two changes:
  1. The feature/data layer is delegated to feature_service.build_dataset(),
     which supports both simulation and production sources.
  2. On a successful registration the service writes ONE ModelVersion row +
     ONE ModelRegistry row into PostgreSQL, with mlflow run_id stored in the
     registry row so the catalog can be joined back to the MLflow artifact.

The retrain-once-on-fail behavior matches exp2: if accuracy < threshold the
service starts a second MLflow run with random_state + 100; whichever attempt
crosses the threshold becomes the registered row.
"""

from __future__ import annotations

import time
from typing import Optional
from uuid import UUID

import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sqlalchemy.orm import Session

from app.core.config import settings
from app.crud import crud_model_registry, crud_model_version
from app.models.model_version import ModelStage
from app.schemas.model_registry import ModelRegistryCreate
from app.schemas.model_version import ModelVersionCreate
from app.services.feature_service import Mode, build_dataset


N_ESTIMATORS = 100


# ── single MLflow run ────────────────────────────────────────────────────────

def _train_and_log(
  X_train, X_test, y_train, y_test,
  *,
  threshold: float,
  dataset_size: int,
  feature_version: str,
  random_state: int,
  retrain_count: int,
) -> dict:
  t0       = time.time()
  model    = RandomForestClassifier(n_estimators=N_ESTIMATORS, random_state=random_state)
  model.fit(X_train, y_train)
  y_pred   = model.predict(X_test)

  accuracy = float(accuracy_score(y_test, y_pred))
  # zero_division=0 avoids warnings when a class is absent from y_test
  precision = float(precision_score(y_test, y_pred, average="binary", zero_division=0))
  recall    = float(recall_score(y_test, y_pred, average="binary", zero_division=0))
  duration  = time.time() - t0

  registered = accuracy >= threshold
  reg_status = "registered" if registered else "failed"

  with mlflow.start_run() as run:
    mlflow.log_params({
      "threshold":       threshold,
      "dataset_size":    dataset_size,
      "feature_version": feature_version,
      "random_state":    random_state,
    })
    mlflow.log_metrics({
      "accuracy":         accuracy,
      "precision":        precision,
      "recall":           recall,
      "retrain_count":    retrain_count,
      "duration_seconds": duration,
    })
    mlflow.log_param("registration_status", reg_status)

    artifact_path = None
    if registered:
      mlflow.sklearn.log_model(
        model, "model",
        registered_model_name=settings.MLFLOW_MODEL_NAME,
      )
      artifact_path = f"runs:/{run.info.run_id}/model"
    else:
      mlflow.set_tag("mlflow.runStatus", "FAILED")

    return {
      "run_id":           run.info.run_id,
      "accuracy":         accuracy,
      "precision":        precision,
      "recall":           recall,
      "registered":       registered,
      "retrain_count":    retrain_count,
      "duration_seconds": duration,
      "artifact_path":    artifact_path,
      "random_state":     random_state,
    }


# ── public API ───────────────────────────────────────────────────────────────

def run_training(
  db: Session,
  *,
  mode: Mode = "simulation",
  threshold: float = 0.50,
  dataset_size: int = 1_000,
  feature_version: str = "v1",
  random_state: int = 42,
  model_name: Optional[str] = None,
  description: Optional[str] = None,
) -> dict:
  """
  Run one training cycle, optionally retraining once on failure, and on
  success commit ModelVersion + ModelRegistry rows to PostgreSQL.

  Returns a summary dict suitable for an API response.
  """
  mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
  mlflow.set_experiment(settings.MLFLOW_EXPERIMENT)

  X, y, descriptor = build_dataset(
    mode,
    size=dataset_size,
    feature_version=feature_version,
    seed=random_state,
    db=db,
  )

  X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=random_state
  )

  result = _train_and_log(
    X_train, X_test, y_train, y_test,
    threshold=threshold,
    dataset_size=descriptor["n_rows"],
    feature_version=feature_version,
    random_state=random_state,
    retrain_count=0,
  )

  # Single automatic retrain on failure — same as exp2.
  if not result["registered"]:
    result = _train_and_log(
      X_train, X_test, y_train, y_test,
      threshold=threshold,
      dataset_size=descriptor["n_rows"],
      feature_version=feature_version,
      random_state=random_state + 100,
      retrain_count=1,
    )

  summary = {
    "mode":            mode,
    "threshold":       threshold,
    "feature_version": feature_version,
    "descriptor":      descriptor,
    "registered":      result["registered"],
    "run_id":          result["run_id"],
    "accuracy":        result["accuracy"],
    "precision":       result["precision"],
    "recall":          result["recall"],
    "retrain_count":   result["retrain_count"],
    "duration_seconds": result["duration_seconds"],
    "model_version_id":  None,
    "model_registry_id": None,
  }

  # Step 3: dual-write to PostgreSQL only when the gate has passed.
  if result["registered"]:
    version_id, registry_id = _persist_to_catalog(
      db,
      result=result,
      descriptor=descriptor,
      threshold=threshold,
      model_name=model_name or settings.MLFLOW_MODEL_NAME,
      description=description,
    )
    summary["model_version_id"]  = str(version_id)
    summary["model_registry_id"] = str(registry_id)

  return summary


# ── PostgreSQL catalog write (step 3) ────────────────────────────────────────

def _persist_to_catalog(
  db: Session,
  *,
  result: dict,
  descriptor: dict,
  threshold: float,
  model_name: str,
  description: Optional[str],
) -> tuple[UUID, UUID]:
  """
  Write the dataset snapshot (ModelVersion) and the model entry (ModelRegistry)
  in one transaction. ModelRegistry.run_id links back to the MLflow run; the
  artifact lives in MLflow's mlruns/ — we only catalog where to find it.
  """
  version_in = ModelVersionCreate(
    version_tag         = f"{descriptor['feature_version']}-{result['run_id'][:8]}",
    stage               = ModelStage.PRODUCTION,
    description         = description,
    feature_set         = descriptor["feature_set"],
    preprocessing_config = {
      "source":          descriptor["source"],
      "feature_version": descriptor["feature_version"],
      "seed":            descriptor["seed"],
    },
    record_count        = descriptor["n_rows"],
    train_ratio         = 0.8,
    val_ratio           = 0.0,
    test_ratio          = 0.2,
  )
  version = crud_model_version.create_model_version(db, version_in)

  registry_in = ModelRegistryCreate(
    model_name    = model_name,
    version_id    = version.id,
    description   = description,
    algorithm     = "RandomForestClassifier",
    stage         = ModelStage.PRODUCTION,
    hyperparameter= {
      "n_estimators": N_ESTIMATORS,
      "random_state": result["random_state"],
      "threshold":    threshold,
    },
    run_id        = result["run_id"],
    metrics       = {
      "accuracy":  result["accuracy"],
      "precision": result["precision"],
      "recall":    result["recall"],
    },
    artifact_path = result["artifact_path"],
  )
  registry = crud_model_registry.create_model_registry(db, registry_in)

  return version.id, registry.id
