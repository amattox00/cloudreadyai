from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.modules.analysis_v2.recommendations_engine_v2 import (
    RecommendationsBundleV2,
    generate_recommendations_for_run,
)

router = APIRouter(
    prefix="/v2/recommendations",
    tags=["recommendations v2"],
)


@router.get("/{run_id}", response_model=RecommendationsBundleV2)
def get_recommendations_v2(
    run_id: str,
    db: Session = Depends(get_db),
) -> RecommendationsBundleV2:
    """
    Generate recommendations for the given run_id using v2 analysis data
    (RunSummaryV2 + R-Score + flags) and the selected analysis profile.

    This endpoint is read-only and does not modify any state.
    """
    bundle = generate_recommendations_for_run(run_id=run_id, db=db)
    if bundle is None:
        raise HTTPException(
            status_code=404,
            detail=f"No v2 analysis data found for run_id={run_id}",
        )
    return bundle
