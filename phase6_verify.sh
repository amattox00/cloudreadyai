#!/usr/bin/env bash
set -euo pipefail

BACKEND_URL="http://localhost:8000"

PASS=0
FAIL=0

ok() {
  echo "  ✔ $1"
  PASS=$((PASS + 1))
}

fail() {
  echo "  ✘ $1"
  FAIL=$((FAIL + 1))
}

echo "------------------------------------------------------------"
echo " CloudReadyAI Phase 6 — Cloud Intelligence Engine 2.0 Verify"
echo "------------------------------------------------------------"

# 1) Health check
echo "[1] Backend health check..."
HEALTH_JSON=$(curl -sS "${BACKEND_URL}/healthz" || true)
if [[ "$HEALTH_JSON" == *'"ok":true'* ]]; then
  ok "Backend /healthz OK"
else
  fail "Backend /healthz FAILED (response: $HEALTH_JSON)"
fi

# 2) Providers
echo "[2] Listing providers..."
PROVIDERS_JSON=$(curl -sS "${BACKEND_URL}/v1/phase6/providers" || true)
if [[ "$PROVIDERS_JSON" == *'"providers"'* ]] && [[ "$PROVIDERS_JSON" == *'"mode"'* ]]; then
  ok "Phase 6 providers endpoint OK"
else
  fail "Phase 6 providers endpoint FAILED (response: $PROVIDERS_JSON)"
fi

# 3) Instance types (mock/hybrid)
echo "[3] Fetching instance types for provider=aws, region=us-east-1..."
IT_JSON=$(curl -sS -X POST "${BACKEND_URL}/v1/phase6/instance-types" \
  -H "Content-Type: application/json" \
  -d '{"provider":"aws","region":"us-east-1","limit":3}' || true)

if [[ "$IT_JSON" == *'"items"'* ]]; then
  ok "Instance types endpoint returned items"
else
  fail "Instance types endpoint FAILED (response: $IT_JSON)"
fi

# 4) Pricing
echo "[4] Fetching pricing for provider=aws, region=us-east-1, instance_type=t3.medium..."
PRICE_JSON=$(curl -sS -X POST "${BACKEND_URL}/v1/phase6/pricing" \
  -H "Content-Type: application/json" \
  -d '{"provider":"aws","region":"us-east-1","instance_type":"t3.medium","hours_per_month":730}' || true)

if [[ "$PRICE_JSON" == *'"quote"'* ]] && [[ "$PRICE_JSON" == *'"monthly_usd"'* ]]; then
  ok "Pricing endpoint returned quote"
else
  fail "Pricing endpoint FAILED (response: $PRICE_JSON)"
fi

# 5) Recommendation
echo "[5] Requesting recommendation for simple workload..."
RECOMM_JSON=$(curl -sS -X POST "${BACKEND_URL}/v1/phase6/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "workload": {
      "total_vcpus": 8,
      "total_memory_gb": 32,
      "environment": "prod",
      "criticality": "high"
    }
  }' || true)

if [[ "$RECOMM_JSON" == *'"chosen"'* ]] && [[ "$RECOMM_JSON" == *'"scores"'* ]]; then
  ok "Recommendation endpoint returned chosen provider + scores"
else
  fail "Recommendation endpoint FAILED (response: $RECOMM_JSON)"
fi

# 6) Full analysis
echo "[6] Requesting full analysis for simple workload..."
FA_JSON=$(curl -sS -X POST "${BACKEND_URL}/v1/phase6/full-analysis" \
  -H "Content-Type: application/json" \
  -d '{
    "workload": {
      "total_vcpus": 8,
      "total_memory_gb": 32,
      "environment": "prod",
      "criticality": "high"
    }
  }' || true)

if [[ "$FA_JSON" == *'"recommendation"'* ]] && [[ "$FA_JSON" == *'"instance_samples"'* ]]; then
  ok "Full analysis endpoint returned recommendation + instance samples"
else
  fail "Full analysis endpoint FAILED (response: $FA_JSON)"
fi

echo "------------------------------------------------------------"
if [[ $FAIL -eq 0 ]]; then
  echo "✅ Phase 6 Verification: ALL CHECKS PASSED ($PASS total)."
  exit 0
else
  echo "❌ Phase 6 Verification: $FAIL CHECK(S) FAILED, $PASS passed."
  exit 1
fi
