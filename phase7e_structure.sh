#!/usr/bin/env bash
set -euo pipefail

ROOT="$HOME/cloudreadyai"

echo "Using ROOT: $ROOT"

# ---- Directories ----
mkdir -p "$ROOT/backend/app/modules/phase7e"
mkdir -p "$ROOT/backend/app/worker"
mkdir -p "$ROOT/backend/app/routers"
mkdir -p "$ROOT/frontend/lib/api"
mkdir -p "$ROOT/frontend/components/diagram"
mkdir -p "$ROOT/frontend/app/diagrams/enrich"

backup_if_exists() {
  local f="$1"
  if [[ -f "$f" ]]; then
    local ts
    ts=$(date +%Y%m%d-%H%M%S)
    echo "  [backup] $f -> ${f}.bak.${ts}"
    cp "$f" "${f}.bak.${ts}"
  fi
}

create_file() {
  local path="$1"
  local header="$2"
  local dir
  dir=$(dirname "$path")
  mkdir -p "$dir"
  backup_if_exists "$path"
  printf "%b" "$header" > "$path"
  echo "  [write]  $path"
}

echo "Creating Phase 7E backend files..."

create_file "$ROOT/backend/app/modules/phase7e/__init__.py" \
"# Phase 7E __init__.py\n# TODO: paste implementation from ChatGPT here.\n"

create_file "$ROOT/backend/app/modules/phase7e/models.py" \
"# Phase 7E models.py\n# TODO: paste implementation from ChatGPT here.\n"

create_file "$ROOT/backend/app/modules/phase7e/auto_layout.py" \
"# Phase 7E auto_layout.py\n# TODO: paste implementation from ChatGPT here.\n"

create_file "$ROOT/backend/app/modules/phase7e/zero_trust.py" \
"# Phase 7E zero_trust.py\n# TODO: paste implementation from ChatGPT here.\n"

create_file "$ROOT/backend/app/modules/phase7e/enrichment.py" \
"# Phase 7E enrichment.py\n# TODO: paste implementation from ChatGPT here.\n"

create_file "$ROOT/backend/app/modules/phase7e/service.py" \
"# Phase 7E service.py\n# TODO: paste implementation from ChatGPT here.\n"

create_file "$ROOT/backend/app/routers/phase7e.py" \
"# Phase 7E router\n# TODO: paste implementation from ChatGPT here.\n"

create_file "$ROOT/backend/app/worker/phase7e_tasks.py" \
"# Phase 7E worker tasks\n# TODO: paste implementation from ChatGPT here.\n"

echo "Creating Phase 7E frontend files..."

create_file "$ROOT/frontend/lib/api/diagram.ts" \
"// Phase 7E diagram API\n// TODO: paste implementation from ChatGPT here.\n"

create_file "$ROOT/frontend/components/diagram/DiagramPreview.tsx" \
"// Phase 7E DiagramPreview component\n// TODO: paste implementation from ChatGPT here.\n"

create_file "$ROOT/frontend/app/diagrams/enrich/page.tsx" \
"// Phase 7E enrichment page\n// TODO: paste implementation from ChatGPT here.\n"

echo "Done. Now open each file and paste the full code bodies."
echo "Reminder: ensure backend/app/main.py includes:  app.include_router(phase7e.router)"
