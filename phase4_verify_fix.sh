#!/usr/bin/env bash
set -euo pipefail

echo "==[ Rewriting phase4_verify.sh to match current /v1/cost/estimate schema ]=="

ROOT_DIR="$HOME/cloudreadyai"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

cat > "$ROOT_DIR/phase4_verify.sh" << 'SHEOF'
#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$HOME/cloudreadyai"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

PASS=0
FAIL=0

ok() {
  echo "✔ $1"
  PASS=$((PASS + 1))
}

fail() {
  echo "✘ $1"
  FAIL=$((FAIL + 1))
}

echo
echo "------------------------------------------------------------"
echo "CloudReadyAI Phase 4 — Verification Run"
echo "------------------------------------------------------------"

# 1) Basic repo structure
if [[ -d "$BACKEND_DIR" ]]; then
  ok "Repo: backend/ exists"
else
  fail "Repo: backend/ missing"
fi

if [[ -d "$FRONTEND_DIR" ]]; then
  ok "Repo: frontend/ exists"
else
  fail "Repo: frontend/ missing"
fi

# 2) Key backend files
cd "$BACKEND_DIR"

if [[ -f "app/cost/calculator.py" ]]; then
  ok "File: app/cost/calculator.py"
else
  fail "File missing: app/cost/calculator.py"
fi

if [[ -f "app/cost/pricing.py" ]]; then
  ok "File: app/cost/pricing.py"
else
  fail "File missing: app/cost/pricing.py"
fi

if [[ -f "pricing_tables/aws.csv" ]]; then
  ok "File: pricing_tables/aws.csv"
else
  fail "File missing: pricing_tables/aws.csv"
fi

if [[ -f "pricing_tables/azure.csv" ]]; then
  ok "File: pricing_tables/azure.csv"
else
  fail "File missing: pricing_tables/azure.csv"
fi

if [[ -f "pricing_tables/gcp.csv" ]]; then
  ok "File: pricing_tables/gcp.csv"
else
  fail "File missing: pricing_tables/gcp.csv"
fi

if [[ -f "app/api/routes/cost.py" ]]; then
  ok "File: app/api/routes/cost.py"
else
  fail "File missing: app/api/routes/cost.py"
fi

if [[ -f "test_costing.py" ]]; then
  ok "File: test_costing.py"
else
  fail "File missing: test_costing.py"
fi

# 3) Python import checks
if [[ -d ".venv" ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

python3 - << 'PY' >/dev/null 2>&1 && echo "OK" || echo "FAIL" | {
from app import app as app_pkg  # noqa: F401
from app import cost as cost_pkg  # noqa: F401
from app.cost import pricing as pricing_mod  # noqa: F401
from app.api.routes import cost as cost_route  # noqa: F401
PY
} | {
  read -r status
  if [[ "$status" == "OK" ]]; then
    echo "✔ Python import OK: app"
    echo "✔ Python import OK: app.cost"
    echo "✔ Python import OK: app.cost.pricing"
    echo "✔ Python import OK: app.api.routes.cost"
    PASS=$((PASS + 4))
  else
    echo "✘ One or more Python imports failed (app / cost / pricing / cost route)."
    FAIL=$((FAIL + 1))
  fi
}

# 4) Run unit tests for costing logic
if pytest -q test_costing.py >/dev/null 2>&1; then
  ok "Pytest: test_costing.py passed"
else
  fail "Pytest: test_costing.py FAILED"
fi

# 5) Service checks (backend / worker / frontend / nginx)
for svc in cloudready-backend cloudready-worker cloudready-frontend nginx; do
  if systemctl is-active --quiet "$svc"; then
    ok "Service active: $svc"
  else
    fail "Service NOT active: $svc"
  fi
done

# 6) API check for /v1/cost/estimate with CURRENT schema
COST_URL="http://localhost:8000/v1/cost/estimate"
REQ_BODY='{
  "provider": "aws",
  "region": "us-east-1",
  "workloads": [
    {
      "name": "demo",
      "vcpus": 4,
      "memory_gb": 16,
      "storage_gib": 200,
      "storage_class": "standard",
      "hours_per_month": 730,
      "egress_gib": 10,
      "ha_multiplier": 1,
      "dr_multiplier": 1
    }
  ],
  "scenario": {
    "name": "baseline",
    "rightsize_factor": 1.0,
    "burst_percent": 0
  }
}'

HTTP_CODE=$(curl -sS -w "%{http_code}" -o /tmp/phase4_cost_response.json \
  -H "Content-Type: application/json" \
  -d "$REQ_BODY" \
  "$COST_URL" || echo "000")

if [[ "$HTTP_CODE" == "200" ]]; then
  ok "API /v1/cost/estimate (HTTP 200)"
  # Basic sanity: response non-empty
  if [[ -s /tmp/phase4_cost_response.json ]]; then
    ok "API /v1/cost/estimate returned non-empty JSON"
  else
    fail "API /v1/cost/estimate returned empty body"
  fi
else
  fail "API /v1/cost/estimate (HTTP $HTTP_CODE)"
  echo "  Response body:"
  sed 's/^/    /' /tmp/phase4_cost_response.json || true
fi

# 7) Optional: check backend services are enabled at boot (non-fatal if not all enabled)
for svc in cloudready-backend cloudready-worker cloudready-frontend nginx; do
  if systemctl is-enabled --quiet "$svc"; then
    ok "Service enabled: $svc"
  else
    echo "⚠️  Service NOT enabled: $svc (non-fatal for Phase 4)"
  fi
done

echo "------------------------------------------------------------"
if [[ $FAIL -eq 0 ]]; then
  echo "✅ Phase 4 Verification: ALL CHECKS PASSED ($PASS total)."
  exit 0
else
  echo "❌ Phase 4 Verification: $FAIL CHECK(S) FAILED, $PASS passed."
  echo "Failed checks may indicate issues with the cost engine or services."
  exit 1
fi
SHEOF

chmod +x "$ROOT_DIR/phase4_verify.sh"
echo "Updated $ROOT_DIR/phase4_verify.sh"
