from typing import Dict, Any
from app.modules.phase7e.models import DiagramEnrichRequest
from app.modules.phase7e.service import enrich_diagram


def enrich_diagram_task(payload: Dict[str, Any]) -> Dict[str, Any]:
    req = DiagramEnrichRequest(**payload)
    resp = enrich_diagram(req)
    return resp.dict()
