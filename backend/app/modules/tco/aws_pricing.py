"""
aws_pricing.py

Simple region-aware pricing layer for CloudReadyAI TCO.

We are NOT calling the real AWS Pricing API yet – this is a
stable, predictable “pricing model” that:
- varies by region
- supports EC2, EBS, NAT, and RDS
- is good enough for demos and planning

All prices are USD, approximate, and for **Linux, shared tenancy**.
"""

from __future__ import annotations

from typing import Dict

# ---------------------------------------------------------------------------
# Regions & multipliers
# ---------------------------------------------------------------------------

# Canonical region codes we support in the UI
SUPPORTED_REGIONS: Dict[str, str] = {
    "us-east-1": "US East (N. Virginia)",
    "us-east-2": "US East (Ohio)",
    "us-west-2": "US West (Oregon)",
    "eu-west-1": "EU (Ireland)",
    "eu-central-1": "EU (Frankfurt)",
}

# Simple price multipliers vs. a "baseline" us-east-1 price.
REGION_MULTIPLIER: Dict[str, float] = {
    "us-east-1": 1.00,  # baseline
    "us-east-2": 1.03,  # a little higher
    "us-west-2": 1.06,  # slightly higher
    "eu-west-1": 1.18,  # EU premium
    "eu-central-1": 1.22,
}

# ---------------------------------------------------------------------------
# EC2 baseline hourly prices (approximate public On-Demand)
# ---------------------------------------------------------------------------

EC2_BASE_HOURLY: Dict[str, float] = {
    "m5.large": 0.096,
    "m5.xlarge": 0.192,
    "m5.2xlarge": 0.384,
}

# ---------------------------------------------------------------------------
# EBS baseline per-GB monthly prices
# ---------------------------------------------------------------------------

# These are deliberately simple buckets – we just need realistic variance.
EBS_BASE_GB_MONTHLY: Dict[str, float] = {
    "gp3": 0.08,   # generic SSD
    "ssd": 0.10,   # “premium” SSD bucket
    "hdd": 0.045,  # spinning / throughput optimized
}

# ---------------------------------------------------------------------------
# NAT / RDS baselines
# ---------------------------------------------------------------------------

# Rough NAT gateway + a bit of data transfer per month (per gateway).
NAT_BASE_MONTHLY = 32.00

# Very rough RDS “medium-ish” DB, hourly.
RDS_BASE_HOURLY = 0.25

HOURS_PER_MONTH = 730.0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def normalize_region(region: str) -> str:
    """
    Validate and normalize an incoming region string.

    Accepts canonical region codes (us-east-1, eu-west-1, etc.).
    Raises ValueError if unsupported so the caller can return a
    friendly API error.
    """
    if not region:
        raise ValueError("Region is required")

    code = region.strip().lower()
    if code not in SUPPORTED_REGIONS:
        raise ValueError(f"Unsupported region '{region}'. Supported: {', '.join(SUPPORTED_REGIONS)}")

    return code


def region_multiplier(region: str) -> float:
    code = normalize_region(region)
    return REGION_MULTIPLIER.get(code, 1.0)


# ---------------------------------------------------------------------------
# EC2
# ---------------------------------------------------------------------------

def map_server_to_instance(vcpu: int | None, ram_gb: int | None) -> str:
    """
    Very simple vCPU/RAM → instance mapping for demo purposes.
    If we don't have vCPU/RAM, we default to m5.large so that
    we still get a price instead of crashing.
    """
    v = vcpu or 0
    r = ram_gb or 0

    if v <= 4 and r <= 16:
        return "m5.large"
    if v <= 8 and r <= 32:
        return "m5.xlarge"
    return "m5.2xlarge"


def get_ec2_hourly_price(instance_type: str, region: str) -> float:
    base = EC2_BASE_HOURLY.get(instance_type, EC2_BASE_HOURLY["m5.large"])
    return base * region_multiplier(region)


def get_ec2_monthly(instance_type: str, region: str) -> float:
    return get_ec2_hourly_price(instance_type, region) * HOURS_PER_MONTH


# Backwards-compat alias if any callers used this name
def get_ec2_price(instance_type: str, region: str) -> float:
    return get_ec2_monthly(instance_type, region)


# ---------------------------------------------------------------------------
# EBS
# ---------------------------------------------------------------------------

def _pick_ebs_bucket(storage_type: str | None) -> str:
    if not storage_type:
        return "gp3"

    t = storage_type.lower()
    if "gp3" in t or "gp2" in t or "ssd" in t:
        return "gp3"
    if "st1" in t or "sc1" in t or "hdd" in t:
        return "hdd"
    return "gp3"


def get_ebs_price(storage_type: str, region: str) -> float:
    """
    Return per-GB monthly price for a given storage type and region.
    NOTE: This is *per GB per month*, not for the whole volume.
    """
    bucket = _pick_ebs_bucket(storage_type)
    base = EBS_BASE_GB_MONTHLY[bucket]
    return base * region_multiplier(region)


# ---------------------------------------------------------------------------
# NAT
# ---------------------------------------------------------------------------

def get_nat_gateway_monthly(region: str, num_gateways: int = 1) -> float:
    """
    Very simple NAT model – one blended monthly number per gateway.
    """
    return NAT_BASE_MONTHLY * region_multiplier(region) * max(num_gateways, 1)


# Backwards-compat alias if older code imported this name.
def get_nat_gateway_price(region: str, num_gateways: int = 1) -> float:
    return get_nat_gateway_monthly(region, num_gateways=num_gateways)


# ---------------------------------------------------------------------------
# RDS
# ---------------------------------------------------------------------------

def get_rds_monthly(instance_class: str, region: str) -> float:
    """
    Simple “modeled” RDS cost – same base regardless of class for now.
    This keeps the API surface ready without us needing full RDS logic yet.
    """
    base_monthly = RDS_BASE_HOURLY * HOURS_PER_MONTH
    return base_monthly * region_multiplier(region)


def get_rds_price(instance_class: str, region: str) -> float:
    # Alias so both naming styles are safe.
    return get_rds_monthly(instance_class, region)
