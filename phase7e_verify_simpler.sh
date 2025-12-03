#!/usr/bin/env bash
set -euo pipefail

echo "==[ Rewriting phase7e_verify.sh with simpler parsing ]=="

cd ~/cloudreadyai

cat > phase7e_verify.sh << 'SHEOF'
#!/usr/bin/env bash
set -euo pipefail

echo "------------------------------------------------------------"
echo "CloudReadyAI Phase 7E / 9 – Diagram & Deliverables Verify"
echo "------------------------------------------------------------"

BACKEND_URL="http://localhost:8000"

# 1) Health check
echo "[1] Checking backend health at $BACKEND_URL/healthz ..."
HEALTH_JSON=$(curl -sS "$BACKEND_URL/healthz" || true)
if [[ "$HEALTH_JSON" != *'"ok":true'* ]]; then
  echo "  ❌ Health check failed. Response: $HEALTH_JSON"
  exit 1
fi
echo "  ✅ Backend health OK."

# 2) List workloads
echo "[2] Listing workloads at $BACKEND_URL/v1/workloads/list ..."
WORKLOADS_JSON=$(curl -sS "$BACKEND_URL/v1/workloads/list" || true)

# Try to extract the first workload_id using simple text processing
WORKLOAD_ID=$(echo "$WORKLOADS_JSON" \
  | sed -n 's/.*"workload_id":"\([^"]*\)".*/\1/p' \
  | head -n 1)

# Fallback: if nothing extracted but we know wl-ingested-sample-3tier exists, use that
if [[ -z "$WORKLOAD_ID" ]]; then
  if [[ "$WORKLOADS_JSON" == *"wl-ingested-sample-3tier"* ]]; then
    WORKLOAD_ID="wl-ingested-sample-3tier"
  fi
fi

if [[ -z "$WORKLOAD_ID" ]]; then
  echo "  ❌ No workloads found or could not parse workload_id from /v1/workloads/list."
  echo "     Raw response: $WORKLOADS_JSON"
  exit 1
fi

echo "  ✅ Found workload_id: $WORKLOAD_ID"

# 3) Test diagram generation v2
echo "[3] Testing /v1/diagram/generate_v2 for workload_id=$WORKLOAD_ID ..."

DIAGRAM_JSON=$(curl -sS -X POST "$BACKEND_URL/v1/diagram/generate_v2" \
  -H "Content-Type: application/json" \
  -d "{\"workload_id\": \"$WORKLOAD_ID\"}" || true)

if [[ "$DIAGRAM_JSON" == *'"xml"'* && "$DIAGRAM_JSON" != *'"xml":""'* ]]; then
  echo "  ✅ Diagram v2 generation OK (XML field present and non-empty)."
else
  echo "  ❌ Diagram v2 generation failed or returned no XML."
  echo "     Response: $DIAGRAM_JSON"
  exit 1
fi

# 4) Test deliverables packaging v2
echo "[4] Testing /v1/deliverables/package_v2 for workload_id=$WORKLOAD_ID ..."

DELIV_JSON=$(curl -sS -X POST "$BACKEND_URL/v1/deliverables/package_v2" \
  -H "Content-Type: application/json" \
  -d "{\"workload_id\": \"$WORKLOAD_ID\", \"opportunity_id\": \"TEST-OPP-7E-9\"}" || true)

if [[ "$DELIV_JSON" == *'"zip_filename"'* && "$DELIV_JSON" == *'"zip_base64"'* ]]; then
  echo "  ✅ Deliverables packaging v2 OK (zip filename + base64 present)."
else
  echo "  ❌ Deliverables packaging v2 failed or returned invalid data."
  echo "     Response: $DELIV_JSON"
  exit 1
fi

echo
echo "✅ Phase 7E / 9 verification PASSED."
SHEOF

chmod +x phase7e_verify.sh
echo "Updated phase7e_verify.sh"
