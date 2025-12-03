from .models import (
    DiagramAutoLayoutRequest,
    DiagramZeroTrustRequest,
    DiagramEnrichRequest,
    DiagramEnrichResponse,
)
from .auto_layout import apply_grid_layout
from .zero_trust import apply_zero_trust
from .enrichment import build_recommendations


def apply_auto_layout(req: DiagramAutoLayoutRequest) -> str:
    return apply_grid_layout(req.xml)


def apply_zero_trust_overlays(req: DiagramZeroTrustRequest) -> str:
    return apply_zero_trust(req.xml, req.metadata)


def enrich_diagram(req: DiagramEnrichRequest) -> DiagramEnrichResponse:
    xml = req.xml

    if req.enable_auto_layout:
        xml = apply_grid_layout(xml)

    if req.enable_zero_trust:
        xml = apply_zero_trust(xml, req.metadata)

    recommendations = build_recommendations(req.metadata) if req.include_recommendations else []

    return DiagramEnrichResponse(
        xml=xml,
        metadata=req.metadata,
        recommendations=recommendations,
        extras={
            "auto_layout_applied": req.enable_auto_layout,
            "zero_trust_applied": req.enable_zero_trust,
        },
    )
