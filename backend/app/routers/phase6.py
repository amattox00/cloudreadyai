from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.modules.phase6 import orchestrator
from app.modules.phase6.models import (
    InstanceTypeRequest,
    InstanceTypeResponse,
    PricingRequest,
    PricingResponse,
    RecommendationRequest,
    RecommendationResponse,
    FullAnalysisRequest,
    FullAnalysisResponse,
)

router = APIRouter(prefix="/v1/phase6", tags=["phase6"])


@router.get("/providers")
def get_providers() -> dict:
    """Return current Phase 6 mode and supported providers."""
    return orchestrator.list_providers()


@router.post("/instance-types", response_model=InstanceTypeResponse)
def post_instance_types(req: InstanceTypeRequest) -> InstanceTypeResponse:
    try:
        return orchestrator.get_instance_types(req)
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/pricing", response_model=PricingResponse)
def post_pricing(req: PricingRequest) -> PricingResponse:
    try:
        return orchestrator.get_pricing(req)
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/recommend", response_model=RecommendationResponse)
def post_recommend(req: RecommendationRequest) -> RecommendationResponse:
    try:
        return orchestrator.recommend(req)
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/full-analysis", response_model=FullAnalysisResponse)
def post_full_analysis(req: FullAnalysisRequest) -> FullAnalysisResponse:
    try:
        return orchestrator.full_analysis(req)
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=str(exc)) from exc
