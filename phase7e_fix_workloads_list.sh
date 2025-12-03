#!/usr/bin/env bash
set -euo pipefail

echo "==[ Rewriting app/routers/workloads.py for robust /workloads/list ]=="

cd ~/cloudreadyai/backend

# 0) Activate backend venv if present
if [[ -d ".venv" ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

WORKLOAD_ROUTER="app/routers/workloads.py"

cat > "$WORKLOAD_ROUTER" << 'PYEOF'
from __future__ import annotations

from pathlib import Path
from typing import List
import json

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
    List workload JSON files known to the system from data/workloads/*.json.

    This is intentionally forgiving: it reads the raw JSON and extracts the
    basic identifying fields without re-validating as a full Workload model,
    so older or slightly different schemas don't break this endpoint.
    """
    base = _ensure_base_dir()
    items: List[WorkloadSummary] = []

    for file in sorted(base.glob("*.json")):
        try:
            obj = json.loads(file.read_text())
            wl_id = obj.get("workload_id") or file.stem
            name = obj.get("name")
            env = obj.get("environment")
            dep = obj.get("deployment_model")
            items.append(
                WorkloadSummary(
                    workload_id=wl_id,
                    name=name,
                    environment=env,
                    deployment_model=dep,
                )
            )
        except Exception:
            # Skip any malformed files instead of crashing the endpoint
            continue

    return WorkloadListResponse(items=items)
PYEOF

echo "Rewrote $WORKLOAD_ROUTER"

# 1) Compile check
python3 -m compileall "$WORKLOAD_ROUTER" >/dev/null
echo "✅ workloads router compile check passed."

