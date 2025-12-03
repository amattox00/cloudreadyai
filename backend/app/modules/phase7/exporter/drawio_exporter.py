from pathlib import Path
from typing import Tuple


SUPPORTED_FORMATS = {"drawio"}  # PDF/PNG/SVG reserved for a later phase

MIME_TYPES = {
    "drawio": "application/xml",
}


class DiagramExportError(Exception):
    """Custom exception for export failures."""
    pass


def _ensure_output_dir() -> Path:
    """
    Ensure a local diagrams/ directory exists under backend/app/.
    """
    # File path: backend/app/modules/phase7/exporter/drawio_exporter.py
    # parents[0] = drawio_exporter.py
    # parents[1] = exporter
    # parents[2] = phase7
    # parents[3] = modules
    # parents[4] = app
    app_dir = Path(__file__).resolve().parents[4]
    out_dir = app_dir / "diagrams"
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def _write_xml_to_file(xml: str, filename: str) -> Path:
    """
    Write XML to a .drawio file in the diagrams/ directory and return the path.
    """
    if not xml or not xml.strip():
        raise DiagramExportError("Empty XML payload cannot be exported.")

    # Allow only safe characters in filename
    safe_name = "".join(c for c in filename if c.isalnum() or c in ("-", "_")) or "diagram"
    out_dir = _ensure_output_dir()
    xml_path = out_dir / f"{safe_name}.drawio"
    xml_path.write_text(xml, encoding="utf-8")
    return xml_path


def export_diagram(xml: str, fmt: str, filename: str) -> Tuple[Path, str]:
    """
    High-level function used by the FastAPI router.

    Currently supports only 'drawio' (native XML download).
    PDF/PNG/SVG will be added when an external export service is wired in.
    """
    fmt = fmt.lower()
    if fmt not in SUPPORTED_FORMATS:
        raise DiagramExportError(
            f"Format '{fmt}' is not yet supported. "
            "Use 'drawio' for now. PDF/PNG/SVG will be enabled in a later phase."
        )

    xml_path = _write_xml_to_file(xml, filename)
    mime = MIME_TYPES[fmt]
    return xml_path, mime
