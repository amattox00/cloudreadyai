from typing import List, Optional

import logging
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import SessionLocal

logger = logging.getLogger(__name__)


def _derive_tier_from_role(role: Optional[str]) -> Optional[str]:
    """
    Very simple mapping from normalized role -> tier label.
    """
    if role is None:
        return None

    r = role.lower()
    if "web" in r or "app" in r:
        return "app"
    if "db" in r or "database" in r:
        return "data"
    if "file" in r or "storage" in r:
        return "storage"
    return None


def _find_dominant_recommendation(
    db: Session, run_id: str, environment: Optional[str], role: Optional[str]
) -> Optional[str]:
    """
    Look into server_rscores and find the most common final_recommendation
    for servers matching (run_id, environment, role).
    """
    row = db.execute(
        text(
            """
            SELECT final_recommendation, COUNT(*) AS cnt
            FROM server_rscores
            WHERE run_id = :run_id
              AND environment IS NOT DISTINCT FROM :environment
              AND role IS NOT DISTINCT FROM :role
            GROUP BY final_recommendation
            ORDER BY cnt DESC
            LIMIT 1
            """
        ),
        {
            "run_id": run_id,
            "environment": environment,
            "role": role,
        },
    ).first()

    if not row:
        return None

    # row[0] is final_recommendation
    return row[0]


def build_workloads_for_run_v2(run_id: str) -> int:
    """
    Build workloads for a run based on normalized v2 server inventory.

    Strategy:
      - Verify the run exists in runs (FK safety).
      - Group servers in inventory_servers_v2 by (environment, role)
      - For each group, compute:
          * server_count
          * avg CPU / RAM / storage utilization (if present)
          * dominant migration pattern from server_rscores
      - Insert one row per group into workloads.

    Returns:
      - Number of workloads created.
    """
    db = SessionLocal()
    try:
        # Ensure the run exists in runs; if not, skip to avoid FK violations.
        run_exists = db.execute(
            text(
                """
                SELECT 1
                FROM runs
                WHERE id = :run_id
                LIMIT 1
                """
            ),
            {"run_id": run_id},
        ).scalar()

        if not run_exists:
            logger.warning(
                "[workload_v2] run '%s' not found in runs table; skipping workload build",
                run_id,
            )
            return 0

        # Remove any previous workloads for this run so operation is idempotent.
        db.execute(
            text(
                """
                DELETE FROM workloads
                WHERE run_id = :run_id
                """
            ),
            {"run_id": run_id},
        )

        # Group servers by environment + role from the v2 inventory.
        groups = db.execute(
            text(
                """
                SELECT
                    environment,
                    role,
                    COUNT(*) AS server_count,
                    AVG(cpu_usage) AS avg_cpu,
                    AVG(ram_usage) AS avg_ram,
                    AVG(storage_usage) AS avg_storage
                FROM inventory_servers_v2
                WHERE run_id = :run_id
                GROUP BY environment, role
                """
            ),
            {"run_id": run_id},
        ).mappings().all()

        workload_count = 0

        for grp in groups:
            environment = grp.get("environment")
            role = grp.get("role")
            server_count = int(grp.get("server_count") or 0)
            avg_cpu = grp.get("avg_cpu")
            avg_ram = grp.get("avg_ram")
            avg_storage = grp.get("avg_storage")

            # Skip empty groups just in case.
            if server_count <= 0:
                continue

            # Build a human-friendly workload name.
            env_label = environment or "unknown"
            role_label = role or "unclassified"
            name = f"{role_label} ({env_label})"

            tier = _derive_tier_from_role(role)
            migration_pattern = _find_dominant_recommendation(
                db, run_id, environment, role
            )

            # Insert into workloads. Many fields are optional and can be NULL.
            db.execute(
                text(
                    """
                    INSERT INTO workloads (
                        run_id,
                        name,
                        environment,
                        tier,
                        criticality,
                        cpu_cores,
                        memory_gb,
                        storage_gb,
                        utilization_cpu,
                        utilization_memory,
                        monthly_cost_estimate,
                        migration_risk,
                        migration_pattern
                    )
                    VALUES (
                        :run_id,
                        :name,
                        :environment,
                        :tier,
                        :criticality,
                        :cpu_cores,
                        :memory_gb,
                        :storage_gb,
                        :utilization_cpu,
                        :utilization_memory,
                        :monthly_cost_estimate,
                        :migration_risk,
                        :migration_pattern
                    )
                    """
                ),
                {
                    "run_id": run_id,
                    "name": name,
                    "environment": environment,
                    "tier": tier,
                    "criticality": None,
                    "cpu_cores": None,
                    "memory_gb": None,
                    "storage_gb": None,
                    "utilization_cpu": float(avg_cpu) if avg_cpu is not None else None,
                    "utilization_memory": float(avg_ram) if avg_ram is not None else None,
                    "monthly_cost_estimate": None,
                    "migration_risk": None,
                    "migration_pattern": migration_pattern,
                },
            )

            workload_count += 1

        db.commit()
        return workload_count
    finally:
        db.close()
