from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db import get_db

router = APIRouter(prefix="/v1/runs", tags=["runs"])


def _get_server_counts(db: Session, run_id: str) -> dict:
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

    return {
        "server_count": int(row.server_count),
        "total_cpu_cores": int(row.total_cpu_cores) if row.total_cpu_cores is not None else 0,
        "total_ram_gb": float(row.total_ram_gb) if row.total_ram_gb is not None else 0.0,
    }


def _get_storage_counts(db: Session, run_id: str) -> dict:
    row = db.execute(
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

    return {
        "volume_count": int(row.volume_count),
        "total_gb": float(row.total_gb) if row.total_gb is not None else 0.0,
    }


def _get_network_counts(db: Session, run_id: str) -> dict:
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

    return {
        "device_count": int(row.device_count),
        "site_count": int(row.site_count),
        "vlan_count": int(row.vlan_count),
    }


def _get_problem_counts(db: Session, run_id: str) -> dict:
    # Storage problems
    volumes_without_server = db.execute(
        text(
            """
            SELECT COUNT(*) AS cnt
            FROM storage
            WHERE run_id = :run_id
              AND (server_id IS NULL OR server_id = '')
            """
        ),
        {"run_id": run_id},
    ).scalar_one()

    oversized_volumes = db.execute(
        text(
            """
            SELECT COUNT(*) AS cnt
            FROM storage
            WHERE run_id = :run_id
              AND size_gb > :threshold
            """
        ),
        {"run_id": run_id, "threshold": 2048},
    ).scalar_one()

    # Network problems
    devices_without_subnet = db.execute(
        text(
            """
            SELECT COUNT(*) AS cnt
            FROM inventory_networks
            WHERE run_id = :run_id
              AND (subnet IS NULL OR subnet = '')
            """
        ),
        {"run_id": run_id},
    ).scalar_one()

    devices_without_site = db.execute(
        text(
            """
            SELECT COUNT(*) AS cnt
            FROM inventory_networks
            WHERE run_id = :run_id
              AND (site IS NULL OR site = '')
            """
        ),
        {"run_id": run_id},
    ).scalar_one()

    duplicate_mgmt_ips = db.execute(
        text(
            """
            SELECT COUNT(*) AS cnt
            FROM (
              SELECT mgmt_ip
              FROM inventory_networks
              WHERE run_id = :run_id
                AND mgmt_ip IS NOT NULL
                AND mgmt_ip <> ''
              GROUP BY mgmt_ip
              HAVING COUNT(*) > 1
            ) t
            """
        ),
        {"run_id": run_id},
    ).scalar_one()

    return {
        "volumes_without_server": int(volumes_without_server),
        "oversized_volumes": int(oversized_volumes),
        "devices_without_subnet": int(devices_without_subnet),
        "devices_without_site": int(devices_without_site),
        "duplicate_mgmt_ips": int(duplicate_mgmt_ips),
    }


@router.get("/{run_id}/analysis")
def get_run_analysis(run_id: str, db: Session = Depends(get_db)):
    """
    High-level analysis for a run.

    This is a thin Phase C slice that:
      - aggregates infra metrics
      - summarizes problem counts
      - emits a simple list of "risks" / observations
    """
    servers = _get_server_counts(db, run_id)
    storage = _get_storage_counts(db, run_id)
    network = _get_network_counts(db, run_id)
    problems = _get_problem_counts(db, run_id)

    risks = []

    # No servers but we have storage or network
    if servers["server_count"] == 0 and (
        storage["volume_count"] > 0 or network["device_count"] > 0
    ):
        risks.append(
            {
                "code": "NO_SERVER_INVENTORY",
                "severity": "medium",
                "message": "Run has storage/network data but no servers.",
                "details": "Consider ingesting server inventory for a complete view of workloads.",
            }
        )

    # Storage-related risks
    if problems["volumes_without_server"] > 0:
        risks.append(
            {
                "code": "VOLUMES_WITHOUT_SERVER",
                "severity": "high",
                "message": "Some volumes are not mapped to any server.",
                "details": f"{problems['volumes_without_server']} volumes in this run have no server_id.",
            }
        )

    if problems["oversized_volumes"] > 0:
        risks.append(
            {
                "code": "OVERSIZED_VOLUMES",
                "severity": "medium",
                "message": "Some volumes exceed the default 2 TB threshold.",
                "details": f"{problems['oversized_volumes']} volumes larger than 2048 GB detected.",
            }
        )

    # Network-related risks
    if problems["devices_without_subnet"] > 0:
        risks.append(
            {
                "code": "DEVICES_WITHOUT_SUBNET",
                "severity": "low",
                "message": "Some network devices do not have a subnet recorded.",
                "details": f"{problems['devices_without_subnet']} devices missing subnet.",
            }
        )

    if problems["devices_without_site"] > 0:
        risks.append(
            {
                "code": "DEVICES_WITHOUT_SITE",
                "severity": "low",
                "message": "Some network devices do not have a site/location recorded.",
                "details": f"{problems['devices_without_site']} devices missing site.",
            }
        )

    if problems["duplicate_mgmt_ips"] > 0:
        risks.append(
            {
                "code": "DUPLICATE_MANAGEMENT_IPS",
                "severity": "medium",
                "message": "Duplicate management IPs detected in network inventory.",
                "details": f"{problems['duplicate_mgmt_ips']} management IPs are shared by multiple devices.",
            }
        )

    return {
        "run_id": run_id,
        "metrics": {
            "servers": servers,
            "storage": storage,
            "network": network,
        },
        "problem_counts": problems,
        "risks": risks,
    }
