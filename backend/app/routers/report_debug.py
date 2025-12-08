from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.modules.reports.service import build_report_context

router = APIRouter(
    prefix="/debug/reports",
    tags=["debug-reports"],
)


@router.get("/{run_id}")
def get_debug_report_context(run_id: str, db: Session = Depends(get_db)) -> dict:
    """
    Debug endpoint to inspect the full report context structure for a run.

    This returns:
      - summary_v1
      - summary_v2
      - recommendations
      - executive_summary
      - sections (executive_summary + recommendations sections)
    """
    ctx = build_report_context(db, run_id)
    return ctx
