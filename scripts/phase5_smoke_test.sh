#!/usr/bin/env bash
set -euo pipefail
URL="${1:-http://localhost}"

curl -fsS "$URL/v1/providers/prices?provider=AWS&region=us-east-1" | head -c 200 >/dev/null && echo "[OK] providers/prices AWS"

curl -fsS "$URL/v1/match/services" \
  -H 'Content-Type: application/json' \
  -d '{"vcpus":8,"memory_gb":32,"os":"linux","storage_gb":500}' >/dev/null && echo "[OK] match/services"

curl -fsS "$URL/v1/cost/compare" \
  -H 'Content-Type: application/json' \
  -d '{"vcpus":8,"memory_gb":32,"os":"linux","storage_gb":500}' >/dev/null && echo "[OK] cost/compare"

curl -fsS "$URL/v1/recommend" \
  -H 'Content-Type: application/json' \
  -d '{"vcpus":8,"memory_gb":32,"os":"linux","storage_gb":500,"constraints":{"windows_bias":false}}' >/dev/null && echo "[OK] recommend"

curl -fsS "$URL/v1/diagram" >/dev/null && echo "[OK] diagram"
