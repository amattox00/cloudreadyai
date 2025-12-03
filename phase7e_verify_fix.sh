#!/usr/bin/env bash
set -euo pipefail

echo "==[ Fixing phase7e_verify.sh to correctly parse JSON outputs ]=="

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
HEALTH_JSON=\$(curl -sS "\$BACKEND_URL/healthz" || true)
if [[ "\$HEALTH_JSON" != *'"ok":true'* ]]; then
  echo "  ❌ Health check failed. Response: \$HEALTH_JSON"
  exit 1
fi
echo "  ✅ Backend health OK."

# 2) List workloads
echo "[2] Listing workloads at \$BACKEND_URL/v1/workloads/list ..."
WORKLOADS_JSON=\$(curl -sS "\$BACKEND_URL/v1/workloads/list" || true)

WORKLOAD_ID=\$(echo "\$WORKLOADS_JSON" | python3 - << 'PY'
import json, sys
try:
    data = json.loads(sys.stdin.read())
    items = data.get("items", [])
    if items:
        print(items[0].get("workload_id", ""))
    else:
        print("")
except Exception:
    print("")
PY
)

if [[ -z "\$WORKLOAD_ID" ]]; then
  echo "  ❌ No workloads found in /v1/workloads/list. Add at least one workload (e.g. via phase8_example_ingest.sh)."
  exit 1
fi

echo "  ✅ Found workload_id: \$WORKLOAD_ID"

# 3) Test diagram generation v2
echo "[3] Testing /v1/diagram/generate_v2 for workload_id=\$WORKLOAD_ID ..."

DIAGRAM_JSON=\$(curl -sS -X POST "\$BACKEND_URL/v1/diagram/generate_v2" \
  -H "Content-Type: application/json" \
  -d "{\\"workload_id\\": \\"\$WORKLOAD_ID\\"}" || true)

HAS_XML=\$(echo "\$DIAGRAM_JSON" | python3 - << 'PY'
import json, sys
try:
    data = json.loads(sys.stdin.read())
    xml = data.get("xml", "")
    if isinstance(xml, str) and len(xml) > 0:
        print("yes")
    else:
        print("no")
except Exception:
    print("no")
PY
)

if [[ "\$HAS_XML" != "yes" ]]; then
  echo "  ❌ Diagram v2 generation failed or returned no XML."
  echo "     Response: \$DIAGRAM_JSON"
  exit 1
fi

echo "  ✅ Diagram v2 generation OK (XML length > 0)."

# 4) Test deliverables packaging v2
echo "[4] Testing /v1/deliverables/package_v2 for workload_id=\$WORKLOAD_ID ..."

DELIV_JSON=\$(curl -sS -X POST "\$BACKEND_URL/v1/deliverables/package_v2" \
  -H "Content-Type: application/json" \
  -d "{\\"workload_id\\": \\"\$WORKLOAD_ID\\", \\"opportunity_id\\": \\"TEST-OPP-7E-9\\"}" || true)

HAS_ZIP=\$(echo "\$DELIV_JSON" | python3 - << 'PY'
import json, sys
try:
    data = json.loads(sys.stdin.read())
    zfn = data.get("zip_filename", "")
    zb64 = data.get("zip_base64", "")
    if isinstance(zfn, str) and zfn and isinstance(zb64, str) and len(zb64) > 0:
        print("yes")
    else:
        print("no")
except Exception:
    print("no")
PY
)

if [[ "\$HAS_ZIP" != "yes" ]]; then
  echo "  ❌ Deliverables packaging v2 failed or returned invalid data."
  echo "     Response: \$DELIV_JSON"
  exit 1
fi

echo "  ✅ Deliverables packaging v2 OK (zip filename + base64 present)."

echo
echo "✅ Phase 7E / 9 verification PASSED."
SHEOF

chmod +x phase7e_verify.sh
echo "Updated phase7e_verify.sh"
