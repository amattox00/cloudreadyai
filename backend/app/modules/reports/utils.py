from pathlib import Path
from typing import Optional


def get_backend_root() -> Path:
    """
    Returns the backend root directory (…/cloudreadyai/backend).

    Assumes this file lives at:
        backend/app/modules/reports/utils.py
    """
    return Path(__file__).resolve().parents[3]


def get_reports_root() -> Path:
    """
    Root directory for all generated reports.
    Example:
        <backend_root>/reports
    """
    return get_backend_root() / "reports"


def ensure_reports_dir(run_id: str) -> Path:
    """
    Ensure the reports directory for a specific run_id exists.
    Example:
        <backend_root>/reports/<run_id>/
    """
    base = get_reports_root()
    target = base / run_id
    target.mkdir(parents=True, exist_ok=True)
    return target


def get_templates_dir() -> Path:
    """
    Directory where HTML templates for reporting live.
    Example:
        <backend_root>/app/modules/reports/templates
    """
    return Path(__file__).resolve().parent / "templates"


def get_logo_path(preferred_name: str = "cloudreadyai-logo.png") -> Optional[Path]:
    """
    Best-effort lookup for a logo image to embed in reports.

    You can drop your logo file at either:
      - <backend_root>/assets/<preferred_name>
      - <backend_root>/static/<preferred_name>

    Returns None if nothing is found.
    """
    backend_root = get_backend_root()
    candidates = [
        backend_root / "assets" / preferred_name,
        backend_root / "static" / preferred_name,
    ]

    for path in candidates:
        if path.is_file():
            return path

    return None
