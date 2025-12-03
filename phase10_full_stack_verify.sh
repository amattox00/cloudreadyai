#!/usr/bin/env bash
set -euo pipefail

echo "============================================================"
echo " CloudReadyAI Phase 10 – Full Stack Readiness Verification"
echo "============================================================"
echo

ROOT_DIR="$HOME/cloudreadyai"
BACKEND_URL="http://localhost:8000"
FRONTEND_URL="http://localhost"

SERVICES=(
  "cloudready-devops"
  "cloudready-backend"
  "cloudready-worker"
  "cloudready-frontend"
)

FAILURES=0

check_service() {
  local svc="$1"
  if systemctl is-active --quiet "$svc"; then
    echo "  ✅ Service $svc is active"
  else
    echo "  ❌ Service $svc is NOT active"
    FAILURES=$((FAILURES + 1))
  fi
}

check_http() {
  local name="$1"
  local url="$2"
  local expect="$3"

  echo "  -> Checking $name at $url"
  local resp
  resp=$(curl -sS "$url" || true)
  if [[ "$resp" == *"$expect"* ]]; then
    echo "     ✅ $name OK (matched '$expect')"
  else
    echo "     ❌ $name FAILED – response did not contain '$expect'"
    echo "        Response: $resp"
    FAILURES=$((FAILURES + 1))
  fi
}

echo "------------------------------------------------------------"
echo " [1] Systemd services"
echo "------------------------------------------------------------"

for svc in "${SERVICES[@]}"; do
  check_service "$svc"
done

echo
echo "------------------------------------------------------------"
echo " [2] HTTP health checks"
echo "------------------------------------------------------------"

# Backend health
check_http "Backend /healthz" "$BACKEND_URL/healthz" '"ok":true'

# Frontend basic check – just make sure we get some HTML back
echo "  -> Checking Frontend at $FRONTEND_URL (basic HTML presence)"
FRONTEND_RESP=$(curl -sS "$FRONTEND_URL" || true)
if [[ "$FRONTEND_RESP" == *"<html"* ]]; then
  echo "     ✅ Frontend appears to be serving HTML"
else
  echo "     ⚠️  Frontend check did NOT find '<html'. Response may still be valid for your setup."
  echo "        (Non-fatal for now.)"
fi

echo
echo "------------------------------------------------------------"
echo " [3] Phase 1–6 / legacy verification (if reverify_phases.sh exists)"
echo "------------------------------------------------------------"

if [[ -f "$ROOT_DIR/reverify_phases.sh" ]]; then
  echo "  -> Running reverify_phases.sh"
  if bash "$ROOT_DIR/reverify_phases.sh"; then
    echo "  ✅ reverify_phases.sh completed successfully"
  else
    echo "  ❌ reverify_phases.sh reported one or more failures"
    FAILURES=$((FAILURES + 1))
  fi
else
  echo "  (Skipped) reverify_phases.sh not found at $ROOT_DIR/reverify_phases.sh"
fi

echo
echo "------------------------------------------------------------"
echo " [4] Phase 8 → 7E → 9 pipeline verification"
echo "------------------------------------------------------------"

# Optional: refresh example ingestion (non-fatal if it fails)
if [[ -f "$ROOT_DIR/phase8_example_ingest.sh" ]]; then
  echo "  -> Running phase8_example_ingest.sh (non-fatal helper)"
  if bash "$ROOT_DIR/phase8_example_ingest.sh"; then
    echo "     ✅ Example ingestion completed"
  else
    echo "     ⚠️  Example ingestion failed; continuing but Phase 7E/9 may fail."
  fi
else
  echo "  (Skipped) phase8_example_ingest.sh not found"
fi

# Run the Phase 7E / 9 verifier (this IS fatal if it fails)
if [[ -f "$ROOT_DIR/phase7e_verify.sh" ]]; then
  echo "  -> Running phase7e_verify.sh"
  if bash "$ROOT_DIR/phase7e_verify.sh"; then
    echo "  ✅ Phase 7E / 9 verification passed"
  else
    echo "  ❌ Phase 7E / 9 verification failed"
    FAILURES=$((FAILURES + 1))
  fi
else
  echo "  ❌ phase7e_verify.sh not found at $ROOT_DIR/phase7e_verify.sh"
  FAILURES=$((FAILURES + 1))
fi

echo
echo "============================================================"
if [[ $FAILURES -eq 0 ]]; then
  echo " ✅ Phase 10 – Full Stack Readiness: PASSED"
  echo "============================================================"
  exit 0
else
  echo " ❌ Phase 10 – Full Stack Readiness: FAILED (failures: $FAILURES)"
  echo "     Check logs above for details."
  echo "============================================================"
  exit 1
fi
