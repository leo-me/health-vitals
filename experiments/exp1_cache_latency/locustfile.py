"""
Locust load test — Exp 1: Cache Layer Response Time
Target: consumer_delivery  (port 8001)

Endpoint under test:
    GET /api/v1/data/smart_watch/{user_id}
    (no JWT — consumer_delivery has no auth layer)

Test matrix — 6 runs (3 concurrency levels × 2 cache states).
CACHE_ENABLED is a consumer_delivery env var; restart the service to toggle it.

Step 1 — Cache OFF (restart consumer_delivery with CACHE_ENABLED=false first):
    cd infra && CACHE_ENABLED=false docker compose up -d consumer_delivery

    locust -f locustfile.py --headless -u 1  -r 1  --run-time 60s --csv results/u1_no_cache
    locust -f locustfile.py --headless -u 10 -r 2  --run-time 60s --csv results/u10_no_cache
    locust -f locustfile.py --headless -u 50 -r 5  --run-time 60s --csv results/u50_no_cache

Step 2 — Cache ON (restart consumer_delivery with CACHE_ENABLED=true):
    cd infra && CACHE_ENABLED=true docker compose up -d consumer_delivery

    locust -f locustfile.py --headless -u 1  -r 1  --run-time 60s --csv results/u1_cache
    locust -f locustfile.py --headless -u 10 -r 2  --run-time 60s --csv results/u10_cache
    locust -f locustfile.py --headless -u 50 -r 5  --run-time 60s --csv results/u50_cache
"""

import json
import os
import random
from pathlib import Path

from locust import HttpUser, between, events, task

BASE_URL     = os.environ.get("BASE_URL", "http://localhost:8001")
HERE         = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent.parent
MANIFEST_PATH = PROJECT_ROOT / "data" / "pipelines" / "user_ids.json"

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


class ConsumerUser(HttpUser):
    host      = BASE_URL
    wait_time = between(0.05, 0.2)

    @task
    def get_smart_watch_data(self):
        user_id = random.choice(_user_ids)
        with self.client.get(
            f"/api/v1/data/smart_watch/{user_id}",
            name="/api/v1/data/smart_watch/[user_id]",
            catch_response=True
        ) as response:
            if response.status_code == 404:
                print(f"[404] invalid user_id: {user_id}")
                response.failure(f"No data for user {user_id}")
            else:
                response.success()