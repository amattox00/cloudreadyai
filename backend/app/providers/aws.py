import time
from typing import List, Dict, Any

def fetch_prices(region: str, service: str, timeout: int = 8, max_results: int = 20, filter_compute: bool = True) -> Dict[str, Any]:
    """
    Phase 7 live-ready placeholder for AWS pricing.
    In LIVE mode, you can replace the body with real calls to AWS Pricing APIs or curated endpoints.
    For now we return a tiny "live-shaped" payload quickly, suitable for UI/tests.
    """
    items = [
        {"sku": "m6i.large",   "vcpu": 2, "memory_gb": 8,  "price_hour": 0.096},
        {"sku": "m6i.xlarge",  "vcpu": 4, "memory_gb": 16, "price_hour": 0.192},
        {"sku": "m6i.2xlarge", "vcpu": 8, "memory_gb": 32, "price_hour": 0.384},
    ][:max_results]
    return {
        "provider": "AWS",
        "region": region,
        "service": service,
        "fetched_at": int(time.time()),
        "items": items,
        "note": "Phase 7 AWS live placeholder; swap with real fetch in production."
    }
