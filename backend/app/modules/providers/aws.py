from typing import Dict, Any, List
import httpx
import os

AWS_INDEX = os.getenv('AWS_PRICING_INDEX', 'https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/index.json')

async def fetch_compute_pricing(region: str) -> Dict[str, Any]:
    """Fetch a minimal subset (on-demand Linux) for EC2; return raw map {sku: price}.
       For production, switch to specific EC2 offer file for the region family.
    """
    async with httpx.AsyncClient(timeout=30) as client:
        idx = (await client.get(AWS_INDEX)).json()
        ec2_offer_url = idx['offers']['AmazonEC2']['currentVersionUrl']
        offer = (await client.get(f"https://pricing.us-east-1.amazonaws.com{ec2_offer_url}")).json()
        # Ultra-minimal example: extract some Linux On-Demand prices
        prices: Dict[str, Any] = {}
        terms = offer.get('terms', {}).get('OnDemand', {})
        products = offer.get('products', {})
        for sku, prod in products.items():
            if prod.get('productFamily') != 'Compute Instance':
                continue
            attr = prod.get('attributes', {})
            if attr.get('operatingSystem') != 'Linux':
                continue
            if attr.get('location') is None:
                continue
            # NOTE: Region mapping would be required for exact filter; simplified here
            if region and region not in attr.get('location', ''):
                continue
            term = terms.get(sku, {})
            for _, term_obj in term.items():
                for _, p in term_obj.get('priceDimensions', {}).items():
                    prices[sku] = {
                        'desc': p.get('description'),
                        'unit': p.get('unit'),
                        'price_per_unit': float(p.get('pricePerUnit', {}).get('USD', '0') or 0),
                    }
        return prices

