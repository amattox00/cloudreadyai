from __future__ import annotations

import os
from typing import List

import requests
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient

from .models import InstanceType, PricingQuote


def _compute_client() -> ComputeManagementClient:
    """
    Build a ComputeManagementClient using DefaultAzureCredential.

    Requires AZURE_SUBSCRIPTION_ID to be set.
    """
    subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
    if not subscription_id:
        raise RuntimeError("AZURE_SUBSCRIPTION_ID env var is required for Azure live mode")
    cred = DefaultAzureCredential(exclude_interactive_browser_credential=True)
    return ComputeManagementClient(cred, subscription_id)


def get_azure_instance_types(region: str, limit: int = 10) -> List[InstanceType]:
    """
    Use Azure ComputeManagementClient to list VM sizes for a region.

    Region should be the Azure location name, e.g. 'eastus'.
    """
    client = _compute_client()
    sizes = client.virtual_machine_sizes.list(location=region)

    items: List[InstanceType] = []
    for s in sizes:
        items.append(
            InstanceType(
                provider="azure",
                region=region,
                name=s.name,
                vcpus=int(s.number_of_cores),
                memory_gb=round(s.memory_in_mb / 1024.0, 2),
                family="unknown",  # could be parsed from name pattern later
                category="general_purpose",
            )
        )
        if len(items) >= limit:
            break

    return items


def get_azure_pricing(
    region: str,
    instance_type: str,
    hours_per_month: int,
) -> PricingQuote:
    """
    Use Azure Retail Prices public API.

    This is a best-effort query that filters by armRegionName and skuName.
    If no price is found, caller (orchestrator) in 'hybrid' mode will fall back.
    """
    base_url = "https://prices.azure.com/api/retail/prices"
    # Example filter: armRegionName eq 'eastus' and skuName eq 'Standard_D2s_v3'
    filter_str = f"armRegionName eq '{region}' and skuName eq '{instance_type}'"

    resp = requests.get(base_url, params={"$filter": filter_str}, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    items = data.get("Items", [])
    if not items:
        raise RuntimeError("No Azure retail price found")

    # Take the first matching meter
    price = float(items[0]["retailPrice"])
    currency = items[0].get("currencyCode", "USD")

    hourly = price
    monthly = round(hourly * hours_per_month, 2)

    return PricingQuote(
        provider="azure",
        region=region,
        instance_type=instance_type,
        currency=currency,
        hourly_usd=hourly,
        monthly_usd=monthly,
        source="azure_retail_prices",
    )
