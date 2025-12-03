# app/modules/diagrams/models.py

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional, Any

from pydantic import BaseModel


# -------------------------------------------------------------------
# Core enums
# -------------------------------------------------------------------


class CloudProvider(str, Enum):
    aws = "aws"
    azure = "azure"
    gcp = "gcp"


class DiagramType(str, Enum):
    landing_zone = "landing_zone"
    app_topology = "app_topology"
    network_security = "network_security"
    data_db = "data_db"


class NodeKind(str, Enum):
    compute = "compute"              # servers, VMs
    database = "database"            # DBs, clusters
    storage_volume = "storage_volume"
    storage_array = "storage_array"
    network_segment = "network_segment"
    network_gateway = "network_gateway"
    network_firewall = "network_firewall"
    app_service = "app_service"      # logical applications
    external_saas = "external_saas"
    message_bus = "message_bus"
    cache = "cache"
    unknown = "unknown"


class EdgeKind(str, Enum):
    connects_to = "connects_to"      # logical dependency
    runs_on = "runs_on"              # app -> server
    attached_to = "attached_to"      # volume -> server
    replicates_to = "replicates_to"  # db -> db
    inbound_from = "inbound_from"    # external -> internal
    unknown = "unknown"


class BusinessCriticality(str, Enum):
    mission_critical = "mission_critical"
    high = "high"
    medium = "medium"
    low = "low"


class UtilizationBand(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class DiagramLayer(str, Enum):
    edge = "edge"        # Internet, DNS, CDN, WAF
    web = "web"          # public-facing web tier
    app = "app"          # internal app tier
    data = "data"        # DBs, data services
    ops = "ops"          # monitoring, logging, backup
    security = "security"  # IAM, firewalls, ZT controls


class DiagramViewMode(str, Enum):
    source_only = "source_only"
    target_only = "target_only"
    source_and_target = "source_and_target"


# -------------------------------------------------------------------
# Normalized topology (built from ingestion)
# -------------------------------------------------------------------


class TopologyNode(BaseModel):
    id: str
    kind: NodeKind
    name: Optional[str] = None

    # Infra placement
    environment: Optional[str] = None
    region: Optional[str] = None

    # OS / runtime
    os_family: Optional[str] = None
    runtime: Optional[str] = None

    # Application metadata
    app_id: Optional[str] = None
    app_name: Optional[str] = None
    business_unit: Optional[str] = None
    owner: Optional[str] = None

    # Business context
    criticality: Optional[BusinessCriticality] = None
    compliance_tags: List[str] = []

    # Database specifics
    db_engine: Optional[str] = None
    db_ha_mode: Optional[str] = None

    # Licensing
    license_model: Optional[str] = None
    license_product: Optional[str] = None
    license_notes: Optional[str] = None

    # Utilization
    avg_cpu: Optional[float] = None
    avg_mem: Optional[float] = None
    avg_io: Optional[float] = None
    utilization_band: Optional[UtilizationBand] = None

    # Arbitrary extra attributes from ingestion
    attributes: Dict[str, Any] = {}


class TopologyEdge(BaseModel):
    id: str
    kind: EdgeKind
    source_id: str
    target_id: str
    description: Optional[str] = None
    attributes: Dict[str, Any] = {}


class TopologyGraph(BaseModel):
    run_id: str
    nodes: Dict[str, TopologyNode]
    edges: List[TopologyEdge]


# -------------------------------------------------------------------
# Diagram model (what gets rendered as draw.io)
# -------------------------------------------------------------------


class DiagramGroup(BaseModel):
    id: str
    label: Optional[str] = None
    group_type: Optional[str] = None  # e.g., aws_account, vpc, subnet, rg, etc.
    parent_group_id: Optional[str] = None


class DiagramNode(BaseModel):
    id: str
    label: Optional[str] = None
    parent_group_id: Optional[str] = None

    # Which icon to use in draw.io exporter (aws.ec2, azure.vm, etc.)
    icon_key: Optional[str] = None

    # Overlays / badges
    is_critical: bool = False
    compliance_tags: List[str] = []
    utilization_band: Optional[UtilizationBand] = None
    licensing_badge: Optional[str] = None

    # Source vs target distinction
    is_target: bool = False             # True for synthesized target-cloud resources
    source_node_id: Optional[str] = None  # TopologyNode.id this target represents

    # Logical layer placement for layout
    layer: Optional[DiagramLayer] = None

    # Arbitrary metadata (used for future rules, hints, etc.)
    attributes: Dict[str, Any] = {}


class DiagramEdge(BaseModel):
    id: str
    source_id: str
    target_id: str
    label: Optional[str] = None
    style: Optional[str] = None
    attributes: Dict[str, Any] = {}


class DiagramSpec(BaseModel):
    cloud: CloudProvider
    diagram_type: DiagramType
    title: Optional[str] = None

    groups: List[DiagramGroup]
    nodes: List[DiagramNode]
    edges: List[DiagramEdge]

    metadata: Dict[str, Any] = {}
