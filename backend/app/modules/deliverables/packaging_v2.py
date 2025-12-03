from __future__ import annotations

import base64
import datetime
import io
import json
from pathlib import Path
import zipfile
from typing import Optional, Tuple

from fastapi import HTTPException

from app.models.workload import Workload
from app.modules.diagram.patterns import infer_pattern
from app.modules.diagram.spec import build_diagram_spec
from app.modules.diagram.render_drawio import diagram_spec_to_mxfile_xml


BASE_WORKLOAD_DIR = Path("data/workloads")


def load_workload_from_disk(workload_id: str) -> Workload:
    """
    Shared helper to load a Workload JSON from data/workloads/{workload_id}.json
    """
    path = BASE_WORKLOAD_DIR / f"{workload_id}.json"
    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Workload file not found for id '{workload_id}' at {path}",
        )
    data = json.loads(path.read_text())
    return Workload(**data)


def build_deliverables_zip(
    workload: Workload,
    *,
    opportunity_id: Optional[str] = None,
    org_name: Optional[str] = None,
    environment: Optional[str] = None,
    version_tag: Optional[str] = None,
) -> Tuple[str, bytes]:
    """
    Build an in-memory ZIP with:

      - diagrams/architecture.drawio.xml
      - metadata/workload.json
      - metadata/summary.txt
    """
    effective_env = environment or workload.environment
    pattern = infer_pattern(workload)
    spec = build_diagram_spec(workload, pattern)
    xml = diagram_spec_to_mxfile_xml(spec)

    now = datetime.datetime.utcnow().isoformat() + "Z"

    # Prepare summary text
    summary_lines = [
        "CloudReadyAI Deliverables Package (v2)",
        "-------------------------------------",
        f"Generated:        {now}",
        f"Workload ID:      {workload.workload_id}",
        f"Workload Name:    {workload.name}",
        f"Environment:      {effective_env}",
        f"Deployment Model: {workload.deployment_model}",
        f"Pattern ID:       {pattern.pattern_id}",
        "",
        f"Opportunity ID:   {opportunity_id or '(not provided)'}",
        f"Org Name:         {org_name or '(not provided)'}",
        f"Version Tag:      {version_tag or '(not provided)'}",
        "",
        "Contents:",
        "  - diagrams/architecture.drawio.xml",
        "  - metadata/workload.json",
        "  - metadata/summary.txt",
        "",
        "Notes:",
        "  - The draw.io XML can be imported directly into draw.io / diagrams.net.",
        "  - workload.json is the canonical normalized workload model used by Diagram Generator 2.0.",
    ]
    summary_text = "\n".join(summary_lines)

    # Build ZIP in memory
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("diagrams/architecture.drawio.xml", xml)
        z.writestr("metadata/workload.json", workload.model_dump_json(indent=2))
        z.writestr("metadata/summary.txt", summary_text)

    zip_bytes = buf.getvalue()

    # Derive filename
    base_name = opportunity_id or workload.workload_id or "cloudreadyai_deliverables"
    filename = f"{base_name}_deliverables_v2.zip"

    return filename, zip_bytes


def encode_zip_base64(zip_bytes: bytes) -> str:
    return base64.b64encode(zip_bytes).decode("utf-8")
