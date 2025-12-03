#!/usr/bin/env bash
set -euo pipefail

echo "==[ Phase 6 – Cloud Intelligence Engine 2.0 Install ]=="

BACKEND_DIR="$HOME/cloudreadyai/backend"

cd "$BACKEND_DIR"

# 0) Activate venv if present
if [[ -d ".venv" ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

mkdir -p app/modules/phase6

########################################
# app/modules/phase6/config.py
########################################
cat > app/modules/phase6/config.py << 'PYEOF'
from __future__ import annotations

import os
from typing import List

# Default to "hybrid": try live where implemented, fall back to mock
PHASE6_MODE: str = os.getenv("PHASE6_MODE", "hybrid").lower()

SUPPORTED_PROVIDERS: List[str] = ["aws", "azure", "gcp"]


def get_mode() -> str:
    """Return the current Phase 6 mode."""
    return PHASE6_MODE


def get_supported_providers() -> list[str]:
    """Return supported cloud providers."""
    return SUPPORTED_PROVIDERS
PYEOF

########################################
# app/modules/phase6/models.py
########################################
cat > app/modules/phase6/models.py << 'PYEOF'
from __future__ import annotations

from typing import List, Optional, Literal

from pydantic import BaseModel, Field


CloudProvider = Literal["aws", "azure", "gcp"]


class InstanceType(BaseModel):
    provider: CloudProvider
    region: str
    name: str
    vcpus: int = Field(..., ge=1)
    memory_gb: float = Field(..., gt=0)
    family: str
    category: str


class InstanceTypeRequest(BaseModel):
    provider: CloudProvider
    region: str
    limit: int = Field(10, ge=1, le=100)


class InstanceTypeResponse(BaseModel):
    items: List[InstanceType]


class PricingRequest(BaseModel):
    provider: CloudProvider
    region: str
    instance_type: str
    hours_per_month: int = Field(730, ge=1, le=744)


class PricingQuote(BaseModel):
    provider: CloudProvider
    region: str
    instance_type: str
    currency: str = "USD"
    hourly_usd: float
    monthly_usd: float
    source: str  # "mock", "aws_pricing_api", "azure_retail_prices", "gcp_billing_catalog"


class PricingResponse(BaseModel):
    quote: PricingQuote


class SimpleWorkload(BaseModel):
    total_vcpus: int = Field(..., ge=1)
    total_memory_gb: float = Field(..., gt=0)
    environment: str = "prod"
    criticality: str = "normal"  # "normal", "high", "mission_critical"


class RecommendationRequest(BaseModel):
    candidate_providers: Optional[List[CloudProvider]] = None
    workload: SimpleWorkload


class ProviderScore(BaseModel):
    provider: CloudProvider
    score: float
    estimated_monthly_usd: float
    rationale: str


class RecommendationResponse(BaseModel):
    chosen: CloudProvider
    scores: List[ProviderScore]


class FullAnalysisRequest(BaseModel):
    workload: SimpleWorkload
    candidate_providers: Optional[List[CloudProvider]] = None


class FullAnalysisResponse(BaseModel):
    recommendation: RecommendationResponse
    instance_samples: List[InstanceType]
PYEOF

########################################
# app/modules/phase6/mock_providers.py
########################################
cat > app/modules/phase6/mock_providers.py << 'PYEOF'
from __future__ import annotations

from typing import List

from .models import InstanceType, PricingQuote, CloudProvider


def get_mock_instance_types(
    provider: CloudProvider,
    region: str,
    limit: int = 10,
) -> List[InstanceType]:
    """Return a small, hard-coded catalog of instance types for mock/hybrid mode."""
    base: list[InstanceType] = []

    if provider == "aws":
        base = [
            InstanceType(
                provider="aws",
                region=region,
                name="t3.small",
                vcpus=2,
                memory_gb=2.0,
                family="t3",
                category="general_purpose",
            ),
            InstanceType(
                provider="aws",
                region=region,
                name="t3.medium",
                vcpus=2,
                memory_gb=4.0,
                family="t3",
                category="general_purpose",
            ),
            InstanceType(
                provider="aws",
                region=region,
                name="m6i.large",
                vcpus=2,
                memory_gb=8.0,
                family="m6i",
                category="general_purpose",
            ),
        ]
    elif provider == "azure":
        base = [
            InstanceType(
                provider="azure",
                region=region,
                name="Standard_B2ms",
                vcpus=2,
                memory_gb=8.0,
                family="B-series",
                category="general_purpose",
            ),
            InstanceType(
                provider="azure",
                region=region,
                name="Standard_D2s_v3",
                vcpus=2,
                memory_gb=8.0,
                family="Dsv3",
                category="general_purpose",
            ),
        ]
    elif provider == "gcp":
        base = [
            InstanceType(
                provider="gcp",
                region=region,
                name="e2-medium",
                vcpus=2,
                memory_gb=4.0,
                family="e2",
                category="general_purpose",
            ),
            InstanceType(
                provider="gcp",
                region=region,
                name="n2-standard-4",
                vcpus=4,
                memory_gb=16.0,
                family="n2",
                category="general_purpose",
            ),
        ]

    return base[:limit]


def get_mock_pricing(
    provider: CloudProvider,
    region: str,
    instance_type: str,
    hours_per_month: int,
) -> PricingQuote:
    """Return a simple mock pricing record, tuned by provider."""
    base_hourly: float

    if provider == "aws":
        base_hourly = 0.08
    elif provider == "azure":
        base_hourly = 0.085
    else:  # gcp
        base_hourly = 0.075

    monthly = round(base_hourly * hours_per_month, 2)
    return PricingQuote(
        provider=provider,
        region=region,
        instance_type=instance_type,
        currency="USD",
        hourly_usd=base_hourly,
        monthly_usd=monthly,
        source="mock",
    )
PYEOF

########################################
# app/modules/phase6/aws_live.py
########################################
cat > app/modules/phase6/aws_live.py << 'PYEOF'
from __future__ import annotations

from typing import List

from .models import InstanceType, PricingQuote, CloudProvider


def get_aws_instance_types(region: str, limit: int = 10) -> List[InstanceType]:
    """
    Placeholder for real AWS integration.
    Currently raises NotImplementedError; orchestrator will catch and fall back to mock
    when running in 'hybrid' mode.
    """
    raise NotImplementedError("AWS live instance type lookup not yet implemented.")


def get_aws_pricing(
    region: str,
    instance_type: str,
    hours_per_month: int,
) -> PricingQuote:
    """
    Placeholder for real AWS Pricing API integration.
    Currently raises NotImplementedError; orchestrator will fall back to mock in 'hybrid' mode.
    """
    raise NotImplementedError("AWS live pricing lookup not yet implemented.")
PYEOF

########################################
# app/modules/phase6/azure_live.py
########################################
cat > app/modules/phase6/azure_live.py << 'PYEOF'
from __future__ import annotations

from typing import List

from .models import InstanceType, PricingQuote


def get_azure_instance_types(region: str, limit: int = 10) -> List[InstanceType]:
    """
    Placeholder for Azure retail prices / SKU query.
    Raises NotImplementedError; orchestrator will fall back to mock in 'hybrid' mode.
    """
    raise NotImplementedError("Azure live instance type lookup not yet implemented.")


def get_azure_pricing(
    region: str,
    instance_type: str,
    hours_per_month: int,
) -> PricingQuote:
    """
    Placeholder for Azure retail pricing integration.
    """
    raise NotImplementedError("Azure live pricing lookup not yet implemented.")
PYEOF

########################################
# app/modules/phase6/gcp_live.py
########################################
cat > app/modules/phase6/gcp_live.py << 'PYEOF'
from __future__ import annotations

from typing import List

from .models import InstanceType, PricingQuote


def get_gcp_instance_types(region: str, limit: int = 10) -> List[InstanceType]:
    """
    Placeholder for GCP Cloud Billing catalog / machine types.
    Raises NotImplementedError; orchestrator will fall back to mock in 'hybrid' mode.
    """
    raise NotImplementedError("GCP live instance type lookup not yet implemented.")


def get_gcp_pricing(
    region: str,
    instance_type: str,
    hours_per_month: int,
) -> PricingQuote:
    """
    Placeholder for GCP Cloud Billing pricing integration.
    """
    raise NotImplementedError("GCP live pricing lookup not yet implemented.")
PYEOF

########################################
# app/modules/phase6/orchestrator.py
########################################
cat > app/modules/phase6/orchestrator.py << 'PYEOF'
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
PYEOF

########################################
# app/modules/phase6/__init__.py
########################################
cat > app/modules/phase6/__init__.py << 'PYEOF'
from __future__ import annotations

from .config import PHASE6_MODE, SUPPORTED_PROVIDERS, get_mode, get_supported_providers  # noqa: F401
from . import orchestrator, models, mock_providers, aws_live, azure_live, gcp_live  # noqa: F401

__all__ = [
    "PHASE6_MODE",
    "SUPPORTED_PROVIDERS",
    "get_mode",
    "get_supported_providers",
    "orchestrator",
    "models",
    "mock_providers",
    "aws_live",
    "azure_live",
    "gcp_live",
]
PYEOF

########################################
# app/routers/phase6.py
########################################
cat > app/routers/phase6.py << 'PYEOF'
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
PYEOF

########################################
# Compile check
########################################
echo "Running python compile check for Phase 6 modules..."
python3 -m compileall app/modules/phase6 app/routers/phase6.py

echo "==[ Phase 6 install completed successfully ]=="
