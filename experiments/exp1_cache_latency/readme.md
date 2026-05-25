# Exp 1 — Cache Layer Response Time

Measures the latency impact of Redis caching in `consumer_delivery` across three concurrency levels.

This experiment has **two phases** that together form a control comparison:

| Phase | Endpoint | Underlying query | Hypothesis |
|---|---|---|---|
| **Phase 1** (original) | `GET /api/v1/data/smart_watch/{user_id}` | One `LIMIT 1` per sensor type, indexed | Cache overhead may dominate → no win |
| **Phase 2** (new) | `GET /api/v1/overview/{user_id}?days=7` | Hourly `GROUP BY` aggregation, scans hundreds of K rows | Query cost exceeds Redis overhead → cache should win |

Same concurrency levels (u=1/10/50), same duration (60 s), same user pool, same cache TTL window — the **only** independent variable is endpoint cost.

---

## Prerequisites

1. Docker services running:
   ```bash
   cd infra && docker compose up -d
   ```

2. Local PostgreSQL (port 5432) seeded with users, devices, and sensor data:
   ```bash
   # From project root
   DATABASE_URL=postgresql://postgres:0000@localhost:5432/health_db \
       python data/pipelines/seed_fixtures.py

   DATABASE_URL=postgresql://postgres:0000@localhost:5432/health_db \
       python data/pipelines/load_subjects.py
   ```

3. Locust installed:
   ```bash
   pip install -r experiments/exp1_cache_latency/requirements.txt
   ```

---

## Phase 1 — cheap query (smart_watch)

The matrix is **6 runs**: 3 concurrency levels × 2 cache states (OFF / ON).
`CACHE_ENABLED` is a `consumer_delivery` environment variable — restart the container to toggle it.

### Step 1 — Cache OFF

```bash
cd infra && CACHE_ENABLED=false docker compose up -d consumer_delivery
```

```bash
cd experiments/exp1_cache_latency

locust -f locustfile.py --headless -u 1  -r 1  --run-time 60s --csv results/u1_no_cache
locust -f locustfile.py --headless -u 10 -r 2  --run-time 60s --csv results/u10_no_cache
locust -f locustfile.py --headless -u 50 -r 5  --run-time 60s --csv results/u50_no_cache
```

### Step 2 — Cache ON

```bash
cd infra && CACHE_ENABLED=true docker compose up -d consumer_delivery
```

```bash
cd experiments/exp1_cache_latency

locust -f locustfile.py --headless -u 1  -r 1  --run-time 60s --csv results/u1_cache
locust -f locustfile.py --headless -u 10 -r 2  --run-time 60s --csv results/u10_cache
locust -f locustfile.py --headless -u 50 -r 5  --run-time 60s --csv results/u50_cache
```

---

## Phase 2 — expensive query (overview)

Same matrix shape — 6 runs (3 concurrency × 2 cache states) — driven by a separate locustfile (`locustfile_overview.py`) that hits `/api/v1/overview/{user_id}?days=7`.

The overview endpoint performs an hourly `GROUP BY` aggregation across all of a user's recent sensor readings (anchored at the user's own `MAX(timestamp)`, to keep the experiment reproducible regardless of wall-clock date and to side-step the IBI timestamp bug). Smoke tests on this hardware show **~430 ms** for a cache miss vs **~3 ms** for a cache hit — roughly a **120× single-call speedup** before contention.

### Step 1 — Cache OFF

```bash
cd infra && CACHE_ENABLED=false docker compose up -d consumer_delivery
```

```bash
cd experiments/exp1_cache_latency

locust -f locustfile_overview.py --headless -u 1  -r 1  --run-time 60s \
    --csv results/overview_u1_no_cache
locust -f locustfile_overview.py --headless -u 10 -r 2  --run-time 60s \
    --csv results/overview_u10_no_cache
locust -f locustfile_overview.py --headless -u 50 -r 5  --run-time 60s \
    --csv results/overview_u50_no_cache
```

### Step 2 — Cache ON

```bash
cd infra && CACHE_ENABLED=true docker compose up -d consumer_delivery
```

```bash
cd experiments/exp1_cache_latency

locust -f locustfile_overview.py --headless -u 1  -r 1  --run-time 60s \
    --csv results/overview_u1_cache
locust -f locustfile_overview.py --headless -u 10 -r 2  --run-time 60s \
    --csv results/overview_u10_cache
locust -f locustfile_overview.py --headless -u 50 -r 5  --run-time 60s \
    --csv results/overview_u50_cache
```

Optional knob — shrink/grow the window to vary query cost:

```bash
OVERVIEW_DAYS=1  locust -f locustfile_overview.py ...   # lighter query
OVERVIEW_DAYS=30 locust -f locustfile_overview.py ...   # heavier query
```

---

## Output

Each run produces three CSV files in `results/`:

| File | Contents |
|------|----------|
| `<name>_stats.csv` | p50 / p95 / p99 latency, RPS, failure count |
| `<name>_stats_history.csv` | Time-series RPS and latency |
| `<name>_failures.csv` | Per-failure detail |

Phase 1 results live under names like `u1_cache_stats.csv`; phase 2 results under `overview_u1_cache_stats.csv`, etc.

---

