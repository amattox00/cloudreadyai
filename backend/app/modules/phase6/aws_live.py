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
