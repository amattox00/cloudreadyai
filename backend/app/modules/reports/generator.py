from pathlib import Path
from typing import Any, Dict, Mapping

from .pdf_builder import build_pdf
from .docx_builder import build_docx
from .packager import create_zip_package
from .utils import ensure_reports_dir


SUMMARY_TEMPLATE = "summary.html"
TECHNICAL_TEMPLATE = "technical.html"
ARCHITECTURE_TEMPLATE = "architecture.html"


def generate_summary_reports(run_id: str, context: Dict[str, Any]) -> Dict[str, Path]:
    reports_dir = ensure_reports_dir(run_id)

    pdf_path = build_pdf(
        run_id=run_id,
        template_name=SUMMARY_TEMPLATE,
        context=context,
        output_filename="summary.pdf",
    )

    docx_path = build_docx(
        run_id=run_id,
        report_type="summary",
        context=context,
        output_filename="summary.docx",
    )

    return {"pdf": pdf_path, "docx": docx_path, "dir": reports_dir}


def generate_technical_reports(
    run_id: str, context: Dict[str, Any]
) -> Dict[str, Path]:
    reports_dir = ensure_reports_dir(run_id)

    pdf_path = build_pdf(
        run_id=run_id,
        template_name=TECHNICAL_TEMPLATE,
        context=context,
        output_filename="technical.pdf",
    )

    docx_path = build_docx(
        run_id=run_id,
        report_type="technical",
        context=context,
        output_filename="technical.docx",
    )

    return {"pdf": pdf_path, "docx": docx_path, "dir": reports_dir}


def generate_architecture_reports(
    run_id: str, context: Dict[str, Any]
) -> Dict[str, Path]:
    reports_dir = ensure_reports_dir(run_id)

    pdf_path = build_pdf(
        run_id=run_id,
        template_name=ARCHITECTURE_TEMPLATE,
        context=context,
        output_filename="architecture.pdf",
    )

    docx_path = build_docx(
        run_id=run_id,
        report_type="architecture",
        context=context,
        output_filename="architecture.docx",
    )

    return {"pdf": pdf_path, "docx": docx_path, "dir": reports_dir}


def generate_all_reports(
    run_id: str, contexts: Mapping[str, Dict[str, Any]]
) -> Dict[str, Path]:
    """
    Generate all three report types and a combined ZIP package.

    contexts keys:
        "summary", "technical", "architecture"
    """
    summary_ctx = contexts.get("summary", {})
    technical_ctx = contexts.get("technical", {})
    architecture_ctx = contexts.get("architecture", {})

    summary = generate_summary_reports(run_id, summary_ctx)
    technical = generate_technical_reports(run_id, technical_ctx)
    architecture = generate_architecture_reports(run_id, architecture_ctx)

    files = [
        summary["pdf"],
        summary["docx"],
        technical["pdf"],
        technical["docx"],
        architecture["pdf"],
        architecture["docx"],
    ]

    zip_path = create_zip_package(run_id, files)

    return {
        "summary_pdf": summary["pdf"],
        "summary_docx": summary["docx"],
        "technical_pdf": technical["pdf"],
        "technical_docx": technical["docx"],
        "architecture_pdf": architecture["pdf"],
        "architecture_docx": architecture["docx"],
        "package_zip": zip_path,
    }
