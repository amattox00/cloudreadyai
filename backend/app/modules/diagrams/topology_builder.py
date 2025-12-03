from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class Node:
    id: str
    label: str
    x: int
    y: int
    width: int = 160
    height: int = 60
    parent: str | None = None
    # style is a generic dict that drawio_exporter can turn into a style string.
    # For now we mostly leave this as None so you get clean rectangles.
    style: Dict[str, Any] | None = None


@dataclass
class Edge:
    id: str
    source: str
    target: str
    label: str | None = None
    style: Dict[str, Any] | None = None


@dataclass
class DiagramSpec:
    id: str
    nodes: List[Node] = field(default_factory=list)
    edges: List[Edge] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _node(
    node_id: str,
    label: str,
    x: int,
    y: int,
    width: int = 160,
    height: int = 60,
    parent: str | None = None,
    style: Dict[str, Any] | None = None,
) -> Node:
    return Node(
        id=node_id,
        label=label,
        x=x,
        y=y,
        width=width,
        height=height,
        parent=parent,
        style=style,
    )


def _edge(
    edge_id: str,
    source: str,
    target: str,
    label: str | None = None,
    style: Dict[str, Any] | None = None,
) -> Edge:
    return Edge(
        id=edge_id,
        source=source,
        target=target,
        label=label,
        style=style,
    )


# ---------------------------------------------------------------------------
# Three-tier web application (default)
# ---------------------------------------------------------------------------

def _build_three_tier_app_diagram(run_id: str) -> DiagramSpec:
    """
    Classic 3-tier app:
      Users -> Route 53 -> CloudFront -> ALB -> App Tier (EC2/ASG) -> RDS + S3
      with CloudWatch + GuardDuty off to the side.
    """
    nodes: List[Node] = []
    edges: List[Edge] = []

    # Core flow left to right / top to bottom
    nodes.append(_node("users", "Users", 520, 80))

    nodes.append(_node("route53", "Amazon Route 53", 280, 200))
    nodes.append(_node("cloudfront", "Amazon CloudFront", 520, 200))

    nodes.append(_node("alb", "Application Load Balancer", 520, 320))
    nodes.append(_node("app_tier", "App Tier (EC2 / ASG)", 760, 320))

    nodes.append(_node("rds", "Amazon RDS (App DB)", 760, 440))
    nodes.append(_node("s3_logs", "Amazon S3 (Logs / Backups)", 1000, 440))

    # Observability / security
    nodes.append(_node("cloudwatch", "Amazon CloudWatch", 520, 560))
    nodes.append(_node("guardduty", "Amazon GuardDuty", 760, 560))

    # Core edges
    edges.append(_edge("e_users_cf", "users", "cloudfront"))
    edges.append(_edge("e_r53_cf", "route53", "cloudfront"))
    edges.append(_edge("e_cf_alb", "cloudfront", "alb"))
    edges.append(_edge("e_alb_app", "alb", "app_tier"))
    edges.append(_edge("e_app_rds", "app_tier", "rds"))
    edges.append(_edge("e_app_s3", "app_tier", "s3_logs"))

    # Observability / security edges
    edges.append(_edge("e_rds_cw", "rds", "cloudwatch"))
    edges.append(_edge("e_app_gd", "app_tier", "guardduty"))

    return DiagramSpec(
        id=f"aws_app_topology_default_{run_id or 'run'}",
        nodes=nodes,
        edges=edges,
    )


# ---------------------------------------------------------------------------
# Serverless API application (run_id starts with SERVERLESS)
# ---------------------------------------------------------------------------

def _build_serverless_api_diagram(run_id: str) -> DiagramSpec:
    """
    Serverless API pattern:
      Users -> CloudFront -> (Cognito) -> API Gateway -> Lambda -> DynamoDB
      Static assets in S3, logs/metrics in CloudWatch.
    """
    nodes: List[Node] = []
    edges: List[Edge] = []

    # Top row: users / auth / edge
    nodes.append(_node("users", "Users", 260, 80))
    nodes.append(_node("cf", "Amazon CloudFront", 260, 200))
    nodes.append(_node("cognito", "Amazon Cognito", 520, 200))

    # Middle: API + Lambda + data
    nodes.append(_node("apigw", "Amazon API Gateway", 520, 320))
    nodes.append(_node("lambda", "AWS Lambda", 780, 320))
    nodes.append(_node("ddb", "Amazon DynamoDB", 1040, 320))

    # Static site + logs
    nodes.append(_node("s3_static", "Amazon S3 (Static Site)", 260, 440))
    nodes.append(_node("cloudwatch", "Amazon CloudWatch", 780, 440))

    # Edges
    edges.append(_edge("e_users_cf", "users", "cf"))
    edges.append(_edge("e_cf_cognito", "cf", "cognito"))
    edges.append(_edge("e_cognito_apigw", "cognito", "apigw"))
    edges.append(_edge("e_apigw_lambda", "apigw", "lambda"))
    edges.append(_edge("e_lambda_ddb", "lambda", "ddb"))

    edges.append(_edge("e_cf_s3_static", "cf", "s3_static"))
    edges.append(_edge("e_lambda_cw", "lambda", "cloudwatch"))
    edges.append(_edge("e_apigw_cw", "apigw", "cloudwatch"))

    return DiagramSpec(
        id=f"aws_serverless_api_{run_id or 'run'}",
        nodes=nodes,
        edges=edges,
    )


# ---------------------------------------------------------------------------
# Data lake / analytics pipeline (run_id starts with DATALAKE / DATA_LAKE)
# ---------------------------------------------------------------------------

def _build_data_lake_diagram(run_id: str) -> DiagramSpec:
    """
    Simple data lake pattern:
      Data sources -> Ingestion (Kinesis / DMS) -> S3 Raw -> Glue ETL -> S3 Curated
      -> Athena / Redshift / QuickSight.
    """
    nodes: List[Node] = []
    edges: List[Edge] = []

    # Left: data sources
    nodes.append(_node("src_apps", "App / Microservices\n(Logs, Events)", 200, 200))
    nodes.append(_node("src_db", "On-Prem / RDS DBs", 200, 320))

    # Ingestion
    nodes.append(_node("kinesis", "Amazon Kinesis Data Streams", 480, 200))
    nodes.append(_node("dms", "AWS Database Migration Service", 480, 320))

    # Raw and curated zones
    nodes.append(_node("s3_raw", "Amazon S3\nRaw / Landing Zone", 760, 260))
    nodes.append(_node("glue", "AWS Glue ETL Jobs", 1040, 260))
    nodes.append(_node("s3_curated", "Amazon S3\nCurated Zone", 1320, 260))

    # Analytics consumers
    nodes.append(_node("athena", "Amazon Athena", 1040, 430))
    nodes.append(_node("redshift", "Amazon Redshift", 1320, 430))
    nodes.append(_node("quicksight", "Amazon QuickSight", 1180, 560))

    # Edges: sources -> ingestion
    edges.append(_edge("e_apps_kinesis", "src_apps", "kinesis"))
    edges.append(_edge("e_db_dms", "src_db", "dms"))

    # Ingestion -> raw S3
    edges.append(_edge("e_kinesis_s3_raw", "kinesis", "s3_raw"))
    edges.append(_edge("e_dms_s3_raw", "dms", "s3_raw"))

    # Raw -> Glue -> Curated
    edges.append(_edge("e_s3_raw_glue", "s3_raw", "glue"))
    edges.append(_edge("e_glue_s3_curated", "glue", "s3_curated"))

    # Curated -> analytics
    edges.append(_edge("e_s3_curated_athena", "s3_curated", "athena"))
    edges.append(_edge("e_s3_curated_redshift", "s3_curated", "redshift"))
    edges.append(_edge("e_athena_quicksight", "athena", "quicksight"))
    edges.append(_edge("e_redshift_quicksight", "redshift", "quicksight"))

    return DiagramSpec(
        id=f"aws_data_lake_{run_id or 'run'}",
        nodes=nodes,
        edges=edges,
    )


# ---------------------------------------------------------------------------
# Public entry point used by the router
# ---------------------------------------------------------------------------

def build_app_topology_diagram(run_id: str, cloud: str, view_mode: str) -> DiagramSpec:
    """
    Main entry called by the /v1/diagrams/generate router.

    For now we use the run_id to pick a "scenario":
      - run_id starts with SERVERLESS  -> serverless API pattern
      - run_id starts with DATALAKE / DATA_LAKE -> data lake pattern
      - anything else -> classic three-tier web app
    """
    key = (run_id or "").strip().lower()

    if key.startswith("serverless"):
        return _build_serverless_api_diagram(run_id)

    if key.startswith("datalake") or key.startswith("data_lake") or key.startswith("data-lake"):
        return _build_data_lake_diagram(run_id)

    # Default
    return _build_three_tier_app_diagram(run_id)
def build_diagram_spec(*args, **kwargs):
    """
    Backwards-compat wrapper expected by app.routers.diagrams.

    Older code imports `build_diagram_spec(...)` from this module.
    Newer versions may expose something like `build_topology_spec(...)`
    or similar. This wrapper keeps the import working and delegates if
    a more specific builder exists.
    """
    # If a newer builder exists in this module, delegate to it.
    if "build_topology_spec" in globals():
        return globals()["build_topology_spec"](*args, **kwargs)

    if "build_topology" in globals():
        return globals()["build_topology"](*args, **kwargs)

    # Fallback: return a minimal, empty spec so callers don't crash.
    return {
        "nodes": [],
        "edges": [],
        "metadata": {
            "note": "build_diagram_spec fallback – no topology builder found"
        },
    }
