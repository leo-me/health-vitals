# Exp 2 — MLflow Model Registry Pipeline

Validates the full ML pipeline lifecycle: synthetic data generation → feature engineering → training → threshold-based registration → automatic retrain on failure. All runs are tracked in MLflow.

**Experiment matrix:** 3 dataset sizes × 3 thresholds × 2 feature versions × 2 scenarios = **36 pipeline runs** (up to 72 MLflow runs including retrains).

---

## Architecture

```
generate_data.py   →   run_pipeline.py   →   MLflow (localhost:5004)
                            ↓
                   accuracy >= threshold?
                     YES → register model (status=production)
                      NO → retrain once (random_state + 100)
```

| File | Purpose |
|------|---------|
| `generate_data.py` | Synthetic E4-style sensor data (EDA, BVP, ACC, IBI) |
| `run_pipeline.py` | Single pipeline run: train → log → register / retrain |
| `run_all.py` | Execute full 36-run matrix |
| `collect_results.py` | Export all MLflow runs to `results/pipeline_results.csv` |

---

## Parameters

| Parameter | Values |
|-----------|--------|
| Dataset sizes | small (1 000), medium (50 000), large (500 000) |
| Thresholds | 0.75, 0.80, 0.85 |
| Feature versions | v1 (raw EDA/BVP/ACC/IBI), v2 (v1 + rolling mean/std window=10) |
| Scenarios | standard (clean data), forced_fail (Gaussian noise injected) |
| Classifier | RandomForestClassifier, n_estimators=100 |
| Train/test split | 80 / 20 |

---

## Prerequisites

1. MLflow service running:
   ```bash
   cd infra && docker compose up -d mlflow
   ```
   UI available at **http://localhost:5004**

2. Install dependencies (from project root or activate existing venv):
   ```bash
   pip install -r experiments/exp2_mlflow_pipeline/requirements.txt
   ```

---

## Running the experiment

### Step 1 — Full matrix run

```bash
cd experiments/exp2_mlflow_pipeline
python run_all.py
```

Takes ~5–15 minutes depending on machine. Progress is printed per run:

```
[1/18] size=small thr=0.75 fv=v1  force_fail=False
  → acc=0.6123  REGISTERED  retrain=0  (0.3s)
```

### Step 2 — Export results to CSV

```bash
python collect_results.py
```

Writes `results/pipeline_results.csv` with one row per MLflow run.

### Step 3 — Inspect in MLflow UI

Open **http://localhost:5004** to browse all runs, compare metrics, and view registered model versions under **Models → SensorsCarePipeline**.

---

## Output

| File | Contents |
|------|----------|
| `results/pipeline_results.csv` | run_id, accuracy, threshold, dataset_size, feature_version, registered, retrain_count, duration_seconds, force_fail |
| MLflow UI | All runs with params, metrics, and registered model versions |

---

## Run a single pipeline manually

```bash
cd experiments/exp2_mlflow_pipeline
python - << 'EOF'
from generate_data import generate_dataset
from run_pipeline import run_pipeline

df = generate_dataset(50_000)
result = run_pipeline(df, threshold=0.80, dataset_size=50_000, feature_version="v2")
print(result)
EOF
```
