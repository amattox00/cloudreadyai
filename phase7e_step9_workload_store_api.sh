#!/usr/bin/env bash
set -euo pipefail

echo "==[ Step 9: Backend Workload Store API (save + list) ]=="

cd ~/cloudreadyai/backend

# 0) Activate backend venv if present
if [[ -d ".venv" ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

WORKLOAD_ROUTER="app/routers/workloads.py"

# 1) Create workloads.py router
cat > "$WORKLOAD_ROUTER" << 'PYEOF'
from __future__ import annotations

from pathlib import Path
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.workload import Workload


router = APIRouter(tags=["workloads"])

BASE_DIR = Path("data/workloads")


class WorkloadSummary(BaseModel):
    workload_id: str
    name: str | None = None
    environment: str | None = None
    deployment_model: str | None = None


class WorkloadSaveRequest(BaseModel):
    workload: Workload


class WorkloadSaveResponse(BaseModel):
    workload_id: str
    path: str


class WorkloadListResponse(BaseModel):
    items: List[WorkloadSummary]


def _ensure_base_dir() -> Path:
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    return BASE_DIR


@router.post("/workloads/save", response_model=WorkloadSaveResponse)
def save_workload(payload: WorkloadSaveRequest) -> WorkloadSaveResponse:
    """
    Save (or overwrite) a Workload JSON under data/workloads/{workload_id}.json

    This is the primary entry point for Phase 3 / Phase 8 ingestion to
    publish canonical workloads for Diagram Generator 2.0.
    """
    base = _ensure_base_dir()
    wl = payload.workload

    if not wl.workload_id:
        raise HTTPException(status_code=400, detail="Workload must have a workload_id.")

    path = base / f"{wl.workload_id}.json"
    path.write_text(wl.model_dump_json(indent=2))

    return WorkloadSaveResponse(
        workload_id=wl.workload_id,
        path=str(path),
    )


@router.get("/workloads/list", response_model=WorkloadListResponse)
def list_workloads() -> WorkloadListResponse:
    """
    List workload JSON files known to the system from data/workloads/*.json
    """
    base = _ensure_base_dir()
    items: List[WorkloadSummary] = []

    for file in sorted(base.glob("*.json")):
        try:
            data = file.read_text()
            wl = Workload.model_validate_json(data)
            items.append(
                WorkloadSummary(
                    workload_id=wl.workload_id,
                    name=wl.name,
                    environment=wl.environment,
                    deployment_model=wl.deployment_model,
                )
            )
        except Exception:
            # Skip any malformed files instead of crashing the endpoint
            continue

    return WorkloadListResponse(items=items)
PYEOF

echo "Created $WORKLOAD_ROUTER"

# 2) Compile check
python3 -m compileall "$WORKLOAD_ROUTER" >/dev/null
echo "✅ Router compile check passed."

# 3) Wire router into app/main.py
MAIN_FILE="app/main.py"
if [[ ! -f "$MAIN_FILE" ]]; then
  echo "ERROR: $MAIN_FILE not found. Please adjust MAIN_FILE path in the script."
  exit 1
fi

# 3a) Add import if missing
if ! grep -q "from app.routers import workloads" "$MAIN_FILE"; then
  echo "Adding import for workloads router to $MAIN_FILE"
  echo "from app.routers import workloads" >> "$MAIN_FILE"
else
  echo "workloads import already present in $MAIN_FILE"
fi

# 3b) Include router if missing
if ! grep -q "workloads.router" "$MAIN_FILE"; then
  echo "Adding app.include_router(...) for workloads to $MAIN_FILE"
  echo "app.include_router(workloads.router, prefix=\"/v1\")" >> "$MAIN_FILE"
else
  echo "workloads router already included in $MAIN_FILE"
fi

echo "✅ main.py updated for workloads router."

# 4) Quick in-process tests (no HTTP)

python3 - << 'PY'
from pathlib import Path
from app.models.workload import Workload, Node, Edge, Platform, BusinessMetadata
from app.routers.workloads import save_workload, list_workloads, WorkloadSaveRequest

print("Creating a demo workload and saving via save_workload()...")

demo_wl = Workload(
    workload_id="wl-demo-phase7e",
    name="Demo Workload Phase7E",
    description="Demo workload created by Step 9 test",
    environment="dev",
    deployment_model="single_cloud",
    business=BusinessMetadata(
        owner="Cloud Engineering",
        criticality="medium",
        industry="Demo",
        tags=["demo"],
    ),
    nodes=[
        Node(
            node_id="n1",
            name="Demo App",
            role="app",
            layer="application",
            technology_type="vm",
            platform=Platform(location="aws", service_hint="ec2"),
        )
    ],
    edges=[],
)

resp = save_workload(WorkloadSaveRequest(workload=demo_wl))
print("Saved workload:", resp.workload_id, "->", resp.path)

print("Listing workloads...")
lst = list_workloads()
for item in lst.items:
    print(" -", item.workload_id, "|", item.name, "|", item.environment, "|", item.deployment_model)
PY

echo "✅ Step 9 tests completed."

