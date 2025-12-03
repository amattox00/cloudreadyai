#!/usr/bin/env bash
set -euo pipefail

################################################################################
# CloudReadyAI — Phase 5 Installer & Scaffolding Script
# Purpose:
#   - Create backend stubs for pricing connectors (AWS, Azure, GCP)
#   - Create Phase 5 API routes (pricing, matching, compare, recommend, diagram)
#   - Add minimal recommendation/matching engines (rule-based)
#   - Add DB bootstrap script for Phase 5 tables (idempotent)
#   - Wire into existing FastAPI app & worker
#   - Append Phase 5 env vars
#   - Restart services
#
# Assumptions (based on earlier phases):
#   - Repo root: /home/ec2-user/cloudreadyai
#   - FastAPI backend at backend/app
#   - Celery worker at backend/worker.py (or backend/app/worker.py)
#   - Postgres/Redis via docker-compose in devops/ (Phase 1-4)
#   - Systemd units: cloudready-backend, cloudready-worker, cloudready-frontend, cloudready-devops
#
# Safe to re-run: YES (idempotent where practical)
################################################################################

ROOT="/home/ec2-user/cloudreadyai"
BACKEND="$ROOT/backend"
APP="$BACKEND/app"
ROUTERS="$APP/routers"
MODULES="$APP/modules"
PROVIDERS="$MODULES/providers"
SCRIPTS="$ROOT/scripts"
ENV_FILE="$ROOT/.env"
LOG_DIR="/var/log/cloudready"

# --- Guards ------------------------------------------------------------------
if [[ ! -d "$ROOT" ]]; then
  echo "[ERROR] Expected repo at $ROOT — aborting." >&2
  exit 1
fi

mkdir -p "$ROUTERS" "$MODULES" "$PROVIDERS" "$SCRIPTS" "$LOG_DIR"
chmod 755 "$LOG_DIR"

# --- Helper: insert line into file if absent ---------------------------------
ins_if_absent() {
  local file="$1"; shift
  local line="$*"
  grep -Fqx "$line" "$file" 2>/dev/null || echo "$line" >> "$file"
}

# --- Phase 5 Env Vars ---------------------------------------------------------
create_env() {
  touch "$ENV_FILE"
  ins_if_absent "$ENV_FILE" "# ==== Phase 5 Settings ===="
  ins_if_absent "$ENV_FILE" "ENABLE_PHASE5=1"
  ins_if_absent "$ENV_FILE" "AWS_PRICING_INDEX=https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/index.json"
  ins_if_absent "$ENV_FILE" "AZURE_PRICES_API=https://prices.azure.com/api/retail/prices"
  ins_if_absent "$ENV_FILE" "GCP_BILLING_API_BASE=https://cloudbilling.googleapis.com/v1"
  ins_if_absent "$ENV_FILE" "GCP_BILLING_API_KEY=REPLACE_ME_OPTIONAL"
  ins_if_absent "$ENV_FILE" "DEFAULT_REGIONS=aws:us-east-1,azure:eastus,gcp:us-central1"
}

# --- Requirements (lightweight) ----------------------------------------------
add_requirements() {
  local req="$BACKEND/requirements.txt"
  if [[ -f "$req" ]]; then
    ins_if_absent "$req" "httpx==0.27.2"
    ins_if_absent "$req" "pydantic==2.9.2"
    ins_if_absent "$req" "python-dotenv==1.0.1"
  fi
}

# --- DB Bootstrap Script (idempotent) ----------------------------------------
cat > "$SCRIPTS/phase5_migrate.py" <<'PYEOF'
#!/usr/bin/env python3
import os, sys
import psycopg2
from urllib.parse import urlparse

DATABASE_URL = os.getenv('DATABASE_URL') or os.getenv('POSTGRES_URL') or ''
if not DATABASE_URL:
    print('[phase5_migrate] No DATABASE_URL/POSTGRES_URL set; skipping.')
    sys.exit(0)

u = urlparse(DATABASE_URL)
# Support postgres:// and postgresql://
if u.scheme.startswith('postgres'):
    conn = psycopg2.connect(DATABASE_URL)
else:
    print('[phase5_migrate] Unsupported DB URL; skipping.')
    sys.exit(0)

DDL = [
    # Pricing cache for normalized SKU items
    '''CREATE TABLE IF NOT EXISTS cr_pricing_cache (
        id SERIAL PRIMARY KEY,
        provider TEXT NOT NULL,
        sku TEXT NOT NULL,
        region TEXT NOT NULL,
        unit TEXT NOT NULL,
        price_per_unit NUMERIC(18,8) NOT NULL,
        currency TEXT NOT NULL DEFAULT 'USD',
        description TEXT,
        raw JSONB,
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        UNIQUE(provider, sku, region, unit)
    );''',
    # Service matching templates (family → instance/storage/network templates)
    '''CREATE TABLE IF NOT EXISTS cr_service_templates (
        id SERIAL PRIMARY KEY,
        provider TEXT NOT NULL,
        family TEXT NOT NULL,
        template JSONB NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        UNIQUE(provider, family)
    );''',
    # Recommendations history
    '''CREATE TABLE IF NOT EXISTS cr_recommendations (
        id SERIAL PRIMARY KEY,
        workload_id TEXT NOT NULL,
        input JSONB NOT NULL,
        decision JSONB NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );'''
]

with conn:
    with conn.cursor() as cur:
        for stmt in DDL:
            cur.execute(stmt)
        conn.commit()

print('[phase5_migrate] Completed successfully.')
PYEOF
chmod +x "$SCRIPTS/phase5_migrate.py"

# --- Provider Connectors ------------------------------------------------------
cat > "$PROVIDERS/aws.py" <<'PYEOF'
from typing import Dict, Any, List
import httpx
import os

AWS_INDEX = os.getenv('AWS_PRICING_INDEX', 'https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/index.json')

async def fetch_compute_pricing(region: str) -> Dict[str, Any]:
    """Fetch a minimal subset (on-demand Linux) for EC2; return raw map {sku: price}.
       For production, switch to specific EC2 offer file for the region family.
    """
    async with httpx.AsyncClient(timeout=30) as client:
        idx = (await client.get(AWS_INDEX)).json()
        ec2_offer_url = idx['offers']['AmazonEC2']['currentVersionUrl']
        offer = (await client.get(f"https://pricing.us-east-1.amazonaws.com{ec2_offer_url}")).json()
        # Ultra-minimal example: extract some Linux On-Demand prices
        prices: Dict[str, Any] = {}
        terms = offer.get('terms', {}).get('OnDemand', {})
        products = offer.get('products', {})
        for sku, prod in products.items():
            if prod.get('productFamily') != 'Compute Instance':
                continue
            attr = prod.get('attributes', {})
            if attr.get('operatingSystem') != 'Linux':
                continue
            if attr.get('location') is None:
                continue
            # NOTE: Region mapping would be required for exact filter; simplified here
            if region and region not in attr.get('location', ''):
                continue
            term = terms.get(sku, {})
            for _, term_obj in term.items():
                for _, p in term_obj.get('priceDimensions', {}).items():
                    prices[sku] = {
                        'desc': p.get('description'),
                        'unit': p.get('unit'),
                        'price_per_unit': float(p.get('pricePerUnit', {}).get('USD', '0') or 0),
                    }
        return prices

PYEOF

cat > "$PROVIDERS/azure.py" <<'PYEOF'
from typing import Dict, Any
import httpx
import os

AZURE_API = os.getenv('AZURE_PRICES_API', 'https://prices.azure.com/api/retail/prices')

async def query_prices(filter_expr: str) -> Dict[str, Any]:
    """Query Azure retail prices with an OData filter; returns combined result page(s)."""
    items = []
    next_url = f"{AZURE_API}?$filter={filter_expr}"
    async with httpx.AsyncClient(timeout=30) as client:
        while next_url:
            data = (await client.get(next_url)).json()
            items.extend(data.get('Items', []))
            next_url = data.get('NextPageLink')
    return {'items': items}

PYEOF

cat > "$PROVIDERS/gcp.py" <<'PYEOF'
from typing import Dict, Any
import httpx
import os

BASE = os.getenv('GCP_BILLING_API_BASE', 'https://cloudbilling.googleapis.com/v1')
API_KEY = os.getenv('GCP_BILLING_API_KEY')

async def list_skus(service_name: str) -> Dict[str, Any]:
    """List SKUs for a GCP service (e.g., services/6F81-5844-456A for Compute Engine)."""
    params = {}
    if API_KEY:
        params['key'] = API_KEY
    async with httpx.AsyncClient(timeout=30) as client:
        url = f"{BASE}/{service_name}/skus"
        data = (await client.get(url, params=params)).json()
        return data

PYEOF

# --- Matching & Recommendation modules ---------------------------------------
cat > "$MODULES/matching.py" <<'PYEOF'
from typing import Dict, Any

# Simplified rule-based matcher. Real logic can evolve to ML.
# Input example:
#   {"vcpus": 8, "memory_gb": 32, "os": "linux", "storage_gb": 500}

def match_services(payload: Dict[str, Any]) -> Dict[str, Any]:
    v = payload
    vcpus = int(v.get('vcpus', 2))
    mem = float(v.get('memory_gb', 8))
    osname = (v.get('os') or 'linux').lower()

    def pick_aws():
        # naive mapping
        if vcpus <= 2 and mem <= 8:
            inst = 't3.small'
        elif vcpus <= 4 and mem <= 16:
            inst = 'm6i.large'
        elif vcpus <= 8 and mem <= 32:
            inst = 'm6i.2xlarge'
        else:
            inst = 'm6i.4xlarge'
        return {"compute": inst, "storage": {"type": "gp3", "iops": "auto"}}

    def pick_azure():
        if vcpus <= 2 and mem <= 8:
            inst = 'B2s'
        elif vcpus <= 4 and mem <= 16:
            inst = 'D4s_v5'
        elif vcpus <= 8 and mem <= 32:
            inst = 'D8s_v5'
        else:
            inst = 'D16s_v5'
        disk = 'Premium SSD' if osname == 'windows' else 'Premium SSD v2'
        return {"compute": inst, "storage": {"type": disk}}

    def pick_gcp():
        if vcpus <= 2 and mem <= 8:
            inst = 'e2-standard-2'
        elif vcpus <= 4 and mem <= 16:
            inst = 'n2-standard-4'
        elif vcpus <= 8 and mem <= 32:
            inst = 'n2-standard-8'
        else:
            inst = 'n2-standard-16'
        return {"compute": inst, "storage": {"type": "pd-balanced"}}

    return {
        "AWS": pick_aws(),
        "Azure": pick_azure(),
        "GCP": pick_gcp(),
    }
PYEOF

cat > "$MODULES/recommend.py" <<'PYEOF'
from typing import Dict, Any

# Minimal decision engine: uses cost (if provided) + simple tie-breakers.
# Inputs:
#   - matches: output from matching.match_services
#   - costs: { provider: { 'monthly_total': float } }
#   - constraints: { region, compliance, windows_bias, analytics_bias }

def recommend(matches: Dict[str, Any], costs: Dict[str, Any], constraints: Dict[str, Any] | None = None) -> Dict[str, Any]:
    constraints = constraints or {}
    # 1) Prefer lowest cost
    best = None
    best_p = None
    for p, v in costs.items():
        mt = float(v.get('monthly_total', 9e18))
        if best is None or mt < best:
            best = mt
            best_p = p

    # 2) Biasing rules (very simplified)
    if constraints.get('windows_bias'):
        best_p = 'Azure'
    if constraints.get('analytics_bias'):
        best_p = 'GCP'

    return {
        'recommended_provider': best_p or 'AWS',
        'explanation': 'Selected by lowest monthly_total with simple bias rules.',
        'match': matches.get(best_p or 'AWS'),
        'cost': costs.get(best_p or 'AWS'),
    }
PYEOF

# --- Phase 5 API Router -------------------------------------------------------
cat > "$ROUTERS/phase5.py" <<'PYEOF'
from fastapi import APIRouter, Query
from typing import Dict, Any
import os

from app.modules import matching, recommend
from app.modules.providers import aws as aws_provider
from app.modules.providers import azure as azure_provider
from app.modules.providers import gcp as gcp_provider

router = APIRouter(prefix="/v1", tags=["phase5"])

@router.get("/providers/prices")
async def providers_prices(provider: str = Query(..., pattern="^(AWS|Azure|GCP)$"), region: str | None = None):
    if provider == 'AWS':
        data = await aws_provider.fetch_compute_pricing(region or '')
        return {"provider": provider, "region": region, "data": data}
    if provider == 'Azure':
        f = "serviceFamily eq 'Compute' and priceType eq 'Consumption'"
        data = await azure_provider.query_prices(f)
        return {"provider": provider, "data": data}
    if provider == 'GCP':
        # Compute Engine service name is stable, but may change; kept configurable later
        data = await gcp_provider.list_skus("services/6F81-5844-456A")
        return {"provider": provider, "data": data}

@router.post("/match/services")
async def match_services(payload: Dict[str, Any]):
    return matching.match_services(payload)

@router.post("/cost/compare")
async def cost_compare(payload: Dict[str, Any]):
    """Very simplified monthly total calculator; expects matches already selected,
       or uses default assumptions per provider. In real Phase 5, fetch exact prices.
    """
    matches = payload.get('matches') or matching.match_services(payload)
    # Placeholder monthly figures (to be replaced by real pull from pricing providers)
    # Using rough relative factors
    baseline = 400.0  # dummy baseline
    mult = {
        'AWS': 1.00,
        'Azure': 0.98,
        'GCP': 0.97,
    }
    costs = {
        p: {
            'instance': baseline * mult[p] * 0.85,
            'storage': baseline * mult[p] * 0.10,
            'network': baseline * mult[p] * 0.05,
            'monthly_total': baseline * mult[p],
        }
        for p in ['AWS','Azure','GCP']
    }
    return {'matches': matches, 'costs': costs}

@router.post("/recommend")
async def make_recommendation(payload: Dict[str, Any]):
    constraints = payload.get('constraints') or {}
    # Run compare first
    compare = await cost_compare(payload)
    return recommend.recommend(compare['matches'], compare['costs'], constraints)

@router.get("/diagram")
async def get_diagram_stub():
    # Placeholder: Phase 5 will return a generated SVG/PNG; here we return a stub
    return {
        'format': 'svg',
        'content': '<svg width="300" height="120" xmlns="http://www.w3.org/2000/svg">\n  <rect x="10" y="10" width="280" height="100" rx="12" ry="12" fill="#eef" stroke="#99f"/>\n  <text x="150" y="65" text-anchor="middle" font-family="Arial" font-size="14">CloudReadyAI Phase 5 Diagram Stub</text>\n</svg>'
    }
PYEOF

# --- Wire router into FastAPI app --------------------------------------------
MAIN_APP="$APP/main.py"
if [[ -f "$MAIN_APP" ]]; then
  if ! grep -q "from app.routers import phase5" "$MAIN_APP"; then
    sed -i "/from app.routers/a from app.routers import phase5" "$MAIN_APP"
  fi
  if ! grep -q "app.include_router(phase5.router)" "$MAIN_APP"; then
    sed -i "/include_router.*health.*$/a \
app.include_router(phase5.router)" "$MAIN_APP" || true
    # Fallback: append at end if pattern not found
    grep -q "app.include_router(phase5.router)" "$MAIN_APP" || echo "\napp.include_router(phase5.router)" >> "$MAIN_APP"
  fi
else
  echo "[WARN] $MAIN_APP not found; please wire router manually." >&2
fi

# --- Optional: Worker task stub ----------------------------------------------
cat > "$APP/worker_tasks_phase5.py" <<'PYEOF'
from typing import Dict, Any

# Placeholder for async/background tasks (e.g., prefetch pricing, cache SKUs)

def warm_pricing_cache(payload: Dict[str, Any] | None = None) -> str:
    # No-op stub — connect to providers and preload common SKUs in a real impl
    return 'OK'
PYEOF

# --- Make a minimal test for /v1 endpoints -----------------------------------
cat > "$SCRIPTS/phase5_smoke_test.sh" <<'BASH'
#!/usr/bin/env bash
set -euo pipefail
URL="${1:-http://localhost}"

curl -fsS "$URL/v1/providers/prices?provider=AWS&region=us-east-1" | head -c 200 >/dev/null && echo "[OK] providers/prices AWS"

curl -fsS "$URL/v1/match/services" \
  -H 'Content-Type: application/json' \
  -d '{"vcpus":8,"memory_gb":32,"os":"linux","storage_gb":500}' >/dev/null && echo "[OK] match/services"

curl -fsS "$URL/v1/cost/compare" \
  -H 'Content-Type: application/json' \
  -d '{"vcpus":8,"memory_gb":32,"os":"linux","storage_gb":500}' >/dev/null && echo "[OK] cost/compare"

curl -fsS "$URL/v1/recommend" \
  -H 'Content-Type: application/json' \
  -d '{"vcpus":8,"memory_gb":32,"os":"linux","storage_gb":500,"constraints":{"windows_bias":false}}' >/dev/null && echo "[OK] recommend"

curl -fsS "$URL/v1/diagram" >/dev/null && echo "[OK] diagram"
BASH
chmod +x "$SCRIPTS/phase5_smoke_test.sh"

# --- Apply env/requirements and run DB migrate -------------------------------
create_env
add_requirements || true

# Try to run DB migrate via Python inside backend venv if present
if [[ -d "$BACKEND/.venv" ]]; then
  source "$BACKEND/.venv/bin/activate"
  pip install -r "$BACKEND/requirements.txt" --quiet || true
  # psycopg2 may not be present; try install if DATABASE_URL is set
  if [[ -n "${DATABASE_URL:-${POSTGRES_URL:-}}" ]]; then
    pip install psycopg2-binary --quiet || true
  fi
  python "$SCRIPTS/phase5_migrate.py" || true
  deactivate || true
else
  echo "[WARN] No backend venv found at $BACKEND/.venv — skipping migrate." >&2
fi

# --- Restart services (best-effort) ------------------------------------------
for svc in cloudready-backend cloudready-worker; do
  if systemctl is-enabled --quiet "$svc" 2>/dev/null; then
    sudo systemctl restart "$svc" || true
    sudo systemctl --no-pager --full status "$svc" | sed -n '1,6p' || true
  fi
done

# --- Final notes --------------------------------------------------------------
echo "\n[Phase 5] Scaffolding complete."
echo "- New API endpoints:"
echo "    GET  /v1/providers/prices?provider=AWS|Azure|GCP&region=..."
echo "    POST /v1/match/services {vcpus,memory_gb,os,storage_gb}"
echo "    POST /v1/cost/compare   { ...same payload... }"
echo "    POST /v1/recommend       { ... + constraints }"
echo "    GET  /v1/diagram"
echo "- Run smoke test:  $SCRIPTS/phase5_smoke_test.sh http://localhost"
echo "- Update GCP_BILLING_API_KEY in .env if you want GCP live calls."
