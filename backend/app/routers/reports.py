from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.modules.reports import service
from app.modules.reports.utils import get_reports_root

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
)


@router.post("/{run_id}/summary")
def generate_summary_report(
    run_id: str,
    db: Session = Depends(get_db),
):
    """
    Generate the Summary report (PDF + DOCX) for a given run_id.
    """
    outputs = service.generate_summary(db, run_id)
    return {
        "status": "ok",
        "run_id": run_id,
        "pdf_path": outputs["pdf_path"],
        "docx_path": outputs["docx_path"],
    }


@router.post("/{run_id}/technical")
def generate_technical_report(
    run_id: str,
    db: Session = Depends(get_db),
):
    """
    Generate the Technical Assessment report (PDF + DOCX) for a given run_id.
    """
    outputs = service.generate_technical(db, run_id)
    return {
        "status": "ok",
        "run_id": run_id,
        "pdf_path": outputs["pdf_path"],
        "docx_path": outputs["docx_path"],
    }


@router.post("/{run_id}/architecture")
def generate_architecture_report(
    run_id: str,
    db: Session = Depends(get_db),
):
    """
    Generate the Target Architecture report (PDF + DOCX) for a given run_id.
    """
    outputs = service.generate_architecture(db, run_id)
    return {
        "status": "ok",
        "run_id": run_id,
        "pdf_path": outputs["pdf_path"],
        "docx_path": outputs["docx_path"],
    }


@router.post("/{run_id}/generate-all")
def generate_all_reports(
    run_id: str,
    db: Session = Depends(get_db),
):
    """
    Generate all reports (Summary, Technical, Architecture) and a ZIP package.
    """
    outputs = service.generate_all(db, run_id)
    return {
        "status": "ok",
        "run_id": run_id,
        **outputs,
    }


@router.get("/{run_id}/download/{filename}")
def download_report_file(run_id: str, filename: str):
    """
    Download a specific file from the reports directory for this run_id.

    Example filenames:
      - summary.pdf
      - summary.docx
      - technical.pdf
      - technical.docx
      - architecture.pdf
      - architecture.docx
      - CloudReadyAI-Assessment-Package.zip
    """
    reports_root = get_reports_root()
    file_path = reports_root / run_id / filename

    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Requested report file not found.")

    return FileResponse(
        path=str(file_path),
        filename=file_path.name,
        media_type="application/octet-stream",
    )
