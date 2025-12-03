from __future__ import annotations

from pathlib import Path
from typing import List
import json

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.workload import Workload


router = APIRouter(tags=["workloads"])

# Resolve base directory relative to backend root so it works
# both under systemd (CWD=/) and when run from the backend folder.
# __file__ = .../backend/app/routers/workloads.py
# parents[0] = routers, [1] = app, [2] = backend
BACKEND_ROOT = Path(__file__).resolve().parents[2]
BASE_DIR = BACKEND_ROOT / "data" / "workloads"


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
    (anchored at backend root).
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
    List workload JSON files known to the system from backend/data/workloads/*.json.

    This reads raw JSON and extracts basic identifying fields without re-validating
    as a full Workload model, so older or slightly different schemas don't break
    this endpoint.
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
            # Skip malformed files instead of crashing the endpoint
            continue

    return WorkloadListResponse(items=items)
