import os, json
from typing import Dict, Any
from app.providers import aws as aws_live
from app.providers import azure as azure_live
from app.providers import gcp as gcp_live

def is_live() -> bool:
    return os.getenv("PHASE7_MODE", "mock").lower() == "live"

def fetch_prices(provider: str, region: str, service: str,
                 timeout: int = 8, max_results: int = 20, filter_compute: bool = True) -> Dict[str, Any]:
    """
    If PHASE7_MODE=live, use provider module; otherwise raise to caller to fallback to Phase-5 path.
    """
    if not is_live():
        raise RuntimeError("phase7_not_live")
    p = provider.upper()
    if p == "AWS":
        return aws_live.fetch_prices(region, service, timeout, max_results, filter_compute)
    if p == "AZURE":
        return azure_live.fetch_prices(region, service, timeout, max_results, filter_compute)
    if p == "GCP":
        return gcp_live.fetch_prices(region, service, timeout, max_results, filter_compute)
    raise ValueError(f"Unsupported provider: {provider}")
