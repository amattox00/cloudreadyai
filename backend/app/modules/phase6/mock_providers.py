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
