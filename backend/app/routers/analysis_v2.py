from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.modules.analysis_v2.run_views_servers_v2 import (
    build_analysis_summary,
    build_recommendations,
)
from app.schemas.analysis import AnalysisSummary, RecommendationsResponse


router = APIRouter(
    prefix="/v1/analysis",
    tags=["analysis_v2"],
)


@router.get("/{run_id}/summary", response_model=AnalysisSummary)
def get_analysis_summary(run_id: str, db: Session = Depends(get_db)) -> AnalysisSummary:
    summary = build_analysis_summary(db, run_id)
    if summary.total_servers == 0:
        raise HTTPException(
            status_code=404,
            detail=f"No servers found for run_id={run_id}",
        )
    return summary


@router.get("/{run_id}/recommendations", response_model=RecommendationsResponse)
def get_recommendations(
    run_id: str, db: Session = Depends(get_db)
) -> RecommendationsResponse:
    recs = build_recommendations(db, run_id)
    if recs.total_recommendations == 0:
        raise HTTPException(
            status_code=404,
            detail=f"No servers found for run_id={run_id}",
        )
    return recs
