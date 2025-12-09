import json
import logging
from typing import Dict, Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.modules.analysis.engine.rscore_engine import RScoreEngine

logger = logging.getLogger(__name__)


def _analyze_servers(db: Session, run_id: str) -> Dict[str, Any]:
    """
    Analyze the 'servers' slice for a run.

    For v2 ingestion we rely on the normalized inventory table:
        inventory_servers_v2

    Columns:
        id, run_id, hostname, role, os, environment,
        cpu_usage, ram_usage, storage_usage

    This function also computes per-server 6R scores via RScoreEngine and
    persists them into server_rscores.
    """

    # ------------------------------------------------------------------
    # Basic counts from inventory_servers_v2
    # ------------------------------------------------------------------
    row_count = db.execute(
        text(
            """
            SELECT COUNT(*) AS cnt
            FROM inventory_servers_v2
            WHERE run_id = :run_id
            """
        ),
        {"run_id": run_id},
    ).scalar() or 0

    def _build_counts(column: str) -> Dict[str, int]:
        # Column names are hard-coded (no user input), so string formatting is safe here.
        sql = f"""
            SELECT {column}, COUNT(*) AS cnt
            FROM inventory_servers_v2
            WHERE run_id = :run_id
            GROUP BY {column}
        """
        rows = db.execute(text(sql), {"run_id": run_id}).all()
        counts: Dict[str, int] = {}
        for value, cnt in rows:
            key = value if value is not None else "unknown"
            counts[str(key)] = int(cnt)
        return counts

    environment_counts = _build_counts("environment")
    role_counts = _build_counts("role")
    os_counts = _build_counts("os")

    # ------------------------------------------------------------------
    # R-Score batch computation for this run
    # ------------------------------------------------------------------
    rscore_engine = RScoreEngine()

    # Fetch per-server fields needed for R-Score.
    server_rows = db.execute(
        text(
            """
            SELECT hostname, role, os, environment, cpu_usage, ram_usage
            FROM inventory_servers_v2
            WHERE run_id = :run_id
            """
        ),
        {"run_id": run_id},
    ).mappings().all()

    # Clear previous per-server scores for this run (idempotent).
    db.execute(
        text("DELETE FROM server_rscores WHERE run_id = :run_id"),
        {"run_id": run_id},
    )

    recommendation_counts: Dict[str, int] = {}
    score_sums: Dict[str, float] = {
        "rehost": 0.0,
        "replatform": 0.0,
        "refactor": 0.0,
        "repurchase": 0.0,
        "retire": 0.0,
        "retain": 0.0,
    }
    num_scored = 0

    for row in server_rows:
        server_data = {
            "hostname": row.get("hostname"),
            "role": row.get("role"),
            "os": row.get("os"),
            "environment": row.get("environment"),
            "cpu_usage": row.get("cpu_usage"),
            "ram_usage": row.get("ram_usage"),
        }

        result = rscore_engine.compute(server_data)
        num_scored += 1

        # Sum scores for averaging later.
        for key in score_sums.keys():
            score_sums[key] += float(result.get(key) or 0.0)

        # Count final recommendation distribution.
        final_rec = (result.get("final_recommendation") or "UNKNOWN").upper()
        recommendation_counts[final_rec] = recommendation_counts.get(final_rec, 0) + 1

        # Persist this server's scores into server_rscores.
        db.execute(
            text(
                """
                INSERT INTO server_rscores (
                    run_id,
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
                )
                VALUES (
                    :run_id,
                    :hostname,
                    :role,
                    :os,
                    :environment,
                    :cpu_usage,
                    :ram_usage,
                    :rehost,
                    :replatform,
                    :refactor,
                    :repurchase,
                    :retire,
                    :retain,
                    :final_recommendation
                )
                """
            ),
            {
                "run_id": run_id,
                "hostname": server_data.get("hostname"),
                "role": server_data.get("role"),
                "os": server_data.get("os"),
                "environment": server_data.get("environment"),
                "cpu_usage": float(server_data.get("cpu_usage") or 0.0),
                "ram_usage": float(server_data.get("ram_usage") or 0.0),
                "rehost": float(result.get("rehost") or 0.0),
                "replatform": float(result.get("replatform") or 0.0),
                "refactor": float(result.get("refactor") or 0.0),
                "repurchase": float(result.get("repurchase") or 0.0),
                "retire": float(result.get("retire") or 0.0),
                "retain": float(result.get("retain") or 0.0),
                "final_recommendation": result.get("final_recommendation"),
            },
        )

    if num_scored > 0:
        average_scores = {
            key: round(score_sums[key] / num_scored, 1) for key in score_sums.keys()
        }
    else:
        average_scores = {key: 0.0 for key in score_sums.keys()}

    rscore_summary = {
        "num_scored": num_scored,
        "distribution": recommendation_counts,
        "average_scores": average_scores,
    }

    return {
        "row_count": int(row_count),
        "environment_counts": environment_counts,
        "role_counts": role_counts,
        "os_counts": os_counts,
        "rscore_summary": rscore_summary,
    }


def _analyze_apps(db: Session, run_id: str) -> Dict[str, Any]:
    """
    Analyze the 'apps' slice based on the applications table.
    """

    row_count = db.execute(
        text(
            """
            SELECT COUNT(*) AS cnt
            FROM applications
            WHERE run_id = :run_id
            """
        ),
        {"run_id": run_id},
    ).scalar() or 0

    rows = db.execute(
        text(
            """
            SELECT environment, COUNT(*) AS cnt
            FROM applications
            WHERE run_id = :run_id
            GROUP BY environment
            """
        ),
        {"run_id": run_id},
    ).all()

    env_counts: Dict[str, int] = {}
    for env, cnt in rows:
        key = env if env is not None else "unknown"
        env_counts[str(key)] = int(cnt)

    return {
        "row_count": int(row_count),
        "env_counts": env_counts,
    }


def _analyze_networks(db: Session, run_id: str) -> Dict[str, Any]:
    """
    Analyze the 'networks' slice based on the networks table.
    """

    row_count = db.execute(
        text(
            """
            SELECT COUNT(*) AS cnt
            FROM networks
            WHERE run_id = :run_id
            """
        ),
        {"run_id": run_id},
    ).scalar() or 0

    return {
        "row_count": int(row_count),
    }


def _analyze_storage(db: Session, run_id: str) -> Dict[str, Any]:
    """
    Analyze the 'storage' slice based on the storage table.

    Assumes a numeric column size_gb exists on the storage table.
    """

    row_count = db.execute(
        text(
            """
            SELECT COUNT(*) AS cnt
            FROM storage
            WHERE run_id = :run_id
            """
        ),
        {"run_id": run_id},
    ).scalar() or 0

    total_size = db.execute(
        text(
            """
            SELECT COALESCE(SUM(size_gb), 0.0) AS total_gb
            FROM storage
            WHERE run_id = :run_id
            """
        ),
        {"run_id": run_id},
    ).scalar() or 0.0

    return {
        "row_count": int(row_count),
        "total_size_gb": float(total_size or 0.0),
    }


def _upsert_run_slice_metric(
    db: Session,
    run_id: str,
    slice_name: str,
    row_count: int,
    metrics: Dict[str, Any],
) -> None:
    """
    Upsert into run_slice_metrics using plain SQL.

    Table columns (based on schema):
        id, run_id, slice_name, row_count, metrics_json
    """

    existing_id = db.execute(
        text(
            """
            SELECT id
            FROM run_slice_metrics
            WHERE run_id = :run_id
              AND slice_name = :slice_name
            ORDER BY id ASC
            LIMIT 1
            """
        ),
        {"run_id": run_id, "slice_name": slice_name},
    ).scalar()

    metrics_json = json.dumps(metrics)

    if existing_id is not None:
        db.execute(
            text(
                """
                UPDATE run_slice_metrics
                SET row_count = :row_count,
                    metrics_json = :metrics_json
                WHERE id = :id
                """
            ),
            {
                "id": existing_id,
                "row_count": row_count,
                "metrics_json": metrics_json,
            },
        )
    else:
        db.execute(
            text(
                """
                INSERT INTO run_slice_metrics (run_id, slice_name, row_count, metrics_json)
                VALUES (:run_id, :slice_name, :row_count, :metrics_json)
                """
            ),
            {
                "run_id": run_id,
                "slice_name": slice_name,
                "row_count": row_count,
                "metrics_json": metrics_json,
            },
        )


def analyze_ingest_slice(run_id: str, slice_name: str) -> None:
    """
    Background job that computes metrics per slice and stores them
    in run_slice_metrics as a single JSON document per (run_id, slice_name).
    """
    db = SessionLocal()
    try:
        if slice_name == "servers":
            metrics = _analyze_servers(db, run_id)
        elif slice_name == "apps":
            metrics = _analyze_apps(db, run_id)
        elif slice_name == "networks":
            metrics = _analyze_networks(db, run_id)
        elif slice_name == "storage":
            metrics = _analyze_storage(db, run_id)
        else:
            logger.warning("[analysis] Unknown slice '%s' for run=%s", slice_name, run_id)
            return

        row_count = int(metrics.get("row_count", 0))

        _upsert_run_slice_metric(
            db=db,
            run_id=run_id,
            slice_name=slice_name,
            row_count=row_count,
            metrics=metrics,
        )

        db.commit()
        logger.info(
            "[analysis] run=%s slice=%s metrics=%s",
            run_id,
            slice_name,
            metrics,
        )
    finally:
        db.close()
