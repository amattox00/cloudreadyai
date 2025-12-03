#!/usr/bin/env bash
set -euo pipefail

echo "==[ Step 5: Integrate Diagram Generator 2.0 into backend API ]=="

cd ~/cloudreadyai/backend

# 0) Activate backend venv if present
if [[ -d ".venv" ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

# 1) Ensure routers directory exists
mkdir -p app/routers

# 2) Create diagram_v2.py router
cat > app/routers/diagram_v2.py << 'PYEOF'
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
    For now, workload_id is optional.
    If not provided, we fall back to a sample workload JSON on disk.
    Later, this will be wired to real stored workloads.
    """
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


@router.post("/diagram/generate_v2", response_model=DiagramGenerateV2Response)
def generate_diagram_v2(payload: DiagramGenerateV2Request) -> DiagramGenerateV2Response:
    """
    Generate a diagram using the new Generator 2.0 pipeline:

      Workload -> Pattern -> DiagramSpec -> Draw.io XML

    For now:
      - If workload_id is None, we use the sample workload JSON.
      - If workload_id is set, we return 501 until real lookup is implemented.
    """
    if payload.workload_id is None:
        workload = _load_workload_from_sample()
    else:
        # Placeholder for future DB lookup / ingestion link
        raise HTTPException(
            status_code=501,
            detail="Loading workload by ID is not implemented yet in Generator 2.0.",
        )

    pattern = infer_pattern(workload)
    spec = build_diagram_spec(workload, pattern)
    xml = diagram_spec_to_mxfile_xml(spec)

    return DiagramGenerateV2Response(xml=xml)
PYEOF

echo "Created app/routers/diagram_v2.py"

# 3) Compile check for the new router
python3 -m compileall app/routers/diagram_v2.py >/dev/null
echo "✅ Router compile check passed."

# 4) Wire router into app/main.py
MAIN_FILE="app/main.py"
if [[ ! -f "$MAIN_FILE" ]]; then
  echo "ERROR: $MAIN_FILE not found. Please adjust MAIN_FILE path in the script."
  exit 1
fi

# 4a) Ensure we import diagram_v2
if ! grep -q "from app.routers import diagram_v2" "$MAIN_FILE"; then
  echo "Adding import for diagram_v2 to $MAIN_FILE"
  echo "from app.routers import diagram_v2" >> "$MAIN_FILE"
else
  echo "diagram_v2 import already present in $MAIN_FILE"
fi

# 4b) Ensure we include the router
if ! grep -q "diagram_v2.router" "$MAIN_FILE"; then
  echo "Adding app.include_router(...) for diagram_v2 to $MAIN_FILE"
  echo "app.include_router(diagram_v2.router, prefix=\"/v1\")" >> "$MAIN_FILE"
else
  echo "diagram_v2 router already included in $MAIN_FILE"
fi

echo "✅ main.py updated."

echo "==[ Step 5 completed: API integration done. ]=="
