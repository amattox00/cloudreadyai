from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.modules.normalization.servers import normalize_servers_for_run

router = APIRouter(tags=["normalization"])


@router.post("/v1/runs/{run_id}/normalize/servers")
def normalize_run_servers(run_id: str, db: Session = Depends(get_db)):
    """
    Normalize server metadata (OS, environment, RAM fields) for a given run.
    Safe to call multiple times (idempotent).
    """
    summary = normalize_servers_for_run(db, run_id)

    if summary["rows_seen"] == 0:
        raise HTTPException(status_code=404, detail=f"No servers found for run {run_id}")

    return summary
