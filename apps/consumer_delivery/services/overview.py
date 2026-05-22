"""
overview — multi-day aggregation over sensor_recordings for one user.

Designed to be expensive enough that Redis caching actually wins. The query
buckets all of a user's readings by hour and computes per-sensor aggregates
(avg / max / min / count) within a configurable window.

Window anchoring: instead of `now() - interval :days days`, the window is
anchored at the user's own `max(timestamp)` — there are two reasons:

  1. The fixture data lives in early 2026; using `now()` (later) would yield
     an empty window and the cache test would degenerate.
  2. IBI timestamps in the loaded dataset are corrupted (cumulative offsets
     push them to ~2078). We exclude `sensor_type = 'ibi'` from both the
     anchor computation and the aggregation.

Cache contract:
  - key = f"overview:{user_id}:{days}"
  - ttl = OVERVIEW_CACHE_TTL (default 60 s)
  - value = the full JSON-encodable result dict
"""

from __future__ import annotations

import os
import time
from typing import Optional
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

from core.cache import cache_get, cache_set


_CACHE_ENABLED   = os.getenv("CACHE_ENABLED", "true").lower() != "false"
OVERVIEW_CACHE_TTL = int(os.getenv("OVERVIEW_CACHE_TTL", "60"))


# Single CTE-based query — kept verbatim for traceability. Excludes 'ibi'
# because its loaded timestamps are corrupted in the current dataset.
#
# ACC rows store {"x", "y", "z"} (not {"value"}); every other signal stores
# {"value"}. We compute the per-row magnitude inline so the aggregate row for
# sensor_type='acc' is meaningful instead of NULL.
_OVERVIEW_SQL = text("""
    WITH anchor AS (
        SELECT MAX(timestamp) AS t
        FROM sensor_recordings
        WHERE user_id = :uid
          AND sensor_type <> 'ibi'
    ),
    typed AS (
        SELECT
            sr.timestamp,
            sr.sensor_type,
            CASE
                WHEN sr.sensor_type = 'acc' THEN
                    sqrt(
                        ((sr.data->>'x')::float) ^ 2 +
                        ((sr.data->>'y')::float) ^ 2 +
                        ((sr.data->>'z')::float) ^ 2
                    )
                ELSE
                    NULLIF((sr.data->>'value')::float, NULL)
            END AS v
        FROM sensor_recordings sr, anchor
        WHERE sr.user_id     = :uid
          AND sr.sensor_type <> 'ibi'
          AND anchor.t IS NOT NULL
          AND sr.timestamp   > anchor.t - (:days || ' days')::interval
          AND sr.timestamp  <= anchor.t
    )
    SELECT
        date_trunc('hour', timestamp)  AS bucket,
        sensor_type                     AS sensor_type,
        COUNT(*)                        AS n,
        AVG(v)                          AS avg_value,
        MAX(v)                          AS max_value,
        MIN(v)                          AS min_value
    FROM typed
    GROUP BY 1, 2
    ORDER BY 1, 2;
""")


def get_overview(
    db: Session,
    user_id: UUID,
    days: int,
) -> Optional[dict]:
    """
    Returns the aggregated overview for one user, or None if no data exists.
    Result shape:
        {
          "user_id":   "...",
          "days":      7,
          "bucket_count": 42,
          "cache_hit":   true/false,
          "db_ms":       123.4,   # only present on cache miss
          "buckets": [
              {"bucket": "...", "sensor_type": "eda",
               "n": 14400, "avg": 2.51, "max": 6.2, "min": 0.0},
              ...
          ]
        }
    """
    cache_key = f"overview:{user_id}:{days}"

    if _CACHE_ENABLED:
        cached = cache_get(cache_key)
        if cached is not None:
            cached["cache_hit"] = True
            return cached

    t0 = time.perf_counter()
    rows = db.execute(_OVERVIEW_SQL, {"uid": str(user_id), "days": days}).fetchall()
    db_ms = (time.perf_counter() - t0) * 1000.0

    if not rows:
        return None

    buckets = [
        {
            "bucket":      r.bucket.isoformat() if r.bucket else None,
            "sensor_type": r.sensor_type if isinstance(r.sensor_type, str) else r.sensor_type.value,
            "n":           int(r.n),
            "avg":         float(r.avg_value) if r.avg_value is not None else None,
            "max":         float(r.max_value) if r.max_value is not None else None,
            "min":         float(r.min_value) if r.min_value is not None else None,
        }
        for r in rows
    ]

    result = {
        "user_id":      str(user_id),
        "days":         days,
        "bucket_count": len(buckets),
        "cache_hit":    False,
        "db_ms":        round(db_ms, 2),
        "buckets":      buckets,
    }

    if _CACHE_ENABLED:
        cache_set(cache_key, result, ttl_seconds=OVERVIEW_CACHE_TTL)

    return result
