from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db import get_db

router = APIRouter(prefix="/v1/runs", tags=["runs"])


def get_server_summary(db: Session, run_id: str) -> dict:
    """
    Aggregate server metrics for a given run_id.
    """
    row = db.execute(
        text(
            """
            SELECT
              COUNT(*) AS server_count,
              COALESCE(SUM(cpu_cores), 0) AS total_cpu_cores,
              COALESCE(SUM(COALESCE(ram_gb, memory_gb)), 0) AS total_ram_gb
            FROM servers
            WHERE run_id = :run_id
            """
        ),
        {"run_id": run_id},
    ).one()

    server_count = int(row.server_count)
    total_cpu_cores = int(row.total_cpu_cores) if row.total_cpu_cores is not None else 0
    total_ram_gb = float(row.total_ram_gb) if row.total_ram_gb is not None else 0.0

    return {
        "server_count": server_count,
        "total_cpu_cores": total_cpu_cores,
        "total_ram_gb": total_ram_gb,
    }


def get_storage_summary(db: Session, run_id: str) -> dict:
    """
    Aggregate storage metrics for a given run_id.
    """
    totals_row = db.execute(
        text(
            """
            SELECT
              COUNT(*) AS volume_count,
              COALESCE(SUM(size_gb), 0) AS total_gb
            FROM storage
            WHERE run_id = :run_id
            """
        ),
        {"run_id": run_id},
    ).one()

    volume_count = int(totals_row.volume_count)
    total_gb = float(totals_row.total_gb) if totals_row.total_gb is not None else 0.0

    type_rows = db.execute(
        text(
            """
            SELECT
              type AS storage_type,
              COUNT(*) AS volume_count,
              COALESCE(SUM(size_gb), 0) AS total_gb
            FROM storage
            WHERE run_id = :run_id
            GROUP BY type
            ORDER BY type
            """
        ),
        {"run_id": run_id},
    ).fetchall()

    by_type = [
        {
            "storage_type": r.storage_type,
            "volume_count": int(r.volume_count),
            "total_gb": float(r.total_gb),
        }
        for r in type_rows
    ]

    return {
        "volume_count": volume_count,
        "total_gb": total_gb,
        "by_type": by_type,
    }


def get_network_summary(db: Session, run_id: str) -> dict:
    """
    Aggregate basic network metrics for a given run_id
    from the inventory_networks table.
    """
    row = db.execute(
        text(
            """
            SELECT
              COUNT(*) AS device_count,
              COUNT(DISTINCT site) AS site_count,
              COUNT(DISTINCT vlan) AS vlan_count
            FROM inventory_networks
            WHERE run_id = :run_id
            """
        ),
        {"run_id": run_id},
    ).one()

    device_count = int(row.device_count)
    site_count = int(row.site_count)
    vlan_count = int(row.vlan_count)

    return {
        "device_count": device_count,
        "site_count": site_count,
        "vlan_count": vlan_count,
    }


@router.get("/{run_id}/summary")
def get_run_summary(run_id: str, db: Session = Depends(get_db)):
    """
    High-level summary for a run.

    Includes servers + storage + basic network footprint.
    """
    server_summary = get_server_summary(db, run_id)
    storage_summary = get_storage_summary(db, run_id)
    network_summary = get_network_summary(db, run_id)

    # Preserve the "no ingested data" behavior when everything is empty
    if (
        server_summary["server_count"] == 0
        and storage_summary["volume_count"] == 0
        and network_summary["device_count"] == 0
    ):
        raise HTTPException(
            status_code=404,
            detail=f"Run {run_id} has no ingested data",
        )

    return {
        "run_id": run_id,
        "servers": server_summary,
        "storage": storage_summary,
        "network": network_summary,
    }
