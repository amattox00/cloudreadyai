from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# IMPORTANT:
# This router is the original in-memory run registry used by the Dashboard.
# It MUST stay under /v1/run_registry because the frontend depends on that.
router = APIRouter(
    prefix="/v1/run_registry",
    tags=["runs"],
)


class RunCreate(BaseModel):
    """
    Payload used when creating a new run from the Dashboard or API.
    """
    name: str
    source: str


class RunSummary(BaseModel):
    """
    Placeholder summary for Phase C. Always safe to return.
    """
    underutilized_servers: int = 0
    overprovisioned_ram_pct: float = 0.0
    hot_network_segments: int = 0
    rightsizing_candidates: int = 0
    notes: Optional[str] = (
        "Phase C placeholder — connect to analysis engine later."
    )


class RunRecord(BaseModel):
    """
    In-memory representation of a CloudReadyAI assessment run.
    """
    id: str
    created_at: datetime
    name: str
    source: str
    state: str = "created"

    servers_ingested: int = 0
    storage_ingested: int = 0
    network_ingested: int = 0

    summary: Optional[RunSummary] = None


# In-memory store.
_RUN_REGISTRY: Dict[str, RunRecord] = {}


def _new_run_id() -> str:
    now = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    return f"run-{now[-8:]}"


def increment_ingest_counts(
    run_id: str,
    servers: int = 0,
    storage: int = 0,
    network: int = 0,
) -> None:
    if not run_id:
        return

    record = _RUN_REGISTRY.get(run_id)
    if not record:
        return

    record.servers_ingested += max(servers, 0)
    record.storage_ingested += max(storage, 0)
    record.network_ingested += max(network, 0)


@router.post("", response_model=RunRecord)
def create_run(payload: RunCreate) -> RunRecord:
    """
    Dashboard 'Start Assessment' uses this endpoint.
    It MUST return an object with field 'id'.
    """
    run_id = _new_run_id()
    record = RunRecord(
        id=run_id,
        created_at=datetime.utcnow(),
        name=payload.name,
        source=payload.source,
        state="created",
        summary=RunSummary(),
    )
    _RUN_REGISTRY[run_id] = record
    return record


@router.get("", response_model=List[RunRecord])
def list_runs() -> List[RunRecord]:
    return sorted(_RUN_REGISTRY.values(), key=lambda r: r.created_at, reverse=True)


@router.get("/{run_id}", response_model=RunRecord)
def get_run(run_id: str) -> RunRecord:
    record = _RUN_REGISTRY.get(run_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")
    return record


@router.delete("/{run_id}")
def delete_run(run_id: str) -> dict:
    if run_id not in _RUN_REGISTRY:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")
    del _RUN_REGISTRY[run_id]
    return {"ok": True, "deleted_run_id": run_id}


# NEW — Summary endpoint for Workloads tab
@router.get("/{run_id}/summary", response_model=RunSummary)
def get_run_summary(run_id: str) -> RunSummary:
    """
    Always return a summary object (fallback if needed).
    Prevents 'Failed to fetch' errors in the Workloads tab.
    """
    record = _RUN_REGISTRY.get(run_id)
    if record and record.summary:
        return record.summary

    # Always safe fallback
    return RunSummary()
