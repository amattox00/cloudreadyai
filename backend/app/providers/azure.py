import time
from typing import List, Dict, Any

def fetch_prices(region: str, service: str, timeout: int = 8, max_results: int = 20, filter_compute: bool = True) -> Dict[str, Any]:
    items = [
        {"sku": "D4s_v5",  "vcpu": 4, "memory_gb": 16, "price_hour": 0.20},
        {"sku": "D8s_v5",  "vcpu": 8, "memory_gb": 32, "price_hour": 0.40},
    ][:max_results]
    return {
        "provider": "Azure",
        "region": region,
        "service": service,
        "fetched_at": int(time.time()),
        "items": items,
        "note": "Phase 7 Azure live placeholder; swap with Retail Prices API usage."
    }
