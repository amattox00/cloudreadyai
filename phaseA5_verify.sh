#!/usr/bin/env bash
set -euo pipefail

RED="$(printf '\033[31m')"
GREEN="$(printf '\033[32m')"
YELLOW="$(printf '\033[33m')"
RESET="$(printf '\033[0m')"

PASS=0
FAIL=0

pass() { echo -e "${GREEN}✔ $1${RESET}"; PASS=$((PASS+1)); }
fail() { echo -e "${RED}✘ $1${RESET}"; FAIL=$((FAIL+1)); }

echo
echo "------------------------------------------------------------"
echo " CloudReadyAI Phase A5 — Diagram Generator Verification"
echo "------------------------------------------------------------"

# 1) Backend health
if curl -sS http://localhost:8000/healthz >/dev/null 2>&1; then
  pass "Backend /healthz is responding"
else
  fail "Backend /healthz is NOT responding"
fi

# 2) Ensure DiagramsPage references /v1/diagram endpoints
DP="frontend/src/pages/DiagramsPage.tsx"

if grep -q "/v1/diagram/generate" "$DP"; then
  pass "Frontend references /v1/diagram/generate"
else
  fail "Frontend does NOT reference /v1/diagram/generate"
fi

if grep -q "/v1/diagram/package" "$DP"; then
  pass "Frontend references /v1/diagram/package"
else
  fail "Frontend does NOT reference /v1/diagram/package"
fi

# 3) Call /v1/diagram/package directly with a small payload
TMP_JSON=/tmp/phaseA5_pkg_request.json
cat > "$TMP_JSON" << 'REQ'
{
  "clouds": ["aws"],
  "include_types": ["landing_zone"],
  "org_name": "5NINE Data Solutions",
  "environment": "Prod",
  "workload_name": "CloudReadyAI",
  "overlay_profile": null,
  "opportunity_id": null,
  "version_tag": "v1"
}
REQ

HTTP_CODE=$(curl -sS -w '%{http_code}' -o /tmp/phaseA5_pkg_response.json \
  -X POST http://localhost:8000/v1/diagram/package \
  -H "Content-Type: application/json" \
  --data-binary @"$TMP_JSON" || echo "000")

if [ "$HTTP_CODE" = "200" ]; then
  pass "/v1/diagram/package returned 200"
else
  fail "/v1/diagram/package did NOT return 200 (got $HTTP_CODE)"
fi

# 4) Basic sanity on response fields
if grep -q "zip_filename" /tmp/phaseA5_pkg_response.json && \
   grep -q "zip_base64"  /tmp/phaseA5_pkg_response.json; then
  pass "Response includes zip_filename and zip_base64"
else
  fail "Response missing zip_filename and/or zip_base64"
fi

echo
echo "------------------------------------------------------------"
echo " Phase A5 Verification Summary"
echo "------------------------------------------------------------"
echo "  Passed checks: $PASS"
echo "  Failed checks: $FAIL"

if [ "$FAIL" -eq 0 ]; then
  echo -e "${GREEN}All Phase A5 checks PASSED.${RESET}"
else
  echo -e "${RED}Some Phase A5 checks FAILED. Review above messages.${RESET}"
fi
