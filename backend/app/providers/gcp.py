import time
from typing import List, Dict, Any

def fetch_prices(region: str, service: str, timeout: int = 8, max_results: int = 20, filter_compute: bool = True) -> Dict[str, Any]:
    items = [
        {"sku": "n2-standard-4",  "vcpu": 4, "memory_gb": 16, "price_hour": 0.19},
        {"sku": "n2-standard-8",  "vcpu": 8, "memory_gb": 32, "price_hour": 0.38},
    ][:max_results]
    return {
        "provider": "GCP",
        "region": region,
        "service": service,
        "fetched_at": int(time.time()),
        "items": items,
        "note": "Phase 7 GCP live placeholder; swap with Cloud Billing Catalog usage."
    }
