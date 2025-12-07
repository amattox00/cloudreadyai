#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 <run_id>"
  exit 1
fi

RUN_ID="$1"

# Move to backend root (one level up from tools/)
cd "$(dirname "$0")/.."

# Activate virtualenv
. .venv/bin/activate

echo "=== Rollup for $RUN_ID ==="
curl -s "http://127.0.0.1:8000/v2/runs/$RUN_ID/rollup" | jq

echo
echo "=== Analysis v2 summary for $RUN_ID ==="
curl -s "http://127.0.0.1:8000/v2/analysis/$RUN_ID/summary" | jq

echo
echo "=== Python deep-dive for $RUN_ID ==="
python -m tools.test_analysis_v2 "$RUN_ID"
