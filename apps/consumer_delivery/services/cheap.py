"""
cheap — minimum-work endpoint for the cache-overhead experiment.

Designed as the true "cheap" baseline against `/data/smart_watch` (adapter chain)
and `/overview` (hourly aggregate):

  - exactly one indexed query: latest heart_rate row for the user
  - no adapter / no transform / no Pydantic schema
  - same cache path as the other endpoints (Redis GET → JSON.loads on hit)

Cache contract:
  - key = f"cheap:{user_id}"
  - ttl = CHEAP_CACHE_TTL (default 5 s; aligned with smart_watch for fair comparison)
  - value = the full result dict
"""

from __future__ import annotations

import os
import time
from typing import Optional
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

from core.cache import cache_get, cache_set


_CACHE_ENABLED  = os.getenv("CACHE_ENABLED", "true").lower() != "false"
CHEAP_CACHE_TTL = int(os.getenv("CHEAP_CACHE_TTL", "5"))


# Single indexed lookup. Pulls only the columns we need and casts the JSONB
# value to float in-SQL so the Python side does no parsing.
_LATEST_HR_SQL = text("""
    SELECT timestamp, (data->>'value')::float AS hr
    FROM sensor_recordings
    WHERE user_id = :uid
      AND sensor_type = 'heart_rate'
    ORDER BY timestamp DESC
    LIMIT 1;
""")


def get_cheap(db: Session, user_id: UUID) -> Optional[dict]:
    cache_key = f"cheap:{user_id}"

    if _CACHE_ENABLED:
        cached = cache_get(cache_key)
        if cached is not None:
            cached["cache_hit"] = True
            return cached

    t0 = time.perf_counter()
    row = db.execute(_LATEST_HR_SQL, {"uid": str(user_id)}).fetchone()
    db_ms = (time.perf_counter() - t0) * 1000.0

    if row is None:
        return None

    result = {
        "user_id":   str(user_id),
        "hr":        float(row.hr) if row.hr is not None else None,
        "timestamp": row.timestamp.isoformat() if row.timestamp else None,
        "cache_hit": False,
        "db_ms":     round(db_ms, 2),
    }

    if _CACHE_ENABLED:
        cache_set(cache_key, result, ttl_seconds=CHEAP_CACHE_TTL)

    return result
