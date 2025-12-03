from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.analysis import AnalysisRunSummary
from app.modules.analysis.engine.orchestrator import run_full_analysis

router = APIRouter(
    prefix="/analysis",
    tags=["analysis"],
)


@router.post("/{run_id}/start", response_model=AnalysisRunSummary)
def start_analysis(run_id: str, db: Session = Depends(get_db)) -> AnalysisRunSummary:
    """
    Run the analysis pipeline for this run_id and return the summary.

    For now, this is stateless: we compute the summary on the fly
    and do NOT depend on the analysis_run table.
    """
    summary = run_full_analysis(run_id, db)
    return summary


@router.get("/{run_id}/summary", response_model=AnalysisRunSummary)
def get_summary(run_id: str, db: Session = Depends(get_db)) -> AnalysisRunSummary:
    """
    Return the current analysis summary for this run_id.

    For MVP, this recomputes the summary on demand, using the
    same engine as /start. Later we can add persistence to
    analysis_run if needed.
    """
    summary = run_full_analysis(run_id, db)
    return summary
