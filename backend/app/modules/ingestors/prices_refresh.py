import os, json, time, httpx
from typing import Dict, Tuple
import redis

REDIS_HOST = os.getenv("REDIS_HOST","127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT","6379"))
PHASE6_CACHE_TTL = int(os.getenv("PHASE6_CACHE_TTL","600"))

STATUS_KEY = "phase6:status"
LAST_KEY   = "phase6:last_refresh"

def _r():
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def _pkey(provider:str, region:str, service:str)->str:
    return f"phase5:prices:{provider}:{region}:{service}"

def _status_set(state:str, detail:str=""):
    _r().hset(STATUS_KEY, mapping={"state":state, "detail":detail, "ts":str(int(time.time()))})

def _fetch_local_prices(provider:str, region:str, service:str, timeout:int=8)->Dict:
    # Call our own Phase 5 endpoint (mock/static/live modes controlled by ENV)
    url = f"http://127.0.0.1:8000/v1/providers/prices"
    params = {"provider":provider, "region":region, "service":service}
    with httpx.Client(timeout=timeout) as c:
        resp = c.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

def do_refresh(provider:str, region:str, service:str, timeout:int=8)->Tuple[bool,str]:
    """Worker function run by RQ."""
    r = _r()
    try:
        _status_set("RUNNING", f"{provider}:{region}:{service}")
        data = _fetch_local_prices(provider, region, service, timeout=timeout)
        r.setex(_pkey(provider,region,service), PHASE6_CACHE_TTL, json.dumps(data))
        r.hset(LAST_KEY, f"{provider}:{region}:{service}", str(int(time.time())))
        _status_set("OK", f"{provider}:{region}:{service}")
        return True, "OK"
    except Exception as e:
        _status_set("ERROR", str(e))
        return False, str(e)
