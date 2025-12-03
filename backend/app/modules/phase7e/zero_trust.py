from xml.etree import ElementTree as ET
from .models import DiagramMetadata

ZERO_TRUST_ZONE_STYLES = {
    "default": "shape=swimlane;horizontal=0;rounded=1;opacity=20;fillColor=#dae8fc;",
    "identity": "shape=swimlane;horizontal=0;rounded=1;opacity=15;fillColor=#e1d5e7;",
    "data": "shape=swimlane;horizontal=0;rounded=1;opacity=15;fillColor=#d5e8d4;",
}


def _add_zone(
    root: ET.Element,
    zone_id: str,
    label: str,
    style_key: str,
    x: int,
    y: int,
    width: int,
    height: int,
):
    cell = ET.SubElement(root, "mxCell")
    cell.set("id", zone_id)
    cell.set("value", label)
    cell.set("style", ZERO_TRUST_ZONE_STYLES.get(style_key, ZERO_TRUST_ZONE_STYLES["default"]))
    cell.set("vertex", "1")
    cell.set("parent", "1")

    geom = ET.SubElement(cell, "mxGeometry")
    geom.set("x", str(x))
    geom.set("y", str(y))
    geom.set("width", str(width))
    geom.set("height", str(height))
    geom.set("as", "geometry")


def apply_zero_trust(xml_str: str, metadata: DiagramMetadata) -> str:
    tree = ET.fromstring(xml_str)
    graph_model = tree.find(".//mxGraphModel")
    if graph_model is None:
        return xml_str

    root = graph_model.find("root")
    if root is None:
        return xml_str

    base_x, base_y, width, height = 20, 20, 1200, 800

    cloud = (metadata.cloud or "aws").lower()
    compliance = (metadata.compliance or "").lower()

    zone_label = {
        "aws": "AWS Application & Data Plane",
        "azure": "Azure Application & Data Plane",
        "gcp": "GCP Application & Data Plane",
    }.get(cloud, "Application & Data Plane")

    identity_label = "Identity & Policy Plane"
    if "dod" in compliance or "il" in compliance:
        identity_label = "DoD Identity / Policy Plane"

    data_label = "Data & Logging Plane"

    _add_zone(root, "zt_app_plane", zone_label, "default", base_x, base_y, width, int(height * 0.6))
    _add_zone(
        root,
        "zt_identity_plane",
        identity_label,
        "identity",
        base_x + 10,
        base_y - 80,
        int(width * 0.6),
        70,
    )
    _add_zone(
        root,
        "zt_data_plane",
        data_label,
        "data",
        base_x + int(width * 0.65),
        base_y - 80,
        int(width * 0.3),
        70,
    )

    return ET.tostring(tree, encoding="unicode")
