#!/usr/bin/env bash
set -euo pipefail

echo "==[ Phase 6 – Enable Live AWS/Azure/GCP Integrations ]=="

BACKEND_DIR="$HOME/cloudreadyai/backend"

cd "$BACKEND_DIR"

# 0) Activate venv if present
if [[ -d ".venv" ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

echo "Installing Phase 6 live API dependencies into backend venv..."
pip install --quiet \
  boto3 \
  azure-identity \
  azure-mgmt-compute \
  google-cloud-compute \
  google-cloud-billing \
  requests

########################################
# app/modules/phase6/aws_live.py
########################################
cat > app/modules/phase6/aws_live.py << 'PYEOF'
from __future__ import annotations

from typing import List

import boto3
from botocore.config import Config

from .models import InstanceType, PricingQuote


def _ec2_client(region: str):
    return boto3.client(
        "ec2",
        region_name=region,
        config=Config(retries={"max_attempts": 5, "mode": "standard"}),
    )


def _pricing_client():
    # AWS Pricing is only available in us-east-1
    return boto3.client(
        "pricing",
        region_name="us-east-1",
        config=Config(retries={"max_attempts": 5, "mode": "standard"}),
    )


def get_aws_instance_types(region: str, limit: int = 10) -> List[InstanceType]:
    """
    Retrieve real EC2 instance types for a region using describe_instance_types.

    If anything goes wrong (no permissions, etc.), the caller (orchestrator)
    will catch the exception and fall back to mock data in 'hybrid' mode.
    """
    ec2 = _ec2_client(region)
    paginator = ec2.get_paginator("describe_instance_types")

    items: List[InstanceType] = []
    for page in paginator.paginate(PaginationConfig={"PageSize": min(limit, 100)}):
        for it in page.get("InstanceTypes", []):
            vcpus = it.get("VCpuInfo", {}).get("DefaultVCpus", 1)
            mem_mib = it.get("MemoryInfo", {}).get("SizeInMiB", 1024)
            family = it.get("InstanceType", "").split(".")[0] if it.get("InstanceType") else "unknown"
            inst_type = it.get("InstanceType", "unknown")

            items.append(
                InstanceType(
                    provider="aws",
                    region=region,
                    name=inst_type,
                    vcpus=int(vcpus),
                    memory_gb=round(mem_mib / 1024.0, 2),
                    family=family,
                    category="general_purpose",  # coarse category; can refine later
                )
            )
            if len(items) >= limit:
                return items

    return items


def get_aws_pricing(
    region: str,
    instance_type: str,
    hours_per_month: int,
) -> PricingQuote:
    """
    Use the AWS Pricing API to get On-Demand Linux pricing for an EC2 instance type.

    If no exact price is found or an error occurs, the orchestrator (in 'hybrid' mode)
    will fall back to mock pricing.
    """
    pricing = _pricing_client()

    # Pricing "location" is human-readable region name, not code, e.g. "US East (N. Virginia)"
    # For now we use a simple mapping; if not found, we let the Pricing API error
    region_map = {
        "us-east-1": "US East (N. Virginia)",
        "us-east-2": "US East (Ohio)",
        "us-west-1": "US West (N. California)",
        "us-west-2": "US West (Oregon)",
    }
    location = region_map.get(region, "US East (N. Virginia)")

    resp = pricing.get_products(
        ServiceCode="AmazonEC2",
        Filters=[
            {"Type": "TERM_MATCH", "Field": "instanceType", "Value": instance_type},
            {"Type": "TERM_MATCH", "Field": "location", "Value": location},
            {"Type": "TERM_MATCH", "Field": "operatingSystem", "Value": "Linux"},
            {"Type": "TERM_MATCH", "Field": "preInstalledSw", "Value": "NA"},
            {"Type": "TERM_MATCH", "Field": "tenancy", "Value": "Shared"},
            {"Type": "TERM_MATCH", "Field": "capacitystatus", "Value": "Used"},
        ],
        MaxResults=1,
    )

    if not resp.get("PriceList"):
        raise RuntimeError("No pricing data returned from AWS Pricing API")

    import json

    product = json.loads(resp["PriceList"][0])
    terms = product.get("terms", {}).get("OnDemand", {})
    if not terms:
        raise RuntimeError("No OnDemand terms found in pricing data")

    # Grab first term / dimension
    term = next(iter(terms.values()))
    dims = term.get("priceDimensions", {})
    dim = next(iter(dims.values()))
    price_per_unit = float(dim["pricePerUnit"]["USD"])

    hourly = price_per_unit
    monthly = round(hourly * hours_per_month, 2)

    return PricingQuote(
        provider="aws",
        region=region,
        instance_type=instance_type,
        currency="USD",
        hourly_usd=hourly,
        monthly_usd=monthly,
        source="aws_pricing_api",
    )
PYEOF

########################################
# app/modules/phase6/azure_live.py
########################################
cat > app/modules/phase6/azure_live.py << 'PYEOF'
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
PYEOF

########################################
# app/modules/phase6/gcp_live.py
########################################
cat > app/modules/phase6/gcp_live.py << 'PYEOF'
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
PYEOF

echo "Running python compile check for Phase 6 live modules..."
python3 -m compileall app/modules/phase6

echo "==[ Phase 6 live API wiring completed successfully ]=="
