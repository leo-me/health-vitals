"""
MLflow pipeline: train → evaluate → register (pass) or retrain once (fail).

Pass : accuracy >= threshold  → register model, tag status=production
Fail : accuracy <  threshold  → log FAILED, retrain once with new random_state
"""

import time
from typing import Optional

import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

MLFLOW_URI     = "http://localhost:5004"
EXPERIMENT     = "sensors2care_registry"
MODEL_NAME     = "SensorsCarePipeline"
N_ESTIMATORS   = 100


# ---------------------------------------------------------------------------
# Feature engineering
# ---------------------------------------------------------------------------

def build_features_v1(df: pd.DataFrame) -> pd.DataFrame:
    return df[["eda", "bvp", "acc", "ibi"]].copy()


def build_features_v2(df: pd.DataFrame) -> pd.DataFrame:
    base = df[["eda", "bvp", "acc", "ibi"]].copy()
    for col in ["eda", "bvp", "acc", "ibi"]:
        base[f"{col}_rmean"] = base[col].rolling(10, min_periods=1).mean()
        base[f"{col}_rstd"]  = base[col].rolling(10, min_periods=1).std().fillna(0)
    return base


FEATURE_BUILDERS = {"v1": build_features_v1, "v2": build_features_v2}


# ---------------------------------------------------------------------------
# Core training run (one MLflow run)
# ---------------------------------------------------------------------------

def _train_and_log(
    X_train, X_test, y_train, y_test,
    *,
    threshold: float,
    dataset_size: int,
    feature_version: str,
    random_state: int,
    force_fail: bool,
    retrain_count: int,
) -> dict:
    t0 = time.time()
    model = RandomForestClassifier(n_estimators=N_ESTIMATORS, random_state=random_state)
    model.fit(X_train, y_train)
    accuracy       = accuracy_score(y_test, model.predict(X_test))
    duration       = time.time() - t0
    registered     = accuracy >= threshold
    reg_status     = "registered" if registered else "failed"

    with mlflow.start_run() as run:
        mlflow.log_params({
            "threshold":       threshold,
            "dataset_size":    dataset_size,
            "feature_version": feature_version,
            "random_state":    random_state,
            "force_fail":      force_fail,
        })
        mlflow.log_metrics({
            "accuracy":         accuracy,
            "retrain_count":    retrain_count,
            "duration_seconds": duration,
        })
        mlflow.log_param("registration_status", reg_status)

        if registered:
            mlflow.sklearn.log_model(model, "model", registered_model_name=MODEL_NAME)
            client   = mlflow.tracking.MlflowClient()
            versions = client.get_latest_versions(MODEL_NAME, stages=["None"])
            if versions:
                client.set_model_version_tag(
                    MODEL_NAME, versions[-1].version, "status", "production"
                )
        else:
            mlflow.set_tag("mlflow.runStatus", "FAILED")

        return {
            "run_id":           run.info.run_id,
            "accuracy":         accuracy,
            "threshold":        threshold,
            "dataset_size":     dataset_size,
            "feature_version":  feature_version,
            "registered":       registered,
            "retrain_count":    retrain_count,
            "duration_seconds": duration,
        }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run_pipeline(
    df: pd.DataFrame,
    *,
    threshold: float,
    dataset_size: int,
    feature_version: str,
    random_state: int = 42,
    force_fail: bool = False,
) -> dict:
    mlflow.set_tracking_uri(MLFLOW_URI)
    mlflow.set_experiment(EXPERIMENT)

    builder = FEATURE_BUILDERS[feature_version]
    X_all   = builder(df)

    if force_fail:
        rng   = np.random.default_rng(random_state)
        noise = rng.normal(0, 5, X_all.shape)
        X_all = X_all + noise

    y = df["label"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X_all, y, test_size=0.2, random_state=random_state
    )

    result = _train_and_log(
        X_train, X_test, y_train, y_test,
        threshold=threshold,
        dataset_size=dataset_size,
        feature_version=feature_version,
        random_state=random_state,
        force_fail=force_fail,
        retrain_count=0,
    )

    # One automatic retrain on failure
    if not result["registered"]:
        result = _train_and_log(
            X_train, X_test, y_train, y_test,
            threshold=threshold,
            dataset_size=dataset_size,
            feature_version=feature_version,
            random_state=random_state + 100,
            force_fail=force_fail,
            retrain_count=1,
        )

    return result
