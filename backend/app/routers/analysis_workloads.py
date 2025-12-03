from typing import List, Literal

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/v1", tags=["analysis"])

RiskLevel = Literal["low", "medium", "high", "unknown"]
WorkloadCategory = Literal[
    "compute",
    "database",
    "storage",
    "network",
    "application",
    "other",
]


class WorkloadSummary(BaseModel):
    workload_id: str
    name: str
    category: WorkloadCategory
    server_count: int
    app_count: int
    storage_gb: float
    monthly_cost_estimate: float
    risk_level: RiskLevel
    recommendation: str


@router.get(
    "/runs/{run_id}/analysis/workloads",
    response_model=List[WorkloadSummary],
    summary="Temporary stub: workload analysis for a run",
)
def list_workloads_for_run(run_id: str) -> List[WorkloadSummary]:
    """
    TEMPORARY STUB ENDPOINT

    This avoids hitting the database and just returns a placeholder
    workload so the frontend Analysis page has something to render
    without 500s. We'll wire this to real data later.
    """
    return [
        WorkloadSummary(
            workload_id=f"{run_id}-sample-1",
            name="Sample Workload",
            category="compute",
            server_count=0,
            app_count=0,
            storage_gb=0.0,
            monthly_cost_estimate=0.0,
            risk_level="unknown",
            recommendation="Ingestion not yet wired – placeholder analysis only.",
        )
    ]
