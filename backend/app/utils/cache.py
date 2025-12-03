import os, json, time
from typing import Optional, Callable
import redis

def _client():
    host = os.getenv("REDIS_HOST", "localhost")
    port = int(os.getenv("REDIS_PORT", "6379"))
    return redis.Redis(host=host, port=port, decode_responses=True)

def cache_get(key: str) -> Optional[dict]:
    r = _client()
    v = r.get(key)
    return json.loads(v) if v else None

def cache_set(key: str, val: dict, ttl_seconds: int = 600) -> None:
    r = _client()
    r.setex(key, ttl_seconds, json.dumps(val))

def cached(key: str, ttl_seconds: int, producer: Callable[[], dict]) -> dict:
    hit = cache_get(key)
    if hit is not None:
        return hit
    val = producer()
    cache_set(key, val, ttl_seconds)
    return val
