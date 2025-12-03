from __future__ import annotations

import os
from typing import List

from google.cloud import compute_v1
from google.cloud import billing_v1

from .models import InstanceType, PricingQuote


def get_gcp_instance_types(region: str, limit: int = 10) -> List[InstanceType]:
    """
    Use the GCP Compute Engine API to list machine types for a region.

    Region example: 'us-central1'. We'll query one zone in that region (e.g. us-central1-a).
    """
    # Default to 'a' zone in the region
    zone = f"{region}-a"
    client = compute_v1.MachineTypesClient()

    request = compute_v1.ListMachineTypesRequest(project=_get_gcp_project_id(), zone=zone)
    pager = client.list(request=request)

    items: List[InstanceType] = []
    for mt in pager:
        items.append(
            InstanceType(
                provider="gcp",
                region=region,
                name=mt.name,
                vcpus=int(mt.guest_cpus),
                memory_gb=round(mt.memory_mb / 1024.0, 2),
                family="unknown",  # could be parsed from name later
                category="general_purpose",
            )
        )
        if len(items) >= limit:
            break

    return items


def _get_gcp_project_id() -> str:
    project_id = os.getenv("GCP_PROJECT_ID")
    if not project_id:
        raise RuntimeError("GCP_PROJECT_ID env var is required for GCP live mode")
    return project_id


def get_gcp_pricing(
    region: str,
    instance_type: str,
    hours_per_month: int,
) -> PricingQuote:
    """
    Use Cloud Billing Catalog to fetch pricing for a given machine type.

    This is a best-effort implementation that looks for a matching SKU
    containing the machine type name and region in the description.
    """
    client = billing_v1.CloudCatalogClient()

    # Compute Engine service name from Cloud Billing
    service_name = "services/6F81-5844-456A"  # documented ID for Compute Engine
    skus = client.list_skus(parent=service_name)

    hourly = None
    currency = "USD"

    target_region = region.replace("-", " ").title()

    for sku in skus:
        desc = sku.description or ""
        if instance_type in desc and target_region in desc:
            if not sku.pricing_info:
                continue
            pricing_expr = sku.pricing_info[0].pricing_expression
            if not pricing_expr.tiered_rates:
                continue
            unit_price = pricing_expr.tiered_rates[0].unit_price
            # unit_price is a Money {units, nanos}
            hourly = unit_price.units + (unit_price.nanos / 1e9)
            currency = unit_price.currency_code or "USD"
            break

    if hourly is None:
        raise RuntimeError("No matching GCP SKU found for pricing")

    monthly = round(hourly * hours_per_month, 2)

    return PricingQuote(
        provider="gcp",
        region=region,
        instance_type=instance_type,
        currency=currency,
        hourly_usd=hourly,
        monthly_usd=monthly,
        source="gcp_billing_catalog",
    )
