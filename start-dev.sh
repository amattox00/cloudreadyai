#!/usr/bin/env bash
set -euo pipefail

ROOT="$HOME/cloudreadyai"
COMPOSE="$ROOT/devops/docker-compose.yml"
BACKEND_DIR="$ROOT/backend"
FRONTEND_DIR="$ROOT/frontend"

# Ensure Docker is running
if ! systemctl is-active --quiet docker; then
  sudo systemctl enable --now docker
fi

# Bring up Postgres + Redis
docker compose -f "$COMPOSE" up -d

# Backend (FastAPI)
if [[ -f "$BACKEND_DIR/.venv/bin/uvicorn" ]]; then
  nohup "$BACKEND_DIR/.venv/bin/uvicorn" app.main:app --host 0.0.0.0 --port 8000 --reload \
    > "$ROOT/logs/backend.log" 2>&1 & echo $! > "$ROOT/pids/backend.pid"
fi

# Worker (RQ)
if [[ -f "$BACKEND_DIR/.venv/bin/rq" ]]; then
  export REDIS_URL="${REDIS_URL:-redis://127.0.0.1:6379/0}"
  nohup "$BACKEND_DIR/.venv/bin/rq" worker \
    > "$ROOT/logs/worker.log" 2>&1 & echo $! > "$ROOT/pids/worker.pid"
fi

# Frontend (Next.js)
cd "$FRONTEND_DIR"
if [[ ! -d node_modules ]]; then npm ci || npm install; fi
nohup npm run dev -- -H 0.0.0.0 -p 3000 \
  > "$ROOT/logs/frontend.log" 2>&1 & echo $! > "$ROOT/pids/frontend.pid"

echo "Started: backend:8000, worker(RQ), frontend:3000, plus Postgres/Redis via Docker."
