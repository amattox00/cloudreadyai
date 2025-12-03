# app/routers/run_details.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.run_metrics import RunSliceMetrics

router = APIRouter(prefix="/v1/runs", tags=["runs"])


@router.get("/{run_id}/details")
def get_run_details(run_id: str, db: Session = Depends(get_db)):
    """
    Return a simple aggregated view of a run based ONLY on run_slice_metrics.

    This keeps us independent of the existing ingestion_runs schema.
    """

    # Fetch all slice metrics for this run
    slice_rows = (
        db.query(RunSliceMetrics)
        .filter(RunSliceMetrics.run_id == run_id)
        .order_by(RunSliceMetrics.slice_name)
        .all()
    )

    # If there are no slice metrics, we consider the run missing
    if not slice_rows:
        raise HTTPException(status_code=404, detail="Run not found")

    slices = []
    for s in slice_rows:
        slices.append(
            {
                "slice_name": s.slice_name,
                "row_count": s.row_count,
                "metrics": s.metrics_json or {},
                "created_at": s.created_at.isoformat() if getattr(s, "created_at", None) else None,
            }
        )

    return {
        "run_id": run_id,
        "slices": slices,
    }
