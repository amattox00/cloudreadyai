from __future__ import annotations

from typing import Dict, Any, List

from app.models.workload import Workload, Node, Edge, Platform, BusinessMetadata


def assets_to_workload(data: Dict[str, Any]) -> Workload:
    """
    Convert a simple assets.json structure into a canonical Workload.

    Expected input shape:

      {
        "workload_id": "...",
        "name": "...",
        "description": "...",
        "environment": "prod",
        "deployment_model": "single_cloud",
        "business": { ...optional... },
        "components": [
          {
            "id": "app",
            "name": "App Pods",
            "role": "app",
            "layer": "application",
            "technology_type": "k8s_pod",
            "platform": { "location": "aws", "service_hint": "eks", ... }
          },
          ...
        ],
        "links": [
          {
            "id": "l1",
            "source": "clients",
            "target": "lb",
            "relationship": "calls"
          },
          ...
        ]
      }
    """
    workload_id = data["workload_id"]
    name = data["name"]
    description = data.get("description")
    environment = data["environment"]
    deployment_model = data["deployment_model"]

    business_meta = None
    if "business" in data:
        b = data["business"]
        business_meta = BusinessMetadata(
            owner=b.get("owner"),
            criticality=b.get("criticality"),
            industry=b.get("industry"),
            tags=b.get("tags") or [],
        )

    nodes: List[Node] = []
    for comp in data.get("components", []):
        platform_data = comp.get("platform") or {}
        platform = Platform(
            location=platform_data.get("location", "other"),
            service_hint=platform_data.get("service_hint"),
            region=platform_data.get("region"),
            account_id=platform_data.get("account_id"),
        )

        node = Node(
            node_id=comp["id"],
            name=comp["name"],
            role=comp["role"],
            layer=comp["layer"],
            technology_type=comp["technology_type"],
            platform=platform,
            sizing=None,
            labels=[],
            metadata={},
        )
        nodes.append(node)

    edges: List[Edge] = []
    for link in data.get("links", []):
        edge = Edge(
            edge_id=link["id"],
            source=link["source"],
            target=link["target"],
            relationship=link.get("relationship", "calls"),
            protocol=None,
            direction="unidirectional",
            frequency=None,
            port=None,
            notes=None,
        )
        edges.append(edge)

    return Workload(
        workload_id=workload_id,
        name=name,
        description=description,
        environment=environment,
        deployment_model=deployment_model,
        business=business_meta,
        nodes=nodes,
        edges=edges,
    )
