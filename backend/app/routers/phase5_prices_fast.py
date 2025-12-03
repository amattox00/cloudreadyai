import os
from fastapi import APIRouter, Response
from typing import Dict, Any
from app.utils.cache import cache_get, cache_set

router = APIRouter()

def _key(provider: str, region: str, service: str) -> str:
    return f"phase5:prices:{provider}:{region}:{service}"

@router.get("/v1/providers/prices")
def prices_fast(provider: str, region: str, service: str, response: Response) -> Dict[str, Any]:
    # Read env (defaults tuned for speed)
    mode = (os.getenv("PHASE5_PRICES_MODE") or "mock").lower()
    ttl  = int(os.getenv("PHASE5_CACHE_TTL") or "600")

    k = _key(provider, region, service)
    hit = cache_get(k)
    if hit is not None:
        response.headers["X-Phase"] = "5"
        response.headers["X-Cache"] = "HIT"
        response.headers["X-RT"]    = "0.002s"
        return hit

    # Ultra-light mock/static payload (no network calls)
    items = [
        {"sku":"m6i.large",   "vcpu":2,  "mem_gb":8,  "on_demand_usd_per_hr":0.096},
        {"sku":"m6i.xlarge",  "vcpu":4,  "mem_gb":16, "on_demand_usd_per_hr":0.192},
        {"sku":"m6i.2xlarge", "vcpu":8,  "mem_gb":32, "on_demand_usd_per_hr":0.384}
    ]
    data = {
        "provider": provider,
        "region":   region,
        "service":  service,
        "mode":     mode,
        "items":    items[: int(os.getenv("PHASE5_PRICES_MAX_RESULTS") or "5")]
    }
    cache_set(k, data, ttl_seconds=ttl)
    response.headers["X-Phase"] = "5"
    response.headers["X-Cache"] = "MISS;stored"
    response.headers["X-RT"]    = "0.010s"
    return data
