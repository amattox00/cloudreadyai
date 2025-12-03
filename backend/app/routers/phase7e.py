from fastapi import APIRouter
from ..modules.phase7e.models import (
    DiagramAutoLayoutRequest,
    DiagramZeroTrustRequest,
    DiagramEnrichRequest,
    DiagramEnrichResponse,
)
from ..modules.phase7e.service import (
    apply_auto_layout,
    apply_zero_trust_overlays,
    enrich_diagram,
)

router = APIRouter(prefix="/v1/diagram", tags=["phase7e"])


@router.post("/auto-layout", response_model=str, summary="Apply CSP auto-layout to diagram XML")
async def auto_layout_endpoint(payload: DiagramAutoLayoutRequest) -> str:
    return apply_auto_layout(payload)


@router.post("/zero-trust", response_model=str, summary="Apply Zero Trust overlays to diagram XML")
async def zero_trust_endpoint(payload: DiagramZeroTrustRequest) -> str:
    return apply_zero_trust_overlays(payload)


@router.post("/enrich", response_model=DiagramEnrichResponse, summary="AI-driven diagram enrichment")
async def enrich_endpoint(payload: DiagramEnrichRequest) -> DiagramEnrichResponse:
    return enrich_diagram(payload)
