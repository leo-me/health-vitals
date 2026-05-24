"""
Locust load test — Exp 1 Phase 2: Cache benefit on an expensive query.

Target: consumer_delivery  (port 8001)

Endpoint under test:
    GET /api/v1/data/overview/{user_id}?days=7

This is the **control arm** of the phase-2 experiment. Phase 1 used the
smart_watch endpoint (a cheap LIMIT-1 query) and found cache hurt latency;
this run uses an expensive hourly-bucket aggregation over the past N days of
a user's sensor_recordings, which scans hundreds of thousands of rows per
call. The hypothesis is that for queries above the Redis-overhead breakeven
point (~30 ms in this environment), cache flips from a tax to a win.

Test matrix — 6 runs (3 concurrency levels × 2 cache states).
CACHE_ENABLED is a consumer_delivery env var; restart the service to toggle.

Step 1 — Cache OFF:
    cd infra && CACHE_ENABLED=false docker compose up -d consumer_delivery

    locust -f locustfile_overview.py --headless -u 1  -r 1  --run-time 60s \\
        --csv results/overview_u1_no_cache
    locust -f locustfile_overview.py --headless -u 10 -r 2  --run-time 60s \\
        --csv results/overview_u10_no_cache
    locust -f locustfile_overview.py --headless -u 50 -r 5  --run-time 60s \\
        --csv results/overview_u50_no_cache

Step 2 — Cache ON:
    cd infra && CACHE_ENABLED=true docker compose up -d consumer_delivery

    locust -f locustfile_overview.py --headless -u 1  -r 1  --run-time 60s \\
        --csv results/overview_u1_cache
    locust -f locustfile_overview.py --headless -u 10 -r 2  --run-time 60s \\
        --csv results/overview_u10_cache
    locust -f locustfile_overview.py --headless -u 50 -r 5  --run-time 60s \\
        --csv results/overview_u50_cache

Optional knobs (env vars):
    OVERVIEW_DAYS    default 7   — window size; smaller = lighter query
    BASE_URL         default http://localhost:8001
"""

import json
import os
import random
from pathlib import Path

from locust import HttpUser, between, events, task

BASE_URL       = os.environ.get("BASE_URL", "http://localhost:8001")
OVERVIEW_DAYS  = int(os.environ.get("OVERVIEW_DAYS", "7"))
HERE           = Path(__file__).resolve().parent
PROJECT_ROOT   = HERE.parent.parent
MANIFEST_PATH  = PROJECT_ROOT / "data" / "pipelines" / "user_ids.json"

_user_ids: list[str] = []


@events.init.add_listener
def on_locust_init(environment, **kwargs):
    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(
            f"user_ids.json not found at {MANIFEST_PATH}. "
            "Run data/pipelines/seed_fixtures.py first."
        )
    with open(MANIFEST_PATH) as f:
        _user_ids.extend(json.load(f)["user_ids"])
    print(f"[locust] Loaded {len(_user_ids)} user IDs from manifest")
    print(f"[locust] OVERVIEW_DAYS={OVERVIEW_DAYS}")


class OverviewUser(HttpUser):
    host      = BASE_URL
    wait_time = between(0.05, 0.2)

    @task
    def get_overview(self):
        user_id = random.choice(_user_ids)
        with self.client.get(
            f"/api/v1/overview/{user_id}?days={OVERVIEW_DAYS}",
            name="/api/v1/overview/[user_id]",
            catch_response=True,
        ) as response:
            if response.status_code == 404:
                # 404 means the DB lacks data for this user — treat as failure
                # so the experiment doesn't silently degrade if the wrong DB is
                # wired up (lesson learnt 2026-05-21).
                response.failure(f"404 for user {user_id} — check DB seeding")
            elif response.status_code >= 500:
                response.failure(f"server error {response.status_code}")
            else:
                response.success()
