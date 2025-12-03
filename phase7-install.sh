#!/usr/bin/env bash
set -euo pipefail

echo "== Phase 7: Provider Integrations (scaffold) =="

BACK="/home/ec2-user/cloudreadyai/backend"
APP="$BACK/app"
MOD="$APP/modules"
PROV="$APP/providers"
PH6="$APP/routers/phase6.py"
ENV="$BACK/.env"

# 0) Sanity
test -d "$BACK" || { echo "Backend not found at $BACK"; exit 1; }
test -d "$APP"  || { echo "App dir not found at $APP"; exit 1; }

# 1) Python deps (httpx + backoff) inside venv
source "$BACK/.venv/bin/activate"
pip install --upgrade pip >/dev/null
pip install httpx backoff >/dev/null
deactivate

# 2) Dirs
sudo mkdir -p "$PROV" "$MOD/ingestors"
sudo chown -R ec2-user:ec2-user "$APP"

# 3) Provider package: __init__.py
cat >"$PROV/__init__.py" <<'PY'
# Provider package
PY

# 4) AWS provider (live-ready placeholder)
cat >"$PROV/aws.py" <<'PY'
import time
from typing import List, Dict, Any

def fetch_prices(region: str, service: str, timeout: int = 8, max_results: int = 20, filter_compute: bool = True) -> Dict[str, Any]:
    """
    Phase 7 live-ready placeholder for AWS pricing.
    In LIVE mode, you can replace the body with real calls to AWS Pricing APIs or curated endpoints.
    For now we return a tiny "live-shaped" payload quickly, suitable for UI/tests.
    """
    items = [
        {"sku": "m6i.large",   "vcpu": 2, "memory_gb": 8,  "price_hour": 0.096},
        {"sku": "m6i.xlarge",  "vcpu": 4, "memory_gb": 16, "price_hour": 0.192},
        {"sku": "m6i.2xlarge", "vcpu": 8, "memory_gb": 32, "price_hour": 0.384},
    ][:max_results]
    return {
        "provider": "AWS",
        "region": region,
        "service": service,
        "fetched_at": int(time.time()),
        "items": items,
        "note": "Phase 7 AWS live placeholder; swap with real fetch in production."
    }
PY

# 5) Azure provider (live-ready placeholder)
cat >"$PROV/azure.py" <<'PY'
import time
from typing import List, Dict, Any

def fetch_prices(region: str, service: str, timeout: int = 8, max_results: int = 20, filter_compute: bool = True) -> Dict[str, Any]:
    items = [
        {"sku": "D4s_v5",  "vcpu": 4, "memory_gb": 16, "price_hour": 0.20},
        {"sku": "D8s_v5",  "vcpu": 8, "memory_gb": 32, "price_hour": 0.40},
    ][:max_results]
    return {
        "provider": "Azure",
        "region": region,
        "service": service,
        "fetched_at": int(time.time()),
        "items": items,
        "note": "Phase 7 Azure live placeholder; swap with Retail Prices API usage."
    }
PY

# 6) GCP provider (live-ready placeholder)
cat >"$PROV/gcp.py" <<'PY'
import time
from typing import List, Dict, Any

def fetch_prices(region: str, service: str, timeout: int = 8, max_results: int = 20, filter_compute: bool = True) -> Dict[str, Any]:
    items = [
        {"sku": "n2-standard-4",  "vcpu": 4, "memory_gb": 16, "price_hour": 0.19},
        {"sku": "n2-standard-8",  "vcpu": 8, "memory_gb": 32, "price_hour": 0.38},
    ][:max_results]
    return {
        "provider": "GCP",
        "region": region,
        "service": service,
        "fetched_at": int(time.time()),
        "items": items,
        "note": "Phase 7 GCP live placeholder; swap with Cloud Billing Catalog usage."
    }
PY

# 7) Phase 7 orchestrator (decides live vs mock)
cat >"$MOD/ingestors/providers_live.py" <<'PY'
import os, json
from typing import Dict, Any
from app.providers import aws as aws_live
from app.providers import azure as azure_live
from app.providers import gcp as gcp_live

def is_live() -> bool:
    return os.getenv("PHASE7_MODE", "mock").lower() == "live"

def fetch_prices(provider: str, region: str, service: str,
                 timeout: int = 8, max_results: int = 20, filter_compute: bool = True) -> Dict[str, Any]:
    """
    If PHASE7_MODE=live, use provider module; otherwise raise to caller to fallback to Phase-5 path.
    """
    if not is_live():
        raise RuntimeError("phase7_not_live")
    p = provider.upper()
    if p == "AWS":
        return aws_live.fetch_prices(region, service, timeout, max_results, filter_compute)
    if p == "AZURE":
        return azure_live.fetch_prices(region, service, timeout, max_results, filter_compute)
    if p == "GCP":
        return gcp_live.fetch_prices(region, service, timeout, max_results, filter_compute)
    raise ValueError(f"Unsupported provider: {provider}")
PY

# 8) Patch Phase 6 worker task to try Phase 7 live first, then fallback to Phase 5 endpoint warm
TASKS="$APP/modules/phase6/tasks.py"
if [[ ! -f "$TASKS" ]]; then
  echo "ERROR: $TASKS not found. Phase 6 must be installed first."
  exit 1
fi

# Backup
cp -a "$TASKS" "${TASKS}.bak.phase7.$(date +%s)"

# Overwrite with live-first task (safe fallback to Phase 5 HTTP warm)
cat >"$TASKS" <<'PY'
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
PY

# 9) Ensure Phase 7 env flags exist (non-destructive append)
touch "$ENV"
grep -q '^PHASE7_MODE=' "$ENV" || echo 'PHASE7_MODE=mock' >> "$ENV"
grep -q '^PHASE7_TIMEOUT=' "$ENV" || echo 'PHASE7_TIMEOUT=8' >> "$ENV"
grep -q '^PHASE7_MAX_RESULTS=' "$ENV" || echo 'PHASE7_MAX_RESULTS=20' >> "$ENV"
grep -q '^PHASE7_FILTER_COMPUTE=' "$ENV" || echo 'PHASE7_FILTER_COMPUTE=true' >> "$ENV"

# 10) Restart services
sudo systemctl restart cloudready-backend cloudready-worker

# 11) Quick verification (mock mode, ensures no regressions)
cat >/tmp/phase7_verify.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail
echo "== Phase 7 Verify (mock mode) =="

health=$(curl -fsS http://127.0.0.1:8000/healthz || true)
[[ "$health" == *'"ok":true'* ]] && echo "✅ /healthz OK" || { echo "❌ /healthz failed"; exit 1; }

echo "→ Enqueue refresh job (AWS/us-east-1/ec2)"
jid=$(curl -sS -X POST -H "Content-Type: application/json" \
  -d '{"providers":["AWS"],"regions":["us-east-1"],"services":["ec2"]}' \
  http://127.0.0.1:8000/v1/refresh/prices | jq -r '.job_id' || true)

if [[ -z "${jid:-}" || "$jid" == "null" ]]; then
  echo "❌ enqueue failed"; exit 1
fi
echo "   job_id=$jid"

# poll status a few times
ok=0
for i in {1..10}; do
  sleep 1
  st=$(curl -sS "http://127.0.0.1:8000/v1/refresh/status?job_id=$jid" | jq -r '.status' || echo "unknown")
  echo "   status=$st"
  if [[ "$st" == "finished" ]]; then ok=1; break; fi
done

[[ $ok -eq 1 ]] && echo "✅ Job finished" || { echo "❌ Job did not finish"; exit 1; }

# verify phase-5 cache key exists
if command -v redis-cli >/dev/null 2>&1; then
  key=$(redis-cli KEYS 'phase5:prices:AWS:us-east-1:ec2' | head -n1 || true)
else
  # docker fallback
  key=$(docker exec -i devops-redis-1 redis-cli KEYS 'phase5:prices:AWS:us-east-1:ec2' | head -n1 || true)
fi

[[ -n "${key:-}" ]] && echo "✅ Cache key present: $key" || { echo "❌ Cache key missing"; exit 1; }

echo "✅ Phase 7 verify (mock) passed"
SH
chmod +x /tmp/phase7_verify.sh

echo "== Phase 7 installer complete =="
echo "Run:  /tmp/phase7_verify.sh"
