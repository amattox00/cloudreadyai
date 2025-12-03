#!/usr/bin/env bash
set -euo pipefail

echo "==[ Phase 8 Example Ingestion: assets.json -> Workload -> /v1/workloads/save ]=="

cd ~/cloudreadyai/backend

# 0) Activate backend venv if present
if [[ -d ".venv" ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

# 1) Ensure examples/assets folder and sample assets JSON
mkdir -p examples/assets

ASSETS_FILE="examples/assets/sample_three_tier_assets.json"

if [[ ! -f "$ASSETS_FILE" ]]; then
  cat > "$ASSETS_FILE" << 'JSONEOF'
{
  "workload_id": "wl-ingested-sample-3tier",
  "name": "Ingested 3-Tier Web App",
  "description": "Example of converting discovery assets into a normalized Workload.",
  "environment": "prod",
  "deployment_model": "single_cloud",
  "business": {
    "owner": "Application Team",
    "criticality": "high",
    "industry": "Example",
    "tags": ["customer-facing", "ingested"]
  },
  "components": [
    {
      "id": "clients",
      "name": "Users / Clients",
      "role": "client",
      "layer": "presentation",
      "technology_type": "other",
      "platform": { "location": "other", "service_hint": "internet" }
    },
    {
      "id": "lb",
      "name": "Public ALB",
      "role": "edge",
      "layer": "presentation",
      "technology_type": "load_balancer",
      "platform": { "location": "aws", "service_hint": "alb", "region": "us-east-2" }
    },
    {
      "id": "app",
      "name": "App Pods (EKS)",
      "role": "app",
      "layer": "application",
      "technology_type": "k8s_pod",
      "platform": { "location": "aws", "service_hint": "eks", "region": "us-east-2" }
    },
    {
      "id": "db",
      "name": "PostgreSQL (RDS)",
      "role": "data",
      "layer": "data",
      "technology_type": "database",
      "platform": { "location": "aws", "service_hint": "rds", "region": "us-east-2" }
    }
  ],
  "links": [
    { "id": "l1", "source": "clients", "target": "lb", "relationship": "calls" },
    { "id": "l2", "source": "lb", "target": "app", "relationship": "calls" },
    { "id": "l3", "source": "app", "target": "db", "relationship": "reads_from" }
  ]
}
JSONEOF

  echo "Created sample assets file at $ASSETS_FILE"
else
  echo "Sample assets file already exists at $ASSETS_FILE"
fi

# 2) Create example_ingest module
mkdir -p app/modules/workload

INGEST_MODULE="app/modules/workload/example_ingest.py"

cat > "$INGEST_MODULE" << 'PYEOF'
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
PYEOF

echo "Created $INGEST_MODULE"

# 3) Compile check for the module
python3 -m compileall "$INGEST_MODULE" >/dev/null
echo "✅ example_ingest module compile check passed."

# 4) Use the module to build a Workload from the sample assets and
#    write /tmp/phase8_ingested_workload.json in the format expected by /v1/workloads/save
python3 - << 'PY'
import json
from pathlib import Path

from app.modules.workload.example_ingest import assets_to_workload

assets_path = Path("examples/assets/sample_three_tier_assets.json")
data = json.loads(assets_path.read_text())
wl = assets_to_workload(data)

wrapper = {"workload": json.loads(wl.model_dump_json())}
out_path = Path("/tmp/phase8_ingested_workload.json")
out_path.write_text(json.dumps(wrapper))
print("Wrote inline workload wrapper to", out_path)
PY

# 5) Call /v1/workloads/save via curl using the wrapper file
echo "Calling /v1/workloads/save with ingested workload..."
curl -sS -X POST http://localhost:8000/v1/workloads/save \
  -H "Content-Type: application/json" \
  -d @/tmp/phase8_ingested_workload.json

echo
echo "✅ Phase 8 example ingestion completed."
