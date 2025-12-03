from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .utils import get_templates_dir, ensure_reports_dir

try:
    from weasyprint import HTML  # type: ignore
except ImportError:  # pragma: no cover
    HTML = None  # type: ignore


# Global Jinja2 environment for report templates
_env = Environment(
    loader=FileSystemLoader(str(get_templates_dir())),
    autoescape=select_autoescape(["html", "xml"]),
    trim_blocks=True,
    lstrip_blocks=True,
)


def render_html(template_name: str, context: Dict[str, Any]) -> str:
    """
    Render a Jinja2 HTML template with the given context.
    """
    template = _env.get_template(template_name)
    return template.render(**context)


def build_pdf(
    run_id: str,
    template_name: str,
    context: Dict[str, Any],
    output_filename: str,
) -> Path:
    """
    Render HTML → PDF and save it to the run_id reports directory.

    Returns the full Path of the generated PDF.
    """
    if HTML is None:
        raise RuntimeError(
            "WeasyPrint is not installed. Install it with: pip install weasyprint"
        )

    reports_dir = ensure_reports_dir(run_id)
    output_path = reports_dir / output_filename

    # Make sure directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    html_str = render_html(template_name, context)
    HTML(string=html_str, base_url=str(get_templates_dir())).write_pdf(
        str(output_path)
    )

    return output_path
