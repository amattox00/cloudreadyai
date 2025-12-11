from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.ingestion_run_v2 import IngestionRunV2
from app.modules.analysis_v2.run_summary_v2 import summarize_run_v2, RunSummaryV2

router = APIRouter(
    prefix="/v2/analysis",
    tags=["analysis v2"],
)


@router.get("/runs", response_model=List[RunSummaryV2])
def list_analysis_runs_v2(db: Session = Depends(get_db)) -> List[RunSummaryV2]:
    """
    List all v2 analysis-capable runs, with full RunSummaryV2 payload
    (totals, slices, R-Score, flags) for each.

    This is backend-only for now; the UI can later call this to power
    an “Analysis v2 Runs” table or dashboard widget.
    """
    runs = (
        db.query(IngestionRunV2)
        .order_by(IngestionRunV2.created_at.desc())
        .all()
    )

    summaries: List[RunSummaryV2] = []
    for run in runs:
        # Reuse the same logic as the single-run summary endpoint
        summary = summarize_run_v2(run_id=run.run_id, db=db)
        summaries.append(summary)

    return summaries


@router.get("/{run_id}/summary", response_model=RunSummaryV2)
def get_run_summary_v2(run_id: str, db: Session = Depends(get_db)) -> RunSummaryV2:
    """
    Return the v2 summary for a single run_id (totals, slices, R-Score, flags).
    """
    summary = summarize_run_v2(run_id=run_id, db=db)
    if summary is None:
        raise HTTPException(
            status_code=404,
            detail=f"No v2 analysis data found for run_id={run_id}",
        )
    return summary
