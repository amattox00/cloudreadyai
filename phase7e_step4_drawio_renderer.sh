#!/usr/bin/env bash
set -euo pipefail

echo "==[ Step 4: Draw.io (mxGraph) renderer for Diagram Generator 2.0 ]=="

cd ~/cloudreadyai/backend

# 0) (Recommended) activate backend venv if present
if [[ -d ".venv" ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

# 1) Ensure diagram module directory exists
mkdir -p app/modules/diagram

# 2) Create render_drawio.py
cat > app/modules/diagram/render_drawio.py << 'PYEOF'
from __future__ import annotations

import datetime
import xml.etree.ElementTree as ET
from typing import Optional

from app.modules.diagram.spec import DiagramSpec


def _mx_cell(
    cell_id: str,
    value: Optional[str] = None,
    style: Optional[str] = None,
    parent: Optional[str] = None,
    vertex: bool = False,
    edge: bool = False,
    source: Optional[str] = None,
    target: Optional[str] = None,
) -> ET.Element:
    cell = ET.Element("mxCell")
    cell.set("id", cell_id)
    if value is not None:
        cell.set("value", value)
    if style is not None:
        cell.set("style", style)
    if parent is not None:
        cell.set("parent", parent)
    if vertex:
        cell.set("vertex", "1")
    if edge:
        cell.set("edge", "1")
    if source is not None:
        cell.set("source", source)
    if target is not None:
        cell.set("target", target)
    return cell


def _mx_geometry(
    x: float,
    y: float,
    width: float,
    height: float,
    relative: bool = False,
) -> ET.Element:
    geom = ET.Element("mxGeometry")
    if relative:
        geom.set("relative", "1")
    geom.set("x", str(x))
    geom.set("y", str(y))
    geom.set("width", str(width))
    geom.set("height", str(height))
    geom.set("as", "geometry")
    return geom


def diagram_spec_to_mxfile_xml(spec: DiagramSpec) -> str:
    """
    Convert a DiagramSpec into a draw.io (mxGraph) XML string.

    This doesn't try to be pixel-perfect; it lays things out in a clean
    left-to-right container order, with nodes stacked inside each container.
    """

    # --- Root <mxfile> / <diagram> / <mxGraphModel> scaffolding ----------
    mxfile = ET.Element("mxfile")
    mxfile.set("host", "cloudreadyai")
    mxfile.set("modified", datetime.datetime.utcnow().isoformat() + "Z")
    mxfile.set("agent", "CloudReadyAI-Phase7E")
    mxfile.set("version", "1.0")

    diagram = ET.SubElement(mxfile, "diagram")
    diagram.set("id", "diagram-1")
    diagram.set("name", spec.title)

    model = ET.SubElement(diagram, "mxGraphModel")
    model.set("dx", "1024")
    model.set("dy", "768")
    model.set("grid", "1")
    model.set("gridSize", "10")
    model.set("guides", "1")
    model.set("tooltips", "1")
    model.set("connect", "1")
    model.set("arrows", "1")
    model.set("fold", "1")
    model.set("page", "1")
    model.set("pageScale", "1")
    model.set("pageWidth", "850")
    model.set("pageHeight", "1100")
    model.set("math", "0")
    model.set("shadow", "0")

    root = ET.SubElement(model, "root")

    # Required base cells in mxGraph
    root.append(_mx_cell("0"))
    root.append(_mx_cell("1", parent="0"))

    # --- Layout parameters -----------------------------------------------
    container_width = 220.0
    container_height = 320.0
    container_spacing_x = 40.0
    container_origin_x = 40.0
    container_origin_y = 60.0

    node_width = 160.0
    node_height = 50.0
    node_vertical_spacing = 10.0
    node_top_margin = 30.0

    # We'll track how many nodes we've placed in each container for stacking
    nodes_in_container: dict[str, int] = {}

    # --- Create containers as group/swimlanes ----------------------------
    for c in sorted(spec.containers, key=lambda c: c.order):
        idx = c.order - 1
        x = container_origin_x + idx * (container_width + container_spacing_x)
        y = container_origin_y

        container_id = f"ct-{c.id}"
        cell = _mx_cell(
            cell_id=container_id,
            value=c.label,
            style="swimlane;rounded=1;whiteSpace=wrap;html=1;childLayout=stackLayout;",
            parent="1",
            vertex=True,
        )
        geom = _mx_geometry(x=x, y=y, width=container_width, height=container_height)
        cell.append(geom)
        root.append(cell)

        nodes_in_container[c.id] = 0

    # Helper to find container cell id from container_id
    def container_cell_id(container_id: str) -> str:
        return f"ct-{container_id}"

    # --- Create node vertices --------------------------------------------
    for n in spec.nodes:
        count = nodes_in_container.get(n.container_id, 0)

        base_container_x = container_origin_x + (
            (next(c.order for c in spec.containers if c.id == n.container_id) - 1)
            * (container_width + container_spacing_x)
        )
        # y coordinate is relative to page; inside container, we just space them
        x = base_container_x + (container_width - node_width) / 2.0
        y = container_origin_y + node_top_margin + count * (node_height + node_vertical_spacing)

        nodes_in_container[n.container_id] = count + 1

        node_id = n.id  # already like "dn-<workload_node_id>"
        style = "rounded=1;whiteSpace=wrap;html=1;"

        # We could later extend this with CSP-specific icons based on
        # n.platform_location and n.platform_service_hint.

        cell = _mx_cell(
            cell_id=node_id,
            value=n.label,
            style=style,
            parent=container_cell_id(n.container_id),
            vertex=True,
        )
        geom = _mx_geometry(
            x=x - base_container_x,  # position inside container
            y=y - container_origin_y,
            width=node_width,
            height=node_height,
        )
        cell.append(geom)
        root.append(cell)

    # --- Create edges --------------------------------------------
    for e in spec.edges:
        edge_id = e.id
        style = "endArrow=block;rounded=1;"

        cell = _mx_cell(
            cell_id=edge_id,
            value=e.label or "",
            style=style,
            parent="1",
            edge=True,
            source=e.source_id,
            target=e.target_id,
        )
        geom = _mx_geometry(x=0, y=0, width=0, height=0, relative=True)
        cell.append(geom)
        root.append(cell)

    # --- Serialize to string ---------------------------------------------
    xml_bytes = ET.tostring(mxfile, encoding="utf-8", method="xml")
    return xml_bytes.decode("utf-8")
PYEOF

echo "Created app/modules/diagram/render_drawio.py"

# 3) Quick syntax check
python3 -m compileall app/modules/diagram/render_drawio.py >/dev/null

echo "✅ Step 4 files created and compiled successfully."

# 4) Quick end-to-end test: Workload -> Pattern -> DiagramSpec -> XML
python3 - << 'PY'
from app.models.workload import Workload
from app.modules.diagram.patterns import infer_pattern
from app.modules.diagram.spec import build_diagram_spec
from app.modules.diagram.render_drawio import diagram_spec_to_mxfile_xml
import json, pathlib

path = pathlib.Path("examples/workloads/sample_three_tier_webapp.json")
data = json.loads(path.read_text())
wl = Workload(**data)

pattern = infer_pattern(wl)
spec = build_diagram_spec(wl, pattern)
xml = diagram_spec_to_mxfile_xml(spec)

print("=== Diagram title ===")
print(spec.title)
print("=== First 40 lines of XML ===")
for i, line in enumerate(xml.splitlines(), start=1):
    print(f"{i:02d}: {line}")
    if i >= 40:
        break
PY

echo "✅ Step 4 test completed."
