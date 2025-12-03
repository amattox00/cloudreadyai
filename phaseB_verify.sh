#!/usr/bin/env bash
set -euo pipefail

echo "------------------------------------------------------------"
echo "CloudReadyAI Phase B — Ingestion & Run Registry Verification"
echo "------------------------------------------------------------"

BACKEND_URL="http://localhost:8000"

SAMPLES_DIR="$(pwd)/samples"
SERVERS_CSV="${SAMPLES_DIR}/phaseB_servers.csv"
STORAGE_CSV="${SAMPLES_DIR}/phaseB_storage.csv"
NETWORK_CSV="${SAMPLES_DIR}/phaseB_network.csv"

echo
echo "[0] Checking sample CSVs exist..."
for f in "$SERVERS_CSV" "$STORAGE_CSV" "$NETWORK_CSV"; do
  if [[ -f "$f" ]]; then
    echo "✔ Found $f"
  else
    echo "✖ MISSING: $f"
  fi
done

echo
echo "[1] Checking backend health..."
if curl -sS "${BACKEND_URL}/healthz"; then
  :
else
  echo "✖ /healthz FAILED"
  exit 1
fi

echo
echo "[2] Ingesting SERVERS sample (no run_id)..."
curl -sS -X POST "${BACKEND_URL}/v1/ingest/servers" \
  -F "file=@${SERVERS_CSV}" || echo "✖ Servers ingest failed"

echo
echo "[3] Ingesting STORAGE sample (no run_id)..."
curl -sS -X POST "${BACKEND_URL}/v1/ingest/storage" \
  -F "file=@${STORAGE_CSV}" || echo "✖ Storage ingest failed"

echo
echo "[4] Ingesting NETWORK sample (no run_id)..."
curl -sS -X POST "${BACKEND_URL}/v1/ingest/network" \
  -F "file=@${NETWORK_CSV}" || echo "✖ Network ingest failed"

echo
echo "[5] Checking ingestion status..."
curl -sS "${BACKEND_URL}/v1/ingest/status" || echo "✖ /v1/ingest/status failed"

echo "------------------------------------------------------------"
echo "Phase B ingestion verification completed."
echo "Review the rows_ingested values above."
echo "------------------------------------------------------------"
