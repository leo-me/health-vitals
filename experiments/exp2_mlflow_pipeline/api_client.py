"""
api_client.py — drive the backend /train endpoints for the exp2 matrix.

Replaces the in-process run_pipeline() with HTTP calls so exp2 exercises the
same dataflow as production:

    run_all.py ──HTTP──▶ backend /train (BackgroundTask)
                              ├─▶ feature_service.build_dataset(simulation)
                              ├─▶ training_service.run_training (+force_fail)
                              ├─▶ MLflow runs / Model Registry
                              └─▶ PostgreSQL: ModelVersion + ModelRegistry

Auth: the backend /train route is admin-only. The fixed user we use lives in
alembic migration 150a555cf5a9_seed_exp2_admin_user. Credentials are read
from env (EXP2_ADMIN_EMAIL / EXP2_ADMIN_PASSWORD) with the same defaults the
backend ships with, so a clean local dev env "just works" with no setup.
"""

from __future__ import annotations

import os
import time
from typing import Any

import httpx

BACKEND_URL    = os.environ.get("BACKEND_URL", "http://localhost:8000")
ADMIN_EMAIL    = os.environ.get("EXP2_ADMIN_EMAIL",    "exp2-admin@hv.local")
ADMIN_PASSWORD = os.environ.get("EXP2_ADMIN_PASSWORD", "exp2-admin-changeme")

# Large dataset (500k rows) RF fit takes ~minutes on a laptop. 600s is the
# same headroom training_jobs uses for in-memory job retention.
POLL_INTERVAL_S = 1.0
POLL_TIMEOUT_S  = 600


def login() -> str:
    """Obtain a JWT for the seeded exp2 admin. Raises on non-2xx."""
    # /auth/login uses OAuth2PasswordRequestForm — form-encoded, "username"
    # carries the email. Do not switch to json=.
    r = httpx.post(
        f"{BACKEND_URL}/api/v1/auth/login",
        data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=10,
    )
    r.raise_for_status()
    return r.json()["access_token"]


def trigger_training(
    token: str,
    *,
    threshold: float,
    dataset_size: int,
    feature_version: str,
    force_fail: bool = False,
    random_state: int = 42,
    mode: str = "simulation",
) -> str:
    """POST /train and return the job_id. Job runs async in a BackgroundTask."""
    payload = {
        "mode":            mode,
        "threshold":       threshold,
        "dataset_size":    dataset_size,
        "feature_version": feature_version,
        "random_state":    random_state,
        "force_fail":      force_fail,
    }
    r = httpx.post(
        f"{BACKEND_URL}/api/v1/train/",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    r.raise_for_status()
    return r.json()["job_id"]


def wait_for_result(token: str, job_id: str) -> dict[str, Any]:
    """Poll GET /train/{job_id} until status leaves pending/running."""
    deadline = time.time() + POLL_TIMEOUT_S
    headers  = {"Authorization": f"Bearer {token}"}
    url      = f"{BACKEND_URL}/api/v1/train/{job_id}"

    while time.time() < deadline:
        r = httpx.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        job = r.json()
        if job["status"] in ("succeeded", "failed"):
            return job
        time.sleep(POLL_INTERVAL_S)

    raise TimeoutError(f"job {job_id} did not finish in {POLL_TIMEOUT_S}s")
