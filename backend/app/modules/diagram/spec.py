from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel

from app.models.workload import Workload, Node, Edge
from app.modules.diagram.patterns import PatternResult


class DiagramContainer(BaseModel):
    """
    A visual zone in the diagram, e.g.:

    - Users / Clients
    - Edge / Ingress
    - Application Tier
    - Data Tier
    - Operations & Security
    """
    id: str
    label: str
    role: str  # "clients", "edge", "app", "data", "ops", "other"
    order: int


class DiagramNode(BaseModel):
    """
    A visual node in the diagram tied back to an underlying workload node.
    """
    id: str  # diagram node id
    label: str
    role: str  # "client", "edge", "app", "data", "cache", "queue", "monitoring", ...
    container_id: str

    # Reference to the underlying workload node
    workload_node_id: str

    # Optional hints for the renderer (e.g., which CSP icon to use)
    platform_location: str
    platform_service_hint: Optional[str] = None


class DiagramEdge(BaseModel):
    """
    A visual edge between diagram nodes, with a step number and kind.
    """
    id: str
    source_id: str
    target_id: str

    step: int
    kind: Literal["request", "data", "telemetry", "event", "other"] = "other"
    label: Optional[str] = None  # optional label to show near the arrow


class DiagramSpec(BaseModel):
    """
    Intermediate, cloud-neutral spec describing what to render.

    A later step will convert this into draw.io XML, PNG, SVG, etc.
    """
    title: str
    pattern_id: str
    containers: List[DiagramContainer]
    nodes: List[DiagramNode]
    edges: List[DiagramEdge]


# --- Helpers --------------------------------------------------------------


def _default_containers_for_three_tier() -> List[DiagramContainer]:
    """
    Containers that roughly match the style of the sample diagrams:

      Clients -> Edge -> App -> Data -> Ops
    """
    return [
        DiagramContainer(id="clients", label="Users / Clients", role="clients", order=1),
        DiagramContainer(id="edge", label="Edge / Ingress", role="edge", order=2),
        DiagramContainer(id="app", label="Application Tier", role="app", order=3),
        DiagramContainer(id="data", label="Data Tier", role="data", order=4),
        DiagramContainer(id="ops", label="Operations & Security", role="ops", order=5),
    ]


def _assign_container_for_node(node: Node) -> str:
    """
    Decide which container a workload node belongs in based on its role.
    """
    role = node.role.lower()

    if role == "client":
        return "clients"
    if role == "edge":
        return "edge"
    if role in {"app", "application", "backend"}:
        return "app"
    if role in {"data", "db", "database", "cache", "queue", "storage"}:
        return "data"
    if role in {"monitoring", "logging", "identity", "security", "ops"}:
        return "ops"

    # Fallback: put unknown roles into app tier for now
    return "app"


def _kind_for_edge(edge: Edge) -> str:
    rel = (edge.relationship or "").lower()
    if rel in {"calls", "invokes", "requests"}:
        return "request"
    if rel in {"reads_from", "writes_to", "persists_to"}:
        return "data"
    if rel in {"monitored_by", "logs_to"}:
        return "telemetry"
    if rel in {"publishes_to", "subscribes_to", "emits_event_to"}:
        return "event"
    return "other"


# --- Public API -----------------------------------------------------------


def build_diagram_spec(workload: Workload, pattern: PatternResult) -> DiagramSpec:
    """
    Given a workload and a detected pattern, build a diagram spec.

    For now this focuses on the 'three_tier_web_app' pattern.
    Other patterns will be added later, reusing the same DiagramSpec.
    """
    if pattern.pattern_id == "three_tier_web_app":
        containers = _default_containers_for_three_tier()
        title = f"{workload.name} – 3-Tier Web Application"
    else:
        # Simple generic layout: Clients, App, Data, Ops
        containers = _default_containers_for_three_tier()
        title = f"{workload.name} – Architecture Overview"

    # Map workload nodes -> diagram nodes
    diagram_nodes: List[DiagramNode] = []
    for wn in workload.nodes:
        container_id = _assign_container_for_node(wn)
        dn = DiagramNode(
            id=f"dn-{wn.node_id}",
            label=wn.name,
            role=wn.role,
            container_id=container_id,
            workload_node_id=wn.node_id,
            platform_location=wn.platform.location,
            platform_service_hint=wn.platform.service_hint,
        )
        diagram_nodes.append(dn)

    # Build diagram edges with step numbers
    diagram_edges: List[DiagramEdge] = []
    for idx, we in enumerate(workload.edges, start=1):
        kind = _kind_for_edge(we)
        de = DiagramEdge(
            id=f"de-{we.edge_id}",
            source_id=f"dn-{we.source}",
            target_id=f"dn-{we.target}",
            step=idx,
            kind=kind,  # type: ignore[arg-type]
            label=str(idx),
        )
        diagram_edges.append(de)

    return DiagramSpec(
        title=title,
        pattern_id=pattern.pattern_id,
        containers=containers,
        nodes=diagram_nodes,
        edges=diagram_edges,
    )
