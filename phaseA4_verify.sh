#!/usr/bin/env bash
set -euo pipefail

RED="$(printf '\033[31m')"
GREEN="$(printf '\033[32m')"
YELLOW="$(printf '\033[33m')"
RESET="$(printf '\033[0m')"

PASS_COUNT=0
FAIL_COUNT=0

pass() { echo -e "${GREEN}✔ $1${RESET}"; PASS_COUNT=$((PASS_COUNT+1)); }
fail() { echo -e "${RED}✘ $1${RESET}"; FAIL_COUNT=$((FAIL_COUNT+1)); }

print_header() {
  echo
  echo "------------------------------------------------------------"
  echo " CloudReadyAI Phase A4 — Ingestion API + UI Verification"
  echo "------------------------------------------------------------"
}

print_footer() {
  echo
  echo "------------------------------------------------------------"
  echo " Phase A4 Verification Summary"
  echo "------------------------------------------------------------"
  echo "  Passed checks: ${PASS_COUNT}"
  echo "  Failed checks: ${FAIL_COUNT}"
  if [ "${FAIL_COUNT}" -eq 0 ]; then
    echo -e "All Phase A4 checks ${GREEN}PASSED.${RESET}"
  else
    echo -e "Some Phase A4 checks ${RED}FAILED.${RESET} Review messages above."
  fi
}

print_header

# 1) Backend health
if curl -sS http://localhost:8000/healthz >/dev/null 2>&1; then
  pass "Backend /healthz is responding"
else
  fail "Backend /healthz is NOT responding"
fi

# 2) Create a sample workload via /v1/workloads/save
SAMPLE_ID="phaseA4-sample-1"

cat > /tmp/phaseA4_sample_workload.json << JSONEOF
{
  "workload": {
    "workload_id": "${SAMPLE_ID}",
    "name": "PhaseA4 Sample Workload",
    "description": "Created by phaseA4_verify.sh",
    "environment": "prod",
    "deployment_model": "aws",
    "business": null,
    "nodes": [
      {
        "node_id": "app1",
        "name": "Sample App",
        "role": "app",
        "layer": "application",
        "technology_type": "web_app",
        "platform": {
          "location": "aws",
          "service_hint": "ec2",
          "region": "us-east-1",
          "account_id": null
        },
        "sizing": null,
        "labels": [],
        "metadata": {}
      }
    ],
    "edges": []
  }
}
JSONEOF

SAVE_RESP_FILE=/tmp/phaseA4_save_resp.json
SAVE_HTTP_CODE=$(curl -sS -w '\n%{http_code}' \
  -X POST http://localhost:8000/v1/workloads/save \
  -H "Content-Type: application/json" \
  --data-binary @/tmp/phaseA4_sample_workload.json \
  > "${SAVE_RESP_FILE}" 2>/dev/null || echo "000")

if [ "${SAVE_HTTP_CODE}" = "200" ]; then
  pass "POST /v1/workloads/save returned 200"
else
  fail "POST /v1/workloads/save did NOT return 200 (got ${SAVE_HTTP_CODE})"
fi

# 3) Confirm sample appears in /v1/workloads/list
LIST_RESP_FILE=/tmp/phaseA4_list_resp.json
LIST_HTTP_CODE=$(curl -sS -w '\n%{http_code}' \
  http://localhost:8000/v1/workloads/list \
  > "${LIST_RESP_FILE}" 2>/dev/null || echo "000")

if [ "${LIST_HTTP_CODE}" = "200" ]; then
  pass "GET /v1/workloads/list returned 200"
else
  fail "GET /v1/workloads/list did NOT return 200 (got ${LIST_HTTP_CODE})"
fi

if grep -q "\"workload_id\":\"${SAMPLE_ID}\"" "${LIST_RESP_FILE}" 2>/dev/null; then
  pass "Sample workload_id ${SAMPLE_ID} appears in /v1/workloads/list response"
else
  fail "Sample workload_id ${SAMPLE_ID} NOT found in /v1/workloads/list response"
fi

# 4) Frontend DiagramsPage ingestion UI checks
DIAGRAMS_PAGE="./frontend/src/pages/DiagramsPage.tsx"

if grep -q "Workload Ingestion" "${DIAGRAMS_PAGE}" 2>/dev/null; then
  pass "DiagramsPage.tsx contains 'Workload Ingestion' panel title"
else
  fail "DiagramsPage.tsx is missing 'Workload Ingestion' panel title"
fi

if grep -q "/v1/workloads/save" "${DIAGRAMS_PAGE}" 2>/dev/null; then
  pass "DiagramsPage.tsx calls /v1/workloads/save"
else
  fail "DiagramsPage.tsx does NOT reference /v1/workloads/save"
fi

if grep -q "/v1/workloads/list" "${DIAGRAMS_PAGE}" 2>/dev/null; then
  pass "DiagramsPage.tsx calls /v1/workloads/list"
else
  fail "DiagramsPage.tsx does NOT reference /v1/workloads/list"
fi

print_footer
