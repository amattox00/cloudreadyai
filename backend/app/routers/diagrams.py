from typing import Literal, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.modules.diagrams.topology_builder import build_diagram_spec
from app.modules.diagrams.drawio_exporter import (
    diagram_spec_to_base64_drawio,
    diagram_spec_to_base64_pdf,
)

router = APIRouter(prefix="/v1/diagrams", tags=["diagrams"])


class DiagramGenerateRequest(BaseModel):
    run_id: str
    cloud: Literal["aws"] = "aws"
    diagram_type: Literal["app_topology"] = "app_topology"

    # UI sends "full", and we may later support other modes like
    # "source_only", "target_only", "source_and_target".
    view_mode: Literal["full", "source_only", "target_only", "source_and_target"] = "full"


class DiagramResponse(BaseModel):
    filename: str
    xml_base64: str


@router.post("/generate", response_model=DiagramResponse)
def generate_diagram(req: DiagramGenerateRequest) -> Dict[str, str]:
    """
    Main endpoint used by the UI for:
      - Generate Preview
      - Download Draw.io
    Returns a .drawio file as base64 plus a nice filename.
    """
    try:
        spec = build_diagram_spec(
            run_id=req.run_id,
            cloud=req.cloud,
            diagram_type=req.diagram_type,
            view_mode=req.view_mode,
        )

        filename_base = f"cloudreadyai_diagram_{req.cloud}_{req.diagram_type}_{req.run_id}"
        filename, xml_b64 = diagram_spec_to_base64_drawio(
            spec,
            filename_base=filename_base,
        )
        return {"filename": filename, "xml_base64": xml_b64}
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate diagram: {exc}",
        ) from exc


@router.post("/pdf")
def generate_diagram_pdf(req: DiagramGenerateRequest) -> Dict[str, str]:
    """
    Endpoint for the 'Download PDF' button.

    Returns:
      {
        "filename": "<name>.pdf",
        "pdf_base64": "<base64 data>"
      }
    """
    try:
        spec = build_diagram_spec(
            run_id=req.run_id,
            cloud=req.cloud,
            diagram_type=req.diagram_type,
            view_mode=req.view_mode,
        )

        filename_base = f"cloudreadyai_diagram_{req.cloud}_{req.diagram_type}_{req.run_id}"
        filename, pdf_b64 = diagram_spec_to_base64_pdf(
            spec,
            filename_base=filename_base,
        )
        return {"filename": filename, "pdf_base64": pdf_b64}
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate PDF: {exc}",
        ) from exc
