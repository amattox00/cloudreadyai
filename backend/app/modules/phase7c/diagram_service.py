# backend/app/modules/phase7c/diagram_service.py

from __future__ import annotations

from typing import Dict, Optional

from app.modules.phase7b.exporters.drawio_exporter import generate_from_template
from .templates.aws_app_tier import aws_app_tier_template


def generate_complex_diagram(
    cloud: str,
    pattern: str,
    overrides: Optional[Dict] = None,
) -> str:
    """
    Phase 7C: richer topology patterns, still template-based.

    Supported (initial):
      - cloud = "aws", pattern = "3_tier_app"
    """
    overrides = overrides or {}
    key = (cloud.lower(), pattern.lower())

    if key == ("aws", "3_tier_app"):
        template = aws_app_tier_template(overrides)
    else:
        raise ValueError(f"Unsupported complex diagram pattern: {key}")

    return generate_from_template(template)
