from xml.etree import ElementTree as ET
from typing import Tuple


def _iter_vertices(root: ET.Element):
    for cell in root.findall(".//mxCell"):
        if cell.get("vertex") == "1":
            yield cell


def _ensure_geometry(cell: ET.Element) -> ET.Element:
    geom = cell.find("mxGeometry")
    if geom is None:
        geom = ET.SubElement(cell, "mxGeometry")
        geom.set("width", "120")
        geom.set("height", "60")
        geom.set("as", "geometry")
    return geom


def _grid_position(index: int, cols: int = 4, x_step: int = 220, y_step: int = 140) -> Tuple[int, int]:
    row = index // cols
    col = index % cols
    x = 40 + col * x_step
    y = 40 + row * y_step
    return x, y


def apply_grid_layout(xml_str: str) -> str:
    tree = ET.fromstring(xml_str)
    graph_model = tree.find(".//mxGraphModel")
    if graph_model is None:
        return xml_str

    root = graph_model.find("root")
    if root is None:
        return xml_str

    for i, cell in enumerate(_iter_vertices(root)):
        geom = _ensure_geometry(cell)
        x, y = _grid_position(i)
        geom.set("x", str(x))
        geom.set("y", str(y))

    return ET.tostring(tree, encoding="unicode")
