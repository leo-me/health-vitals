import json
import os
from typing import Any, Optional

import redis as redis_lib

_client: Optional[redis_lib.Redis] = None


def get_redis() -> redis_lib.Redis:
    global _client
    if _client is None:
        _client = redis_lib.Redis(
            host=os.getenv("REDIS_HOST", "redis"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            decode_responses=True,
        )
    return _client


def cache_get(key: str) -> Optional[dict]:
    raw = get_redis().get(key)
    return json.loads(raw) if raw else None


def cache_set(key: str, value: dict, ttl_seconds: int = 60) -> None:
    get_redis().setex(key, ttl_seconds, json.dumps(value, default=str))
