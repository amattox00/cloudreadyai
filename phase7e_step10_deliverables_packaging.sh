#!/usr/bin/env bash
set -euo pipefail

echo "==[ Step 10: Deliverables Packaging Engine (v2) ]=="

cd ~/cloudreadyai/backend

# 0) Activate backend venv if present
if [[ -d ".venv" ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

# 1) Create modules/deliverables package and packaging_v2.py
mkdir -p app/modules/deliverables

DELIVERABLES_MODULE="app/modules/deliverables/packaging_v2.py"

cat > "$DELIVERABLES_MODULE" << 'PYEOF'
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
PYEOF

echo "Created $DELIVERABLES_MODULE"

# 2) Create router deliverables_v2.py
DELIVERABLES_ROUTER="app/routers/deliverables_v2.py"

cat > "$DELIVERABLES_ROUTER" << 'PYEOF'
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter

from pydantic import BaseModel

from app.modules.deliverables.packaging_v2 import (
    load_workload_from_disk,
    build_deliverables_zip,
    encode_zip_base64,
)


router = APIRouter(tags=["deliverables_v2"])


class DeliverablesPackageV2Request(BaseModel):
    workload_id: str
    opportunity_id: Optional[str] = None
    org_name: Optional[str] = None
    environment: Optional[str] = None
    version_tag: Optional[str] = None


class DeliverablesPackageV2Response(BaseModel):
    zip_filename: str
    zip_base64: str


@router.post("/deliverables/package_v2", response_model=DeliverablesPackageV2Response)
def package_deliverables_v2(payload: DeliverablesPackageV2Request) -> DeliverablesPackageV2Response:
    """
    Package deliverables for a given workload_id (and optional opportunity metadata)
    into a ZIP containing:

      - diagrams/architecture.drawio.xml
      - metadata/workload.json
      - metadata/summary.txt
    """
    workload = load_workload_from_disk(payload.workload_id)

    filename, zip_bytes = build_deliverables_zip(
        workload,
        opportunity_id=payload.opportunity_id,
        org_name=payload.org_name,
        environment=payload.environment,
        version_tag=payload.version_tag,
    )

    zip_b64 = encode_zip_base64(zip_bytes)
    return DeliverablesPackageV2Response(zip_filename=filename, zip_base64=zip_b64)
PYEOF

echo "Created $DELIVERABLES_ROUTER"

# 3) Compile check
python3 -m compileall "$DELIVERABLES_MODULE" "$DELIVERABLES_ROUTER" >/dev/null
echo "✅ Deliverables modules compile check passed."

# 4) Wire router into app/main.py
MAIN_FILE="app/main.py"
if [[ ! -f "$MAIN_FILE" ]]; then
  echo "ERROR: $MAIN_FILE not found. Please adjust MAIN_FILE path in the script."
  exit 1
fi

# 4a) Add import if missing
if ! grep -q "from app.routers import deliverables_v2" "$MAIN_FILE"; then
  echo "Adding import for deliverables_v2 router to $MAIN_FILE"
  echo "from app.routers import deliverables_v2" >> "$MAIN_FILE"
else
  echo "deliverables_v2 import already present in $MAIN_FILE"
fi

# 4b) Add include_router if missing
if ! grep -q "deliverables_v2.router" "$MAIN_FILE"; then
  echo "Adding app.include_router(...) for deliverables_v2 to $MAIN_FILE"
  echo "app.include_router(deliverables_v2.router, prefix=\"/v1\")" >> "$MAIN_FILE"
else
  echo "deliverables_v2 router already included in $MAIN_FILE"
fi

echo "✅ main.py updated for deliverables_v2 router."

# 5) Quick in-process test (no HTTP):
#    Use wl-demo-phase7e (created in Step 9) if present, otherwise try wl-sample-3tier-001.

python3 - << 'PY'
from pathlib import Path

from app.routers.workloads import list_workloads
from app.routers.deliverables_v2 import package_deliverables_v2, DeliverablesPackageV2Request

lst = list_workloads()
if not lst.items:
    raise SystemExit("No workloads found in data/workloads; cannot run test.")

wl_id = lst.items[0].workload_id
print("Using workload_id for test:", wl_id)

req = DeliverablesPackageV2Request(
    workload_id=wl_id,
    opportunity_id="TEST-OPP-123",
    org_name="CloudReadyAI Demo Org",
    environment="dev",
    version_tag="v2-test",
)
resp = package_deliverables_v2(req)
print("Package filename:", resp.zip_filename)
print("Base64 length:", len(resp.zip_base64))
PY

echo "✅ Step 10 tests completed."

