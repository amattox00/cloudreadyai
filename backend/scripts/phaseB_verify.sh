#!/usr/bin/env bash
set -euo pipefail

# Phase B Verification Script for CloudReadyAI
# Verifies:
#  - Backend health
#  - Presence of key ingestion tables (1–10)
#  - Row counts per table
#  - (Optional) OpenAPI paths for /v1/ingest/* endpoints

DB_HOST="localhost"
DB_USER="cloudready"
DB_NAME="cloudready"
BACKEND_URL="http://localhost:8000"

echo "========================================="
echo " CloudReadyAI Phase B Verification"
echo "========================================="
echo
echo "Backend:  ${BACKEND_URL}"
echo "DB:       ${DB_USER}@${DB_HOST}/${DB_NAME}"
echo

# -----------------------------
# 1. Check backend health
# -----------------------------
echo "1) Checking backend health (/healthz)..."
if curl -sS "${BACKEND_URL}/healthz" | grep -q '"ok":true'; then
  echo "   ✅ Backend healthz OK"
else
  echo "   ❌ Backend health check FAILED"
  echo "      (Is cloudready-backend.service running?)"
  exit 1
fi
echo

# Helper to run psql
psql_cmd() {
  psql -h "${DB_HOST}" -U "${DB_USER}" -d "${DB_NAME}" -tAc "$1"
}

# -----------------------------
# 2. Verify tables exist
# -----------------------------
echo "2) Checking required Phase B tables..."

TABLES=(
  "servers"
  "storage"
  "inventory_networks"
  "databases"
  "applications"
  "business_metadata"
  "app_dependencies"
  "os_metadata"
  "licensing_metadata"
  "utilization_metrics"
)

for tbl in "${TABLES[@]}"; do
  exists=$(psql_cmd "SELECT to_regclass('${tbl}');")
  exists_trimmed=$(echo "${exists}" | xargs)

  if [[ "${exists_trimmed}" == "${tbl}" ]]; then
    echo "   ✅ Table exists: ${tbl}"
  else
    echo "   ❌ MISSING table: ${tbl}"
  fi
done
echo

# -----------------------------
# 3. Show row counts (if tables exist)
# -----------------------------
echo "3) Row counts per Phase B table (for sanity)..."

for tbl in "${TABLES[@]}"; do
  exists=$(psql_cmd "SELECT to_regclass('${tbl}');")
  exists_trimmed=$(echo "${exists}" | xargs)

  if [[ "${exists_trimmed}" == "${tbl}" ]]; then
    count=$(psql_cmd "SELECT count(*) FROM ${tbl};")
    count_trimmed=$(echo "${count}" | xargs)
    echo "   - ${tbl}: ${count_trimmed} rows"
  else
    echo "   - ${tbl}: (table missing)"
  fi
done
echo

# -----------------------------
# 4. Optional: verify ingest endpoints via OpenAPI
# -----------------------------
echo "4) Checking ingest endpoints in OpenAPI (if jq is available)..."

if ! command -v jq >/dev/null 2>&1; then
  echo "   ⚠️  jq not installed; skipping OpenAPI endpoint checks."
else
  echo "   Downloading OpenAPI JSON..."
  OPENAPI_JSON=$(curl -sS "${BACKEND_URL}/openapi.json")

  ENDPOINTS=(
    "/v1/ingest/servers"
    "/v1/ingest/storage"
    "/v1/ingest/network"
    "/v1/ingest/databases"
    "/v1/ingest/applications"
    "/v1/ingest/business"
    "/v1/ingest/dependencies"
    "/v1/ingest/os"
    "/v1/ingest/licensing"
    "/v1/ingest/utilization"
  )

  for ep in "${ENDPOINTS[@]}"; do
    if echo "${OPENAPI_JSON}" | jq -r '.paths | keys[]' | grep -q "^${ep}$"; then
      echo "   ✅ Endpoint present in OpenAPI: ${ep}"
    else
      echo "   ❌ Endpoint MISSING from OpenAPI: ${ep}"
    fi
  done
fi

echo
echo "========================================="
echo " Phase B Verification complete."
echo " (If all ✅, Phase B is functionally ready.)"
echo "========================================="
