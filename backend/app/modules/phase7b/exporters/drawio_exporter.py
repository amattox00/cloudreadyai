# backend/app/modules/phase7b/exporters/drawio_exporter.py

from __future__ import annotations

from typing import Dict, List
import html


def _escape_value(text: str | None) -> str:
    """
    Escape text for use inside an XML attribute value for draw.io:
    - Escape &, <, >, quotes
    - Replace newlines with &#xa; (what draw.io uses for line breaks)
    """
    if not text:
        return ""
    # Escape XML special chars
    escaped = html.escape(text, quote=True)
    # Convert literal newlines to draw.io-compatible line breaks
    escaped = escaped.replace("\n", "&#xa;")
    return escaped


def generate_basic_drawio_xml() -> str:
    """
    Minimal test diagram used by /v1/diagram/test and /test/raw.
    """
    template = {
        "name": "CloudReadyAI Basic",
        "nodes": [
            {
                "id": "n1",
                "label": "CloudReadyAI",
                "x": 80,
                "y": 80,
                "width": 200,
                "height": 80,
                "style": "rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;",
            }
        ],
        "edges": [],
    }
    return generate_from_template(template)


def generate_from_template(template: Dict) -> str:
    """
    Generic draw.io XML generator from a simple template dict:

      {
        "name": "Diagram Name",
        "nodes": [
          {
            "id": "n1",
            "label": "Text",
            "x": 80, "y": 40,
            "width": 260, "height": 80,
            "style": "..."
          },
          ...
        ],
        "edges": [
          {
            "id": "e1",
            "source": "n1",
            "target": "n2",
            "style": "endArrow=block;strokeColor=#000000;"
          },
          ...
        ]
      }
    """
    name = template.get("name", "Cloud Diagram")
    nodes: List[Dict] = template.get("nodes", [])
    edges: List[Dict] = template.get("edges", [])

    lines: List[str] = []
    lines.append(
        '<mxfile host="cloudreadyai" modified="2025-01-01T00:00:00Z" '
        'agent="CloudReadyAI-Phase7B" version="1.0">'
    )
    lines.append(f'  <diagram id="cloud-diagram" name="{_escape_value(name)}">')
    lines.append(
        '    <mxGraphModel dx="1024" dy="768" grid="1" gridSize="10" guides="1" '
        'tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" '
        'pageWidth="850" pageHeight="1100" math="0" shadow="0">'
    )
    lines.append("      <root>")
    lines.append('        <mxCell id="0"/>')
    lines.append('        <mxCell id="1" parent="0"/>')

    # Nodes
    for node in nodes:
        nid = node.get("id")
        label = _escape_value(node.get("label", ""))
        style = node.get("style", "rounded=1;whiteSpace=wrap;html=1;")
        x = node.get("x", 40)
        y = node.get("y", 40)
        width = node.get("width", 160)
        height = node.get("height", 80)

        lines.append(
            f'        <mxCell id="{nid}" value="{label}" '
            f'style="{style}" vertex="1" parent="1">'
        )
        lines.append(
            f'          <mxGeometry x="{x}" y="{y}" width="{width}" height="{height}" as="geometry"/>'
        )
        lines.append("        </mxCell>")

    # Edges
    for edge in edges:
        eid = edge.get("id")
        source = edge.get("source")
        target = edge.get("target")
        style = edge.get("style", "endArrow=block;strokeColor=#000000;")

        lines.append(
            f'        <mxCell id="{eid}" edge="1" source="{source}" target="{target}" style="{style}">'
        )
        lines.append('          <mxGeometry relative="1" as="geometry"/>')
        lines.append("        </mxCell>")

    lines.append("      </root>")
    lines.append("    </mxGraphModel>")
    lines.append("  </diagram>")
    lines.append("</mxfile>")

    return "\n".join(lines)
