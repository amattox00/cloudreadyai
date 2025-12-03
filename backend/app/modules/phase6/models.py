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
