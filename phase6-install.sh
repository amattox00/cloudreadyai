#!/usr/bin/env bash
set -euo pipefail

# === Paths ===
ROOT="/home/ec2-user/cloudreadyai"
BACK="$ROOT/backend"
APP="$BACK/app"
VENV="$BACK/.venv"
MAIN="$APP/main.py"
ENV="$BACK/.env"

echo "== Phase 6: Live Price Refresh scaffolding =="

# --- 1) Ensure dirs ---
mkdir -p "$APP/routers" \
         "$APP/modules/ingestors" \
         "$APP/utils"

# --- 2) ENV additions (non-destructive) ---
touch "$ENV"
add_env () { grep -q "^$1=" "$ENV" || echo "$1=$2" >> "$ENV"; }
add_env PHASE6_ENABLE true
add_env PHASE6_MODE mock           # mock|static|live (live wiring in Phase 7+)
add_env PHASE6_TIMEOUT 8           # per-provider fetch timeout (seconds)
add_env PHASE6_REGIONS us-east-1   # comma list (expand later)
add_env PHASE6_SERVICES ec2        # comma list (ec2|compute|vm etc)
add_env PHASE6_CACHE_TTL 600       # seconds for cached price docs
add_env REDIS_HOST 127.0.0.1
add_env REDIS_PORT 6379

# --- 3) Minimal RQ helper (queue connection) ---
cat >"$APP/utils/rq_conn.py" <<'PY'
import os, redis
from rq import Queue
def _redis():
    host = os.getenv("REDIS_HOST","127.0.0.1")
    port = int(os.getenv("REDIS_PORT","6379"))
    return redis.Redis(host=host, port=port, decode_responses=True)
def queue(name="default"):
    return Queue(name, connection=_redis())
PY

# --- 4) Phase6 ingestor job: refresh provider prices into same Phase5 cache keys ---
cat >"$APP/modules/ingestors/prices_refresh.py" <<'PY'
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
PY

# --- 5) Phase6 router: trigger refresh + check status ---
cat >"$APP/routers/phase6.py" <<'PY'
import os, time
from fastapi import APIRouter, HTTPException
from app.utils.rq_conn import queue
from rq.job import Job
import redis

router = APIRouter(prefix="/v1/providers", tags=["phase6"])

REDIS_HOST = os.getenv("REDIS_HOST","127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT","6379"))
PHASE6_ENABLE = os.getenv("PHASE6_ENABLE","true").lower() == "true"
STATUS_KEY = "phase6:status"
LAST_KEY   = "phase6:last_refresh"

def _r():
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

@router.post("/refresh")
def refresh_prices(provider:str, region:str, service:str):
    if not PHASE6_ENABLE:
        raise HTTPException(status_code=400, detail="Phase 6 disabled")
    from app.modules.ingestors.prices_refresh import do_refresh  # late import for worker compatibility
    q = queue()
    job = q.enqueue(do_refresh, provider, region, service, timeout=int(os.getenv("PHASE6_TIMEOUT","8")))
    return {"enqueued": True, "job_id": job.get_id(), "provider":provider, "region":region, "service":service}

@router.get("/status")
def refresh_status():
    r = _r()
    status = r.hgetall(STATUS_KEY) or {}
    last = r.hgetall(LAST_KEY) or {}
    return {"status": status, "last_refresh": last, "phase": 6}

PY

# --- 6) Wire router into main.py (idempotent) ---
grep -q 'from app\.routers import phase6' "$MAIN" || \
  sed -i '/from app\.routers import phase5/a from app.routers import phase6' "$MAIN"

grep -q 'include_router(phase6\.router)' "$MAIN" || \
  sed -i '/include_router(phase5\.router)/a app.include_router(phase6.router)' "$MAIN"

# --- 7) Python deps (idempotent) ---
source "$VENV/bin/activate"
pip install -q rq==2.6.0 httpx==0.27.2 redis==5.0.7 python-dotenv==1.0.1
deactivate

# --- 8) Restart services ---
sudo systemctl restart cloudready-backend
sudo systemctl restart cloudready-worker

echo "== Phase 6 install complete =="
