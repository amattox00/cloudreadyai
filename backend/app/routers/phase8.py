from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os

from app.modules.phase8 import CostModeler, list_scenarios, get_scenario, ScenarioResult
from app.modules.phase8.modeling import EstimateRequest, EstimateResult

router = APIRouter(prefix="/v1/model", tags=["phase8-modeling"])

class WhatIfRequest(BaseModel):
    scenario: str

@router.get("/health")
def model_health():
    return {
        "phase": 8,
        "enabled": os.getenv("PHASE8_ENABLED", "true").lower() == "true",
        "mode": os.getenv("PHASE8_MODE", "mock"),
    }

@router.get("/scenarios", response_model=list[ScenarioResult])
def model_scenarios():
    return list_scenarios()

@router.post("/estimate", response_model=EstimateResult)
def model_estimate(req: EstimateRequest):
    modeler = CostModeler()
    return modeler.estimate(req)

@router.post("/whatif", response_model=ScenarioResult)
def model_whatif(req: WhatIfRequest):
    try:
        return get_scenario(req.scenario)  # type: ignore
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
