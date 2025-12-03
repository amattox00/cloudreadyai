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

warn() {
  echo "⚠️  $1"
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

if [[ -f "app/api/routes/cost.py" ]]; then
  ok "File: app/api/routes/cost.py"
else
  fail "File missing: app/api/routes/cost.py"
fi

# Pricing tables are nice-to-have; warn if missing, but don't fail
for f in pricing_tables/aws.csv pricing_tables/azure.csv pricing_tables/gcp.csv; do
  if [[ -f "$f" ]]; then
    ok "File: $f"
  else
    warn "Optional file missing: $f (pricing may be using defaults or alternative sources)"
  fi
done

# Unit test file is optional; warn if missing
if [[ -f "test_costing.py" ]]; then
  ok "File: test_costing.py"
  TEST_FILE_PRESENT=1
else
  warn "Optional unit test missing: test_costing.py"
  TEST_FILE_PRESENT=0
fi

# 3) Python import checks (match current structure)
if [[ -d ".venv" ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

if python3 - << 'PY'
from app.cost import pricing as pricing_mod  # noqa: F401
from app.api.routes import cost as cost_route  # noqa: F401
PY
then
  ok "Python import OK: app.cost.pricing"
  ok "Python import OK: app.api.routes.cost"
else
  fail "Python import failed for app.cost.pricing and/or app.api.routes.cost"
fi

# 4) Run unit tests if present (optional)
if [[ "$TEST_FILE_PRESENT" -eq 1 ]]; then
  if pytest -q test_costing.py >/dev/null 2>&1; then
    ok "Pytest: test_costing.py passed"
  else
    fail "Pytest: test_costing.py FAILED"
  fi
else
  warn "Skipping pytest: test_costing.py not present"
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

# 7) Optional: service enabled checks (non-fatal, informational)
for svc in cloudready-backend cloudready-worker cloudready-frontend nginx; do
  if systemctl is-enabled --quiet "$svc"; then
    ok "Service enabled: $svc"
  else
    warn "Service NOT enabled: $svc (non-fatal for Phase 4)"
  fi
done

echo "------------------------------------------------------------"
if [[ $FAIL -eq 0 ]]; then
  echo "✅ Phase 4 Verification: ALL CRITICAL CHECKS PASSED ($PASS total)."
  exit 0
else
  echo "❌ Phase 4 Verification: $FAIL CRITICAL CHECK(S) FAILED, $PASS passed."
  echo "Failed checks may indicate issues with the cost engine or services."
  exit 1
fi
