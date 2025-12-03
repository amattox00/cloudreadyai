from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db import get_db

router = APIRouter(
    prefix="/v1/runs",
    tags=["run-summary-v2"],
)


def _get_single_row(db: Session, sql: str, params: dict):
    result = db.execute(text(sql), params)
    row = result.mappings().first()
    if row is None:
        return None
    return dict(row)


def _get_multi_rows(db: Session, sql: str, params: dict):
    result = db.execute(text(sql), params)
    return [dict(r) for r in result.mappings().all()]


# --- SERVERS (backed by inventory_servers) ------------------------------------


def get_servers_summary(db: Session, run_id: str) -> dict:
    """
    Servers summary for a run, based on the inventory_servers table.

    inventory_servers columns (from your psql output):
      run_id, hostname, environment, os_name, cpu_count, memory_gb
    """

    agg = _get_single_row(
        db,
        """
        SELECT
          COUNT(*) AS server_count,
          COALESCE(SUM(cpu_count), 0) AS total_cpu_cores,
          COALESCE(SUM(memory_gb), 0) AS total_ram_gb
        FROM inventory_servers
        WHERE run_id = :run_id
        """,
        {"run_id": run_id},
    ) or {"server_count": 0, "total_cpu_cores": 0, "total_ram_gb": 0}

    envs = _get_multi_rows(
        db,
        """
        SELECT
          COALESCE(NULLIF(environment, ''), 'unknown') AS environment,
          COUNT(*) AS count
        FROM inventory_servers
        WHERE run_id = :run_id
        GROUP BY COALESCE(NULLIF(environment, ''), 'unknown')
        ORDER BY environment
        """,
        {"run_id": run_id},
    )

    return {
        "totals": agg,
        "by_environment": envs,
    }


# --- PLACEHOLDER / SAFE STUBS FOR OTHER SLICES --------------------------------
# These are intentionally conservative so we don't crash on schema mismatches
# while the ingestion modules for those slices are still evolving.


def get_storage_summary(db: Session, run_id: str) -> dict:
    # TODO: Wire to real storage table once schema is finalized
    return {
        "totals": {
            "volume_count": 0,
            "total_size_gb": 0,
        },
        "by_type": [],
    }


def get_network_summary(db: Session, run_id: str) -> dict:
    # TODO: Wire to inventory_networks once stable
    return {
        "device_count": 0,
    }


def get_databases_summary(db: Session, run_id: str) -> dict:
    # TODO: Wire to databases table once stable
    return {
        "totals": {
            "db_count": 0,
            "total_db_size_gb": 0,
        },
        "by_type": [],
    }


def get_applications_summary(db: Session, run_id: str) -> dict:
    # TODO: Wire to applications + business metadata tables
    return {
        "totals": {
            "app_count": 0,
        },
        "by_business_unit": [],
        "by_criticality": [],
    }


def get_business_metadata_summary(db: Session, run_id: str) -> dict:
    return {
        "by_sla_tier": [],
        "by_criticality": [],
    }


def get_dependencies_summary(db: Session, run_id: str) -> dict:
    return {
        "dependency_count": 0,
        "apps_with_dependencies": 0,
    }


def get_os_summary(db: Session, run_id: str) -> dict:
    return {
        "by_family": [],
        "by_name": [],
    }


def get_licensing_summary(db: Session, run_id: str) -> dict:
    return {
        "by_vendor": [],
        "by_product": [],
    }


def get_utilization_summary(db: Session, run_id: str) -> dict:
    return {
        "servers_with_metrics": 0,
        "avg_cpu_avg": 0,
        "avg_cpu_peak": 0,
        "avg_ram_avg_gb": 0,
        "avg_ram_peak_gb": 0,
    }


@router.get("/{run_id}/summary/v2")
def get_run_summary_v2(run_id: str, db: Session = Depends(get_db)):
    """
    Unified Phase C-style summary for a run, backed by inventory_servers.

    For now, we:
      - Consider a run "existent" if it has rows in inventory_servers.
      - Return real data for servers.
      - Return safe placeholder structures for other slices.
    """

    # Check if this run_id appears in inventory_servers
    core_row = db.execute(
        text(
            """
            SELECT 1
            FROM inventory_servers
            WHERE run_id = :run_id
            LIMIT 1
            """
        ),
        {"run_id": run_id},
    ).first()

    if not core_row:
        raise HTTPException(status_code=404, detail=f"No data found for run {run_id}")

    servers = get_servers_summary(db, run_id)
    storage = get_storage_summary(db, run_id)
    network = get_network_summary(db, run_id)
    databases = get_databases_summary(db, run_id)
    applications = get_applications_summary(db, run_id)
    business = get_business_metadata_summary(db, run_id)
    dependencies = get_dependencies_summary(db, run_id)
    osinfo = get_os_summary(db, run_id)
    licensing = get_licensing_summary(db, run_id)
    utilization = get_utilization_summary(db, run_id)

    return {
        "run_id": run_id,
        "servers": servers,
        "storage": storage,
        "network": network,
        "databases": databases,
        "applications": applications,
        "business": business,
        "dependencies": dependencies,
        "os": osinfo,
        "licensing": licensing,
        "utilization": utilization,
    }
