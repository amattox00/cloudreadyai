#!/usr/bin/env bash
set -euo pipefail

echo "==[ Step 1: Workload schema for Diagram Generator 2.0 ]=="

# 1) Go to backend
cd ~/cloudreadyai/backend

# 2) Ensure models directory exists
mkdir -p app/models

# 3) Create workload.py with canonical models
cat > app/models/workload.py << 'PYEOF'
from __future__ import annotations

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel


class Platform(BaseModel):
    """
    Where this node runs (on-prem, AWS, Azure, GCP, etc.).
    This is cloud-neutral but gives hints to the diagram generator.
    """
    location: Literal["on_prem", "aws", "azure", "gcp", "other"] = "other"
    service_hint: Optional[str] = None  # e.g. "alb", "eks", "rds", "aks", "sql_db"
    region: Optional[str] = None
    account_id: Optional[str] = None


class Node(BaseModel):
    """
    A single logical component in the workload graph:
    app, db, cache, queue, gateway, identity provider, etc.
    """
    node_id: str
    name: str

    # How the diagram engine will group/position this node
    role: str  # "client", "edge", "app", "data", "cache", "queue", "identity", "monitoring", ...
    layer: str  # "presentation", "application", "data", "ops", "security"
    technology_type: str  # "vm", "k8s_pod", "database", "load_balancer", "object_store", ...

    platform: Platform

    sizing: Optional[Dict[str, float]] = None  # vcpus, memory_gb, storage_gb, etc.
    labels: List[str] = []  # arbitrary tags
    metadata: Dict[str, str] = {}  # free-form extra info (os, db_engine, cluster, namespace, ...)


class Edge(BaseModel):
    """
    Relationship between two nodes: calls, reads_from, writes_to, monitored_by, etc.
    """
    edge_id: str
    source: str  # node_id
    target: str  # node_id

    relationship: str  # "calls", "reads_from", "writes_to", "monitored_by", ...
    protocol: Optional[str] = None  # "https", "tcp", "sql", ...
    direction: Literal["unidirectional", "bidirectional"] = "unidirectional"
    frequency: Optional[str] = None  # "sync", "async", "batch"
    port: Optional[int] = None
    notes: Optional[str] = None


class BusinessMetadata(BaseModel):
    owner: Optional[str] = None
    criticality: Optional[Literal["low", "medium", "high"]] = None
    industry: Optional[str] = None
    tags: List[str] = []  # e.g. ["customer-facing", "regulated"]


class Workload(BaseModel):
    """
    Canonical, cloud-neutral description of a client's workload.
    This is the main input to Diagram Generator 2.0.
    """
    workload_id: str
    name: str
    description: Optional[str] = None

    environment: str  # "prod", "nonprod", "dev", "test", "dr", ...
    deployment_model: str  # "on_prem", "single_cloud", "multi_cloud", "hybrid"

    business: Optional[BusinessMetadata] = None

    nodes: List[Node]
    edges: List[Edge]
PYEOF

echo "Created app/models/workload.py"

# 4) Export models from app/models/__init__.py (without clobbering existing content)
INIT_FILE="app/models/__init__.py"
if [[ ! -f "$INIT_FILE" ]]; then
  echo "# Models package for CloudReadyAI backend" > "$INIT_FILE"
fi

# Only append the import line if it's not already there
if ! grep -q "from .workload import" "$INIT_FILE"; then
  echo "from .workload import Platform, Node, Edge, BusinessMetadata, Workload" >> "$INIT_FILE"
fi

echo "Updated $INIT_FILE"

# 5) (Optional but helpful) create an example workload JSON for later tests
mkdir -p examples/workloads

cat > examples/workloads/sample_three_tier_webapp.json << 'JEOF'
{
  "workload_id": "wl-sample-3tier-001",
  "name": "Sample 3-Tier Web App",
  "description": "Example workload for Diagram Generator 2.0 testing",
  "environment": "prod",
  "deployment_model": "single_cloud",
  "business": {
    "owner": "Application Team",
    "criticality": "high",
    "industry": "Example",
    "tags": ["customer-facing", "sample"]
  },
  "nodes": [
    {
      "node_id": "n-clients",
      "name": "Users / Clients",
      "role": "client",
      "layer": "presentation",
      "technology_type": "other",
      "platform": { "location": "other", "service_hint": "internet" },
      "labels": ["external_users"],
      "metadata": {}
    },
    {
      "node_id": "n-alb",
      "name": "Public Ingress",
      "role": "edge",
      "layer": "presentation",
      "technology_type": "load_balancer",
      "platform": { "location": "aws", "service_hint": "alb", "region": "us-east-2" },
      "labels": [],
      "metadata": {}
    },
    {
      "node_id": "n-eks",
      "name": "Web & API (EKS)",
      "role": "app",
      "layer": "application",
      "technology_type": "k8s_pod",
      "platform": { "location": "aws", "service_hint": "eks", "region": "us-east-2" },
      "labels": [],
      "metadata": {}
    },
    {
      "node_id": "n-rds",
      "name": "PostgreSQL Database",
      "role": "data",
      "layer": "data",
      "technology_type": "database",
      "platform": { "location": "aws", "service_hint": "rds", "region": "us-east-2" },
      "labels": [],
      "metadata": {}
    },
    {
      "node_id": "n-redis",
      "name": "Redis Cache",
      "role": "cache",
      "layer": "data",
      "technology_type": "database",
      "platform": { "location": "aws", "service_hint": "elasticache", "region": "us-east-2" },
      "labels": [],
      "metadata": {}
    }
  ],
  "edges": [
    {
      "edge_id": "e1",
      "source": "n-clients",
      "target": "n-alb",
      "relationship": "calls",
      "protocol": "https",
      "direction": "unidirectional",
      "frequency": "sync",
      "port": 443
    },
    {
      "edge_id": "e2",
      "source": "n-alb",
      "target": "n-eks",
      "relationship": "calls",
      "protocol": "https",
      "direction": "unidirectional",
      "frequency": "sync",
      "port": 443
    },
    {
      "edge_id": "e3",
      "source": "n-eks",
      "target": "n-rds",
      "relationship": "reads_from",
      "protocol": "sql",
      "direction": "bidirectional",
      "frequency": "sync",
      "port": 5432
    },
    {
      "edge_id": "e4",
      "source": "n-eks",
      "target": "n-redis",
      "relationship": "reads_from",
      "protocol": "tcp",
      "direction": "bidirectional",
      "frequency": "sync",
      "port": 6379
    }
  ]
}
JEOF

echo "Created examples/workloads/sample_three_tier_webapp.json"

# 6) Quick syntax check so we fail fast if there's a typo
python -m compileall app/models/workload.py >/dev/null

echo "✅ Step 1 complete: workload schema models created and validated."
