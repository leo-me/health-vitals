# Exp 1 — Cache Layer Response Time

Measures the latency impact of Redis caching in `consumer_delivery` across three concurrency levels.

**Endpoint under test:** `GET /api/v1/data/smart_watch/{user_id}`

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

## Running the experiment

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

## Output

Each run produces three CSV files in `results/`:

| File | Contents |
|------|----------|
| `<name>_stats.csv` | p50 / p95 / p99 latency, RPS, failure count |
| `<name>_stats_history.csv` | Time-series RPS and latency |
| `<name>_failures.csv` | Per-failure detail |

---

