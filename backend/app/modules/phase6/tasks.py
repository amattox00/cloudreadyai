import os, json
from typing import List
import httpx
from app.utils.rq_conn import get_redis
from app.modules.ingestors import providers_live

PHASE5_ENDPOINT = "http://127.0.0.1:8000/v1/providers/prices"

def _phase5_warm(provider: str, region: str, service: str, timeout: int = 8) -> dict:
    params = {"provider": provider, "region": region, "service": service}
    with httpx.Client(timeout=timeout) as c:
        r = c.get(PHASE5_ENDPOINT, params=params)
        r.raise_for_status()
        return r.json()

def refresh_prices(providers: List[str], regions: List[str], services: List[str]) -> dict:
    """
    Phase 7-aware refresh:
      - If PHASE7_MODE=live → fetch via providers_live, store in Phase-5 cache key for continuity
      - Else → call Phase-5 endpoint to warm cache (mock/static as configured)
    """
    timeout = int(os.getenv("PHASE7_TIMEOUT", os.getenv("PHASE5_PRICES_TIMEOUT", "8")))
    max_results = int(os.getenv("PHASE7_MAX_RESULTS", os.getenv("PHASE5_PRICES_MAX_RESULTS", "20")))
    filter_compute = os.getenv("PHASE7_FILTER_COMPUTE", os.getenv("PHASE5_PRICES_FILTER_COMPUTE", "true")).lower() == "true"

    rds = get_redis()
    results = []
    used_live = providers_live.is_live()

    for p in providers:
        for rg in regions:
            for svc in services:
                key = f"phase5:prices:{p}:{rg}:{svc}"
                try:
                    if used_live:
                        payload = providers_live.fetch_prices(p, rg, svc, timeout=timeout, max_results=max_results, filter_compute=filter_compute)
                        # store into Phase-5 cache key so UI/Phase-5 route sees fresh data
                        rds.setex(key, int(os.getenv("PHASE5_CACHE_TTL", "600")), json.dumps(payload))
                        results.append({"provider": p, "region": rg, "service": svc, "mode": "live", "count": len(payload.get("items", []))})
                    else:
                        payload = _phase5_warm(p, rg, svc, timeout=timeout)
                        # the Phase-5 route already caches, but we also ensure key exists
                        rds.setex(key, int(os.getenv("PHASE5_CACHE_TTL", "600")), json.dumps(payload))
                        results.append({"provider": p, "region": rg, "service": svc, "mode": "phase5", "count": len(payload.get("items", payload.get("data", [])))})
                except Exception as e:
                    results.append({"provider": p, "region": rg, "service": svc, "mode": "error", "error": str(e)})

    return {"ok": True, "used_live": used_live, "results": results}
