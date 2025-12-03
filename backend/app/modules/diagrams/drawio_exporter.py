from __future__ import annotations

import base64
import uuid
import xml.etree.ElementTree as ET
from typing import Any, Dict, Tuple

from app.modules.diagrams.topology_builder import DiagramSpec, Node, Edge


def _clean_attrib(attrs: Dict[str, Any]) -> Dict[str, str]:
    """
    Convert all non-None values to strings and drop any keys with None values.
    This prevents xml.etree.ElementTree from throwing 'cannot serialize None'.
    """
    return {k: str(v) for k, v in attrs.items() if v is not None}


def _node_to_mxcell(node: Node, fallback_id: str) -> ET.Element:
    """
    Convert a Node into an <mxCell> vertex element.
    Ensures no None values are passed into XML.
    """
    cell_id = node.id or fallback_id

    # Basic vertex cell attributes
    attrib = _clean_attrib(
        {
            "id": cell_id,
            "value": node.label or "",
            "style": node.style or "",
            "vertex": "1",
            # If parent is None, attach to cell "1" (the default layer)
            "parent": node.parent or "1",
        }
    )

    cell = ET.Element("mxCell", attrib)

    # Geometry — default to 0/0/width/height if any are missing
    x = getattr(node, "x", 0) or 0
    y = getattr(node, "y", 0) or 0
    width = getattr(node, "width", 160) or 160
    height = getattr(node, "height", 80) or 80

    geom_attrib = _clean_attrib(
        {
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "as": "geometry",
        }
    )
    ET.SubElement(cell, "mxGeometry", geom_attrib)
    return cell


def _edge_to_mxcell(edge: Edge, fallback_id: str) -> ET.Element:
    """
    Convert an Edge into an <mxCell> edge element.
    Ensures no None values are passed into XML.
    """
    cell_id = edge.id or fallback_id

    attrib = _clean_attrib(
        {
            "id": cell_id,
            "value": edge.label or "",
            "style": edge.style or "",
            "edge": "1",
            "source": edge.source,
            "target": edge.target,
            "parent": "1",
        }
    )

    cell = ET.Element("mxCell", attrib)

    # Basic geometry for edges
    geom_attrib = _clean_attrib({"relative": "1", "as": "geometry"})
    ET.SubElement(cell, "mxGeometry", geom_attrib)
    return cell


def _diagram_spec_to_xml(diagram: DiagramSpec) -> bytes:
    """
    Turn a DiagramSpec into a draw.io-compatible XML (mxfile).
    This is intentionally simple but structurally valid.
    """
    # Top-level mxfile + diagram
    mxfile = ET.Element("mxfile")
    diagram_el = ET.SubElement(mxfile, "diagram", _clean_attrib({"name": diagram.title or "Diagram"}))

    # Graph model + root
    model = ET.SubElement(diagram_el, "mxGraphModel")
    root = ET.SubElement(model, "root")

    # Mandatory root cells
    ET.SubElement(root, "mxCell", _clean_attrib({"id": "0"}))
    ET.SubElement(root, "mxCell", _clean_attrib({"id": "1", "parent": "0"}))

    # Map from our node IDs to cell IDs (in case we need consistency later)
    node_id_map: Dict[str, str] = {}

    # Add all nodes
    for idx, node in enumerate(diagram.nodes):
        fallback_id = f"n_{idx}"
        cell = _node_to_mxcell(node, fallback_id=fallback_id)
        root.append(cell)
        node_id_map[node.id or fallback_id] = cell.get("id") or fallback_id

    # Add all edges
    for idx, edge in enumerate(diagram.edges):
        fallback_id = f"e_{idx}"

        # Ensure source / target reference valid node IDs if possible
        source = node_id_map.get(edge.source, edge.source)
        target = node_id_map.get(edge.target, edge.target)

        safe_edge = Edge(
            source=source,
            target=target,
            label=edge.label,
            style=edge.style,
            id=edge.id,
            metadata=getattr(edge, "metadata", {}),
        )

        cell = _edge_to_mxcell(safe_edge, fallback_id=fallback_id)
        root.append(cell)

    # Serialize with XML declaration
    xml_bytes = ET.tostring(mxfile, encoding="utf-8", xml_declaration=True)
    return xml_bytes


def diagram_spec_to_base64_drawio(diagram: DiagramSpec, filename_base: str) -> Tuple[str, str]:
    """
    Public API: Convert DiagramSpec into a .drawio file (base64 XML).
    Returns (filename, xml_base64).
    """
    xml_bytes = _diagram_spec_to_xml(diagram)
    xml_b64 = base64.b64encode(xml_bytes).decode("ascii")

    # Generate a safe filename
    safe_base = filename_base or "cloudreadyai_diagram"
    filename = f"{safe_base}.drawio"

    return filename, xml_b64


def diagram_spec_to_base64_pdf(diagram: DiagramSpec, filename_base: str) -> Tuple[str, str]:
    """
    Placeholder implementation for PDF export.
    Currently not implemented – we just raise, so the router can handle it
    or we can wire a real PDF converter later.
    """
    raise NotImplementedError("PDF export is not implemented for diagrams yet.")
