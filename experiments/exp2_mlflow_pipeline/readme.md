# Exp 2 — MLflow Model Registry Pipeline

Validates the full ML pipeline lifecycle: synthetic data generation → feature engineering → training → threshold-based registration → automatic retrain on failure. **Driven entirely through the backend HTTP API**, so the experiment exercises the same dataflow as production (including the dual-write into `ModelVersion` + `ModelRegistry` in PostgreSQL).

**Experiment matrix:** 3 dataset sizes × 3 thresholds = **9 pipeline calls** (up to 18 MLflow runs including retrains).

> **Design note (2026-05-28).** Feature version (v1/v2) and forced-fail scenario were removed as parameters. On synthetic data with independent labels, v1/v2 accuracy differs by ~0.013 (noise), and Gaussian noise injection has zero effect (Δacc ≈ 0.002). The threshold level alone controls pass/fail. See `result.md §8` for the full rationale.

---

## Architecture

```
run_all.py ──HTTP──▶ backend /api/v1/train (admin-only, BackgroundTask)
                          │
                          ├─▶ feature_service.build_dataset(simulation)
                          ├─▶ training_service.run_training
                          ├─▶ MLflow runs / Model Registry (localhost:5004)
                          └─▶ PostgreSQL: ModelVersion + ModelRegistry rows
```

| File | Purpose |
|------|---------|
| `api_client.py` | Login + trigger + poll wrappers around `/api/v1/train` |
| `run_all.py` | Execute the 9-run matrix via the backend |
| `collect_results.py` | Export all MLflow runs to `results/pipeline_results.csv` |
| `plot_results.py` | Plot accuracy / duration / retrain rate from the CSV |

Synthetic data generation and sklearn training were previously in `generate_data.py` and `run_pipeline.py` in this folder. They now live in `apps/backend/app/services/feature_service.py` and `training_service.py` — the backend is the single source of truth.

---

## Parameters

| Parameter | Values |
|-----------|--------|
| Dataset sizes | small (1 K), medium (50 K), large (400 K) |
| Thresholds | 0.50, 0.55, 0.60 |
| Feature version | v1 (raw EDA/BVP/ACC/IBI) — fixed |
| Scenario | standard (clean data) — fixed |
| Classifier | RandomForestClassifier, n_estimators=100 |
| Train/test split | 80 / 20 |

> **Large = 400 K**, not 500 K. 500 K exhausts the Docker VM memory (7.666 GiB, ~5.3 GiB available after other services) and is killed by the OOM killer. 400 K is the empirical boundary on this machine. See `result.md §8.4`.

---

## Prerequisites

1. Bring up the stack — db, mlflow, and backend (which runs `alembic upgrade head` on boot and thereby seeds the exp2 admin user):
   ```bash
   cd infra
   docker compose up -d db mlflow backend
   ```
   - MLflow UI: **http://localhost:5004**
   - Backend API: **http://localhost:8000** (Swagger at `/docs`)

2. Confirm the admin seed landed:
   ```bash
   docker compose exec db psql -U postgres -d health_db \
     -c "SELECT email, user_type FROM users WHERE user_type='ADMIN';"
   ```
   You should see `exp2-admin@hv.local | ADMIN`. The default password is `exp2-admin-changeme` (override with `EXP2_ADMIN_PASSWORD` env var on both backend and client).

3. Install client dependencies:
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

`run_all.py` logs in once, then for each of the 9 combinations:
1. `POST /api/v1/train/` → returns 202 + `job_id`
2. polls `GET /api/v1/train/{job_id}` until the BackgroundTask reports `succeeded` / `failed`

Progress is printed per run:

```
[1/9] size=small thr=0.50 fv=v1
  → acc=0.5800  REGISTERED  retrain=0  (0.3s)
```

> **Note on large runs.** Each 400 K pipeline call takes ~5 min to train and significantly longer for MLflow artifact upload. The poll timeout in `api_client.py` is set to 1 800 s; run large cells individually if needed.

### Step 2 — Export results to CSV

```bash
python collect_results.py
```

Writes `results/pipeline_results.csv` with one row per MLflow run.

### Step 3 — Inspect in MLflow UI and PostgreSQL

- **http://localhost:5004** → browse runs, compare metrics, view registered model versions under **Models → SensorsCarePipeline**.
- For the PG side of the dual-write:
  ```bash
  docker compose exec db psql -U postgres -d health_db -c \
    "SELECT count(*) FROM model_registry; SELECT count(*) FROM model_version;"
  ```

---

## Output

| File | Contents |
|------|----------|
| `results/pipeline_results.csv` | run_id, accuracy, threshold, dataset_size, feature_version, registered, retrain_count, duration_seconds, force_fail |
| MLflow UI | All runs with params, metrics, and registered model versions |
| PostgreSQL | `model_version` + `model_registry` rows (one per registered run) |

---

## Configuration

Environment variables read by `api_client.py` (all optional, defaults match the backend Settings):

| Var | Default | Notes |
|-----|---------|-------|
| `BACKEND_URL` | `http://localhost:8000` | Where the backend listens |
| `EXP2_ADMIN_EMAIL` | `exp2-admin@hv.local` | Must match the value seeded by alembic |
| `EXP2_ADMIN_PASSWORD` | `exp2-admin-changeme` | Override in shared environments |

---

## Trigger one run manually (sanity check)

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -d "username=exp2-admin@hv.local&password=exp2-admin-changeme" | jq -r .access_token)

curl -s -X POST http://localhost:8000/api/v1/train/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"dataset_size":1000,"threshold":0.6,"feature_version":"v1","force_fail":false}'
```
