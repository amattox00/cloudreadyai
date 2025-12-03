#!/usr/bin/env bash
set -euo pipefail

echo "------------------------------------------------------------"
echo "CloudReadyAI Phase A — Verification Run"
echo "------------------------------------------------------------"

BACKEND_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:3000"
NGINX_URL="http://localhost"

echo
echo "[1] Checking systemd services..."
systemctl is-active --quiet cloudready-backend && echo "✔ cloudready-backend active" || echo "✖ cloudready-backend NOT active"
systemctl is-active --quiet cloudready-frontend && echo "✔ cloudready-frontend active" || echo "✖ cloudready-frontend NOT active"
systemctl is-active --quiet cloudready-devops && echo "✔ cloudready-devops active" || echo "✖ cloudready-devops NOT active"
systemctl is-active --quiet cloudready-worker && echo "✔ cloudready-worker active" || echo "✖ cloudready-worker NOT active"

echo
echo "[2] Backend health check..."
curl -sS "${BACKEND_URL}/healthz" || echo "✖ /healthz FAILED"

echo
echo "[3] Run registry smoke test..."
echo "- GET /v1/run_registry"
curl -sS "${BACKEND_URL}/v1/run_registry" || echo "✖ GET /v1/run_registry FAILED"

echo
echo "- POST /v1/run_registry (test run)"
curl -sS -X POST "${BACKEND_URL}/v1/run_registry" \
  -H "Content-Type: application/json" \
  -d '{"name":"PhaseA Verify Run","source":"phaseA_verify"}' || echo "✖ POST /v1/run_registry FAILED"

echo
echo "[4] Ingestion status smoke test..."
curl -sS "${BACKEND_URL}/v1/ingest/status" || echo "✖ GET /v1/ingest/status FAILED"

echo
echo "[5] Diagram engine smoke test..."
echo "- POST /v1/diagram/generate"
curl -sS -X POST "${BACKEND_URL}/v1/diagram/generate" \
  -H "Content-Type: application/json" \
  -d '{"cloud":"aws","diagram_type":"landing_zone"}' || echo "✖ /v1/diagram/generate FAILED"

echo
echo "- POST /v1/diagram/package (basic payload)"
curl -sS -X POST "${BACKEND_URL}/v1/diagram/package" \
  -H "Content-Type: application/json" \
  -d '{
    "org_name": "PhaseA Verify Org",
    "environment": "Dev",
    "workload_name": "PhaseA",
    "overlay_profile": "none",
    "opportunity_id": "PHASEA-VERIFY",
    "version_tag": "v1"
  }' || echo "✖ /v1/diagram/package FAILED"

echo
echo "[6] Frontend (Vite preview) smoke test..."
curl -sS "${FRONTEND_URL}" >/dev/null && echo "✔ Frontend Vite preview responding" || echo "✖ Frontend Vite preview NOT responding"

echo
echo "[7] Nginx / dashboard smoke test (optional)..."
curl -sS "${NGINX_URL}/dashboard" >/dev/null && echo "✔ Nginx /dashboard responding" || echo "✖ Nginx /dashboard FAILED (might be http->https or firewall)"

echo
echo "------------------------------------------------------------"
echo "Phase A verification completed. Review any ✖ lines above."
echo "------------------------------------------------------------"
