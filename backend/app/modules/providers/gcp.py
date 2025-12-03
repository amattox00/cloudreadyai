from typing import Dict, Any
import httpx
import os

BASE = os.getenv('GCP_BILLING_API_BASE', 'https://cloudbilling.googleapis.com/v1')
API_KEY = os.getenv('GCP_BILLING_API_KEY')

async def list_skus(service_name: str) -> Dict[str, Any]:
    """List SKUs for a GCP service (e.g., services/6F81-5844-456A for Compute Engine)."""
    params = {}
    if API_KEY:
        params['key'] = API_KEY
    async with httpx.AsyncClient(timeout=30) as client:
        url = f"{BASE}/{service_name}/skus"
        data = (await client.get(url, params=params)).json()
        return data

