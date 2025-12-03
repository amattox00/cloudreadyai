from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/cost", tags=["cost"])


class CostEstimateRequest(BaseModel):
    # All fields optional so we never 422 for missing data
    cloud: Optional[str] = None
    workload_name: Optional[str] = None
    environment: Optional[str] = None
    region: Optional[str] = None
    monthly_budget: Optional[float] = None


class CostItem(BaseModel):
    service: str
    monthly_cost: float


class CostEstimateResponse(BaseModel):
    cloud: str
    monthly_total: float
    breakdown: List[CostItem]
    warnings: Optional[List[str]] = None


@router.post("/estimate", response_model=CostEstimateResponse)
async def estimate_cost(req: CostEstimateRequest) -> CostEstimateResponse:
    """
    Phase A placeholder cost estimator.

    Design goals:
    - Never return 422 for "normal" JSON input
    - Avoid 500s by catching internal errors
    - Always return:
      - cloud
      - monthly_total
      - breakdown[]
    """
    warnings: List[str] = []

    try:
        cloud = (req.cloud or "unknown").lower()

        if cloud == "aws":
            breakdown = [
                CostItem(service="EC2", monthly_cost=60.0),
                CostItem(service="RDS", monthly_cost=30.0),
                CostItem(service="S3", monthly_cost=10.0),
            ]
        elif cloud == "azure":
            breakdown = [
                CostItem(service="VM", monthly_cost=55.0),
                CostItem(service="Azure SQL", monthly_cost=35.0),
                CostItem(service="Blob Storage", monthly_cost=10.0),
            ]
        elif cloud == "gcp":
            breakdown = [
                CostItem(service="GCE", monthly_cost=50.0),
                CostItem(service="Cloud SQL", monthly_cost=40.0),
                CostItem(service="GCS", monthly_cost=10.0),
            ]
        else:
            breakdown = [
                CostItem(service="compute", monthly_cost=70.0),
                CostItem(service="database", monthly_cost=20.0),
                CostItem(service="storage", monthly_cost=10.0),
            ]
            warnings.append(
                f"Unknown cloud '{req.cloud}'; using generic placeholder costs."
            )

        monthly_total = sum(item.monthly_cost for item in breakdown)

    except Exception:
        logger.exception("Cost estimator failed; returning safe defaults")
        breakdown = []
        monthly_total = 0.0
        cloud = (req.cloud or "unknown").lower()
        warnings.append("Estimator failed internally; returning zero costs.")

    return CostEstimateResponse(
        cloud=cloud,
        monthly_total=monthly_total,
        breakdown=breakdown,
        warnings=warnings or None,
    )
