"""
collect_results.py — query MLflow for all runs in sensors2care_registry,
export to results/pipeline_results.csv.
"""

import os
import pandas as pd
import mlflow
from mlflow.tracking import MlflowClient

MLFLOW_URI  = "http://localhost:5004"
EXPERIMENT  = "sensors2care_registry"
OUT_PATH    = os.path.join(os.path.dirname(__file__), "results", "pipeline_results.csv")


def collect():
    mlflow.set_tracking_uri(MLFLOW_URI)
    client = MlflowClient()

    exp = client.get_experiment_by_name(EXPERIMENT)
    if exp is None:
        print(f"Experiment '{EXPERIMENT}' not found.")
        return

    runs = client.search_runs(
        experiment_ids=[exp.experiment_id],
        order_by=["start_time ASC"],
    )

    rows = []
    for r in runs:
        p = r.data.params
        m = r.data.metrics
        rows.append({
            "run_id":           r.info.run_id,
            "accuracy":         m.get("accuracy"),
            "threshold":        float(p.get("threshold", 0)),
            "dataset_size":     int(p.get("dataset_size", 0)),
            "feature_version":  p.get("feature_version"),
            "registered":       p.get("registration_status") == "registered",
            "retrain_count":    int(m.get("retrain_count", 0)),
            "duration_seconds": m.get("duration_seconds"),
            "force_fail":       p.get("force_fail") == "True",
        })

    df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    df.to_csv(OUT_PATH, index=False)
    print(f"Exported {len(df)} runs → {OUT_PATH}")
    print(df.to_string(index=False))


if __name__ == "__main__":
    collect()
