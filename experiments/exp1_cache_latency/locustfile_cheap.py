"""
Locust load test — Exp 1: Cache Layer Response Time (cheap baseline)
Target: consumer_delivery  (port 8001)

Endpoint under test:
    GET /api/v1/cheap/{user_id}

The minimum-work endpoint: a single `LIMIT 1` lookup of latest heart_rate
for a user, no adapter transform, no Pydantic schema. Use as the true cheap
baseline against /overview (hourly aggregate).
"""

import json
import os
import random
from pathlib import Path

from locust import HttpUser, between, events, task

BASE_URL      = os.environ.get("BASE_URL", "http://localhost:8001")
HERE          = Path(__file__).resolve().parent
PROJECT_ROOT  = HERE.parent.parent
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
    def get_cheap(self):
        user_id = random.choice(_user_ids)
        with self.client.get(
            f"/api/v1/cheap/{user_id}",
            name="/api/v1/cheap/[user_id]",
            catch_response=True,
        ) as response:
            if response.status_code == 404:
                print(f"[404] invalid user_id: {user_id}")
                response.failure(f"No data for user {user_id}")
            else:
                response.success()
