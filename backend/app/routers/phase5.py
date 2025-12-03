from fastapi import APIRouter, Query
from typing import Dict, Any
import os

from app.modules import matching, recommend
from app.modules.providers import aws as aws_provider
from app.modules.providers import azure as azure_provider
from app.modules.providers import gcp as gcp_provider

router = APIRouter(prefix="/v1", tags=["phase5"])

@router.get("/providers/prices")
async def providers_prices(provider: str = Query(..., pattern="^(AWS|Azure|GCP)$"), region: str | None = None):
    if provider == 'AWS':
        data = await aws_provider.fetch_compute_pricing(region or '')
        return {"provider": provider, "region": region, "data": data}
    if provider == 'Azure':
        f = "serviceFamily eq 'Compute' and priceType eq 'Consumption'"
        data = await azure_provider.query_prices(f)
        return {"provider": provider, "data": data}
    if provider == 'GCP':
        # Compute Engine service name is stable, but may change; kept configurable later
        data = await gcp_provider.list_skus("services/6F81-5844-456A")
        return {"provider": provider, "data": data}

@router.post("/match/services")
async def match_services(payload: Dict[str, Any]):
    return matching.match_services(payload)

@router.post("/cost/compare")
async def cost_compare(payload: Dict[str, Any]):
    """Very simplified monthly total calculator; expects matches already selected,
       or uses default assumptions per provider. In real Phase 5, fetch exact prices.
    """
    matches = payload.get('matches') or matching.match_services(payload)
    # Placeholder monthly figures (to be replaced by real pull from pricing providers)
    # Using rough relative factors
    baseline = 400.0  # dummy baseline
    mult = {
        'AWS': 1.00,
        'Azure': 0.98,
        'GCP': 0.97,
    }
    costs = {
        p: {
            'instance': baseline * mult[p] * 0.85,
            'storage': baseline * mult[p] * 0.10,
            'network': baseline * mult[p] * 0.05,
            'monthly_total': baseline * mult[p],
        }
        for p in ['AWS','Azure','GCP']
    }
    return {'matches': matches, 'costs': costs}

@router.post("/recommend")
async def make_recommendation(payload: Dict[str, Any]):
    constraints = payload.get('constraints') or {}
    # Run compare first
    compare = await cost_compare(payload)
    return recommend.recommend(compare['matches'], compare['costs'], constraints)

@router.get("/diagram")
async def get_diagram_stub():
    # Placeholder: Phase 5 will return a generated SVG/PNG; here we return a stub
    return {
        'format': 'svg',
        'content': '<svg width="300" height="120" xmlns="http://www.w3.org/2000/svg">\n  <rect x="10" y="10" width="280" height="100" rx="12" ry="12" fill="#eef" stroke="#99f"/>\n  <text x="150" y="65" text-anchor="middle" font-family="Arial" font-size="14">CloudReadyAI Phase 5 Diagram Stub</text>\n</svg>'
    }
