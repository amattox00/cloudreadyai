import json
from typing import Any, Dict, List, Optional

from sqlalchemy import text

from app.db import SessionLocal


def get_servers_slice_summary(run_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch the 'servers' slice summary for a run from run_slice_metrics.

    Returns a dict like:
    {
        "row_count": 2,
        "environment_counts": {...},
        "role_counts": {...},
        "os_counts": {...},
        "rscore_summary": {...}
    }
    or None if no metrics are present.
    """
    db = SessionLocal()
    try:
        row = db.execute(
            text(
                """
                SELECT row_count, metrics_json
                FROM run_slice_metrics
                WHERE run_id = :run_id
                  AND slice_name = 'servers'
                ORDER BY id DESC
                LIMIT 1
                """
            ),
            {"run_id": run_id},
        ).first()

        if not row:
            return None

        row_count = int(row[0] or 0)
        raw_metrics = row[1]

        # metrics_json might already be a dict (JSONB) or a JSON string.
        if isinstance(raw_metrics, (dict, list)):
            metrics = raw_metrics
        elif isinstance(raw_metrics, (str, bytes, bytearray)):
            metrics = json.loads(raw_metrics or "{}")
        else:
            metrics = {}

        # Ensure row_count is present and consistent.
        metrics["row_count"] = row_count
        return metrics
    finally:
        db.close()


def get_server_rscores(run_id: str) -> List[Dict[str, Any]]:
    """
    Return per-server 6R scores and final recommendation for a run.

    Each element looks like:
    {
        "hostname": "...",
        "role": "...",
        "os": "...",
        "environment": "...",
        "cpu_usage": 0.0,
        "ram_usage": 0.0,
        "rehost": 45.0,
        "replatform": 55.0,
        "refactor": 30.0,
        "repurchase": 10.0,
        "retire": 16.0,
        "retain": 12.5,
        "final_recommendation": "REPLATFORM",
    }
    """
    db = SessionLocal()
    try:
        rows = db.execute(
            text(
                """
                SELECT
                    hostname,
                    role,
                    os,
                    environment,
                    cpu_usage,
                    ram_usage,
                    rehost,
                    replatform,
                    refactor,
                    repurchase,
                    retire,
                    retain,
                    final_recommendation
                FROM server_rscores
                WHERE run_id = :run_id
                ORDER BY hostname
                """
            ),
            {"run_id": run_id},
        ).mappings().all()

        results: List[Dict[str, Any]] = []
        for r in rows:
            results.append(
                {
                    "hostname": r.get("hostname"),
                    "role": r.get("role"),
                    "os": r.get("os"),
                    "environment": r.get("environment"),
                    "cpu_usage": float(r.get("cpu_usage") or 0.0)
                    if r.get("cpu_usage") is not None
                    else None,
                    "ram_usage": float(r.get("ram_usage") or 0.0)
                    if r.get("ram_usage") is not None
                    else None,
                    "rehost": float(r.get("rehost") or 0.0),
                    "replatform": float(r.get("replatform") or 0.0),
                    "refactor": float(r.get("refactor") or 0.0),
                    "repurchase": float(r.get("repurchase") or 0.0),
                    "retire": float(r.get("retire") or 0.0),
                    "retain": float(r.get("retain") or 0.0),
                    "final_recommendation": r.get("final_recommendation"),
                }
            )

        return results
    finally:
        db.close()


def get_workloads_summary(run_id: str) -> List[Dict[str, Any]]:
    """
    Return workload-level summary rows for a run from the workloads table.

    Each element looks like:
    {
        "id": 1,
        "name": "web (prod)",
        "environment": "prod",
        "tier": "app",
        "utilization_cpu": 35.0,
        "utilization_memory": 40.0,
        "migration_pattern": "REPLATFORM",
    }

    Works for both legacy and v2-built workloads, as long as they share the same schema.
    """
    db = SessionLocal()
    try:
        rows = db.execute(
            text(
                """
                SELECT
                    id,
                    name,
                    environment,
                    tier,
                    utilization_cpu,
                    utilization_memory,
                    migration_pattern
                FROM workloads
                WHERE run_id = :run_id
                ORDER BY id
                """
            ),
            {"run_id": run_id},
        ).mappings().all()

        results: List[Dict[str, Any]] = []
        for r in rows:
            results.append(
                {
                    "id": r.get("id"),
                    "name": r.get("name"),
                    "environment": r.get("environment"),
                    "tier": r.get("tier"),
                    "utilization_cpu": float(r.get("utilization_cpu"))
                    if r.get("utilization_cpu") is not None
                    else None,
                    "utilization_memory": float(r.get("utilization_memory"))
                    if r.get("utilization_memory") is not None
                    else None,
                    "migration_pattern": r.get("migration_pattern"),
                }
            )

        return results
    finally:
        db.close()
