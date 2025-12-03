import logging
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.modules.tco.calculator import calculate_aws_tco

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/v1/tco",
    tags=["tco"],
)


@router.get("/aws/{run_id}")
def get_aws_tco(
    run_id: str,
    region: str = Query("us-east-1"),
    db: Session = Depends(get_db),
):
    """
    AWS TCO endpoint.

    Example:
      GET /v1/tco/aws/run-35073330?region=us-east-1
    """
    try:
        data = calculate_aws_tco(db, run_id, region)
        return data
    except Exception as e:
        logger.exception("Failed to calculate AWS TCO")
        # Return structured error instead of raw 500
        return {
            "error": f"Failed to calculate AWS TCO: {type(e).__name__}: {e}"
        }
