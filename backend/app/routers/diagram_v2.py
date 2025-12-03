from __future__ import annotations

from pathlib import Path
import json
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.workload import Workload
from app.modules.diagram.patterns import infer_pattern
from app.modules.diagram.spec import build_diagram_spec
from app.modules.diagram.render_drawio import diagram_spec_to_mxfile_xml


router = APIRouter(tags=["diagram_v2"])


class DiagramGenerateV2Request(BaseModel):
    """
    Workload source options:

      - workload (inline Workload model)       -> highest priority
      - workload_id (string)                  -> load from data/workloads/{id}.json
      - neither                                -> fall back to sample workload (for demo/testing)
    """
    workload: Optional[Workload] = None
    workload_id: Optional[str] = None
    detail_level: Optional[str] = "detailed"  # reserved for future use


class DiagramGenerateV2Response(BaseModel):
    xml: str


def _load_workload_from_sample() -> Workload:
    """
    Temporary helper: load the sample workload we created in Step 1.
    """
    sample_path = Path("examples/workloads/sample_three_tier_webapp.json")
    if not sample_path.exists():
        raise HTTPException(status_code=500, detail="Sample workload file not found on server.")
    data = json.loads(sample_path.read_text())
    return Workload(**data)


def _load_workload_from_disk(workload_id: str) -> Workload:
    """
    Starter implementation of "real" workloads:
    looks for JSON at data/workloads/{workload_id}.json
    """
    base = Path("data/workloads")
    path = base / f"{workload_id}.json"
    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Workload file not found for id '{workload_id}' at {path}",
        )
    data = json.loads(path.read_text())
    return Workload(**data)


@router.post("/diagram/generate_v2", response_model=DiagramGenerateV2Response)
def generate_diagram_v2(payload: DiagramGenerateV2Request) -> DiagramGenerateV2Response:
    """
    Generate a diagram using the new Generator 2.0 pipeline:

      Workload -> Pattern -> DiagramSpec -> Draw.io XML

    Resolution order for workload:

      1) payload.workload (inline body)
      2) payload.workload_id (lookup on disk)
      3) fallback to sample workload JSON
    """
    if payload.workload is not None:
        workload = payload.workload
    elif payload.workload_id is not None:
        workload = _load_workload_from_disk(payload.workload_id)
    else:
        workload = _load_workload_from_sample()

    pattern = infer_pattern(workload)
    spec = build_diagram_spec(workload, pattern)
    xml = diagram_spec_to_mxfile_xml(spec)

    return DiagramGenerateV2Response(xml=xml)
