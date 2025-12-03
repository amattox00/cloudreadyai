from __future__ import annotations

from typing import List

from .config import get_mode, get_supported_providers
from .models import (
    CloudProvider,
    InstanceType,
    InstanceTypeRequest,
    InstanceTypeResponse,
    PricingRequest,
    PricingResponse,
    SimpleWorkload,
    ProviderScore,
    RecommendationRequest,
    RecommendationResponse,
    FullAnalysisRequest,
    FullAnalysisResponse,
)
from . import mock_providers
from . import aws_live, azure_live, gcp_live


def list_providers() -> dict:
    return {
        "mode": get_mode(),
        "providers": get_supported_providers(),
    }


def _live_instance_types(provider: CloudProvider, region: str, limit: int) -> List[InstanceType]:
    if provider == "aws":
        return aws_live.get_aws_instance_types(region, limit=limit)
    if provider == "azure":
        return azure_live.get_azure_instance_types(region, limit=limit)
    if provider == "gcp":
        return gcp_live.get_gcp_instance_types(region, limit=limit)
    raise ValueError(f"Unsupported provider: {provider}")


def _live_pricing(
    provider: CloudProvider,
    region: str,
    instance_type: str,
    hours_per_month: int,
):
    if provider == "aws":
        return aws_live.get_aws_pricing(region, instance_type, hours_per_month)
    if provider == "azure":
        return azure_live.get_azure_pricing(region, instance_type, hours_per_month)
    if provider == "gcp":
        return gcp_live.get_gcp_pricing(region, instance_type, hours_per_month)
    raise ValueError(f"Unsupported provider: {provider}")


def get_instance_types(req: InstanceTypeRequest) -> InstanceTypeResponse:
    mode = get_mode()
    items: List[InstanceType]

    if mode == "mock":
        items = mock_providers.get_mock_instance_types(req.provider, req.region, req.limit)
    elif mode in ("live", "hybrid"):
        try:
            items = _live_instance_types(req.provider, req.region, req.limit)
        except Exception:
            if mode == "hybrid":
                items = mock_providers.get_mock_instance_types(req.provider, req.region, req.limit)
            else:
                raise
    else:
        items = mock_providers.get_mock_instance_types(req.provider, req.region, req.limit)

    return InstanceTypeResponse(items=items)


def get_pricing(req: PricingRequest) -> PricingResponse:
    mode = get_mode()

    if mode == "mock":
        quote = mock_providers.get_mock_pricing(
            req.provider, req.region, req.instance_type, req.hours_per_month
        )
    elif mode in ("live", "hybrid"):
        try:
            quote = _live_pricing(
                req.provider, req.region, req.instance_type, req.hours_per_month
            )
        except Exception:
            if mode == "hybrid":
                quote = mock_providers.get_mock_pricing(
                    req.provider, req.region, req.instance_type, req.hours_per_month
                )
            else:
                raise
    else:
        quote = mock_providers.get_mock_pricing(
            req.provider, req.region, req.instance_type, req.hours_per_month
        )

    return PricingResponse(quote=quote)


def _score_provider(
    provider: CloudProvider,
    workload: SimpleWorkload,
) -> ProviderScore:
    # Very simple scoring logic: just use mock pricing and a provider bias.
    base_instance_type = "general-medium"

    mock_quote = mock_providers.get_mock_pricing(
        provider=provider,
        region="default-region",
        instance_type=base_instance_type,
        hours_per_month=730,
    )

    bias = {
        "aws": 1.0,
        "azure": 0.98,
        "gcp": 0.97,
    }.get(provider, 1.0)

    score = 100.0 * bias

    rationale = (
        f"Mock score for {provider.upper()} based on baseline pricing and simple bias. "
        f"Workload: {workload.total_vcpus} vCPUs, {workload.total_memory_gb} GiB RAM."
    )

    return ProviderScore(
        provider=provider,
        score=round(score, 2),
        estimated_monthly_usd=mock_quote.monthly_usd,
        rationale=rationale,
    )


def recommend(req: RecommendationRequest) -> RecommendationResponse:
    providers = req.candidate_providers or get_supported_providers()
    scores = sorted(
        (_score_provider(p, req.workload) for p in providers),
        key=lambda s: s.score,
        reverse=True,
    )
    chosen = scores[0].provider
    return RecommendationResponse(chosen=chosen, scores=scores)


def full_analysis(req: FullAnalysisRequest) -> FullAnalysisResponse:
    recommendation = recommend(
        RecommendationRequest(
            candidate_providers=req.candidate_providers,
            workload=req.workload,
        )
    )

    # Use the chosen provider to fetch some instance samples in the default region
    inst_req = InstanceTypeRequest(
        provider=recommendation.chosen,
        region="default-region",
        limit=3,
    )
    inst_resp = get_instance_types(inst_req)

    return FullAnalysisResponse(
        recommendation=recommendation,
        instance_samples=inst_resp.items,
    )
