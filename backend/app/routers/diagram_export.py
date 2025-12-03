from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse
import base64

router = APIRouter(prefix="/v1/diagram", tags=["diagrams"])

# -----------------------------
# Request Model (Pydantic v2)
# -----------------------------
class DiagramExportRequest(BaseModel):
    xml: str = Field(
        ...,
        description="draw.io mxfile XML content"
    )
    format: str = Field(
        default="drawio",
        description="Export format (currently only 'drawio' is supported)",
        pattern="^(drawio)$"   # <-- Updated from regex= to pattern=
    )
    filename: str = Field(
        default="diagram",
        description="Filename without extension (letters, numbers, -, _)",
        pattern=r"^[A-Za-z0-9_-]+$"   # <-- Updated from regex= to pattern=
    )

# -----------------------------
# Response Model
# -----------------------------
class DiagramExportResponse(BaseModel):
    xml: str
    filename: str

# -----------------------------
# Endpoint
# -----------------------------
@router.post("/export", response_model=DiagramExportResponse)
async def diagram_export_api(payload: DiagramExportRequest):
    """
    Returns a draw.io XML file (raw XML content)
    """
    try:
        xml_data = payload.xml
        filename = payload.filename + ".drawio"

        if not xml_data.strip():
            raise HTTPException(status_code=400, detail="XML is empty")

        # No conversion yet — just return raw XML
        return DiagramExportResponse(
            xml=xml_data,
            filename=filename
        )

    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
