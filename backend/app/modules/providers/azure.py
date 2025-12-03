from typing import Dict, Any
import httpx
import os

AZURE_API = os.getenv('AZURE_PRICES_API', 'https://prices.azure.com/api/retail/prices')

async def query_prices(filter_expr: str) -> Dict[str, Any]:
    """Query Azure retail prices with an OData filter; returns combined result page(s)."""
    items = []
    next_url = f"{AZURE_API}?$filter={filter_expr}"
    async with httpx.AsyncClient(timeout=30) as client:
        while next_url:
            data = (await client.get(next_url)).json()
            items.extend(data.get('Items', []))
            next_url = data.get('NextPageLink')
    return {'items': items}

