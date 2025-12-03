from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from ...cost.calculator import CostCalculator, WorkloadInput, Scenario
from ...cost.pricing import PricingCatalog

router = APIRouter(prefix="/v1/cost", tags=["cost"])

class Workload(BaseModel):
    name: str
    cloud: str
    region: str = "any"
    vcpu: int = Field(gt=0)
    memory_gib: float = Field(gt=0)
    storage_gib: float = Field(ge=0)
    storage_class: str = "standard"
    hours_per_month: int = 730
    egress_gib: float = 0.0
    ha_multiplier: float = 1.0
    dr_multiplier: float = 1.0

class ScenarioIn(BaseModel):
    name: str
    commitment: Optional[str] = None
    rightsize_factor: float = 1.0
    burst_percent: float = 0.0
    notes: Optional[str] = None

class RequestBody(BaseModel):
    workloads: List[Workload]
    scenario: ScenarioIn

@router.post("/estimate")
def estimate(req: RequestBody):
    try:
        pricing = PricingCatalog()
        calc = CostCalculator(pricing)
        workloads = [WorkloadInput(**w.dict()) for w in req.workloads]
        scenario = Scenario(**req.scenario.dict())
        return calc.estimate_scenario(workloads, scenario)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ---- Phase 4 cost estimate API compatibility shim ----
# This ensures /v1/cost/estimate exists even if earlier code paths differ.

from typing import Any, Dict, List
from fastapi import APIRouter
from pydantic import BaseModel

# Reuse existing router if already defined; otherwise create one
try:
    router  # type: ignore[name-defined]
except NameError:  # pragma: no cover
    router = APIRouter()

class WorkloadItem(BaseModel):
    name: str
    vcpus: int
    memory_gb: float
    hours_per_month: float

class CostEstimateRequest(BaseModel):
    provider: str
    region: str
    workloads: List[WorkloadItem]

@router.post("/estimate")
async def estimate_cost_api(payload: CostEstimateRequest) -> Dict[str, Any]:
    """
    Minimal Phase 4-compatible endpoint.

    For now this returns a stubbed response that proves the API is wired correctly.
    We can later wire this into app.cost.calculator if we want full logic here.
    """
    total_hours = sum(w.hours_per_month for w in payload.workloads)
    return {
        "status": "ok",
        "provider": payload.provider,
        "region": payload.region,
        "workloads_count": len(payload.workloads),
        "total_hours": total_hours,
        "note": "Phase 4 compatibility shim; pricing logic can be plugged in later.",
    }
