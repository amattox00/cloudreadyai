from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db import get_db

router = APIRouter(prefix="/v1/runs", tags=["runs"])


def get_server_problems(db: Session, run_id: str) -> dict:
    """
    Server health checks for a run:

    - Servers with no CPU defined
    - Servers with no RAM defined
    - Servers with no OS defined
    """
    # No CPU cores
    no_cpu_rows = db.execute(
        text(
            """
            SELECT server_id, hostname
            FROM servers
            WHERE run_id = :run_id
              AND (cpu_cores IS NULL OR cpu_cores <= 0)
            """
        ),
        {"run_id": run_id},
    ).fetchall()

    servers_without_cpu = [
        {"server_id": r.server_id, "hostname": r.hostname}
        for r in no_cpu_rows
    ]

    # No RAM (ram_gb or memory_gb)
    no_ram_rows = db.execute(
        text(
            """
            SELECT server_id, hostname
            FROM servers
            WHERE run_id = :run_id
              AND COALESCE(ram_gb, memory_gb) IS NULL
            """
        ),
        {"run_id": run_id},
    ).fetchall()

    servers_without_ram = [
        {"server_id": r.server_id, "hostname": r.hostname}
        for r in no_ram_rows
    ]

    # No OS
    no_os_rows = db.execute(
        text(
            """
            SELECT server_id, hostname
            FROM servers
            WHERE run_id = :run_id
              AND (os IS NULL OR os = '')
            """
        ),
        {"run_id": run_id},
    ).fetchall()

    servers_without_os = [
        {"server_id": r.server_id, "hostname": r.hostname}
        for r in no_os_rows
    ]

    return {
        "servers_without_cpu": servers_without_cpu,
        "servers_without_ram": servers_without_ram,
        "servers_without_os": servers_without_os,
    }


def get_storage_problems(
    db: Session,
    run_id: str,
    oversized_threshold_gb: int = 2048,
) -> dict:
    """
    Storage health checks for a run:

    - Volumes with no server_id
    - Oversized volumes above a configurable threshold
    """
    no_server_rows = db.execute(
        text(
            """
            SELECT storage_id
            FROM storage
            WHERE run_id = :run_id
              AND (server_id IS NULL OR server_id = '')
            """
        ),
        {"run_id": run_id},
    ).fetchall()

    volumes_without_server = [r.storage_id for r in no_server_rows]

    oversized_rows = db.execute(
        text(
            """
            SELECT storage_id, size_gb
            FROM storage
            WHERE run_id = :run_id
              AND size_gb > :threshold
            ORDER BY size_gb DESC
            """
        ),
        {"run_id": run_id, "threshold": oversized_threshold_gb},
    ).fetchall()

    oversized_volumes = [
        {
            "storage_id": r.storage_id,
            "size_gb": float(r.size_gb),
        }
        for r in oversized_rows
    ]

    return {
        "volumes_without_server": volumes_without_server,
        "oversized_volumes": oversized_volumes,
        "oversized_threshold_gb": oversized_threshold_gb,
    }


def get_network_problems(db: Session, run_id: str) -> dict:
    """
    Network health checks for a run using inventory_networks:

    - Devices without subnet
    - Devices without site
    - Duplicate mgmt_ip addresses
    """
    no_subnet_rows = db.execute(
        text(
            """
            SELECT device_name, mgmt_ip
            FROM inventory_networks
            WHERE run_id = :run_id
              AND (subnet IS NULL OR subnet = '')
            """
        ),
        {"run_id": run_id},
    ).fetchall()

    devices_without_subnet = [
        {"device_name": r.device_name, "mgmt_ip": r.mgmt_ip}
        for r in no_subnet_rows
    ]

    no_site_rows = db.execute(
        text(
            """
            SELECT device_name, mgmt_ip
            FROM inventory_networks
            WHERE run_id = :run_id
              AND (site IS NULL OR site = '')
            """
        ),
        {"run_id": run_id},
    ).fetchall()

    devices_without_site = [
        {"device_name": r.device_name, "mgmt_ip": r.mgmt_ip}
        for r in no_site_rows
    ]

    dup_ip_rows = db.execute(
        text(
            """
            SELECT mgmt_ip, COUNT(*) AS cnt
            FROM inventory_networks
            WHERE run_id = :run_id
              AND mgmt_ip IS NOT NULL
              AND mgmt_ip <> ''
            GROUP BY mgmt_ip
            HAVING COUNT(*) > 1
            ORDER BY cnt DESC
            """
        ),
        {"run_id": run_id},
    ).fetchall()

    duplicate_mgmt_ips = [
        {"mgmt_ip": r.mgmt_ip, "count": int(r.cnt)}
        for r in dup_ip_rows
    ]

    return {
        "devices_without_subnet": devices_without_subnet,
        "devices_without_site": devices_without_site,
        "duplicate_mgmt_ips": duplicate_mgmt_ips,
    }


@router.get("/{run_id}/problems")
def get_run_problems(run_id: str, db: Session = Depends(get_db)):
    """
    Aggregated problem view for a run.

    Includes:
      - server issues
      - storage issues
      - network issues
    """
    server_problems = get_server_problems(db, run_id)
    storage_problems = get_storage_problems(db, run_id)
    network_problems = get_network_problems(db, run_id)

    return {
        "run_id": run_id,
        "servers": server_problems,
        "storage": storage_problems,
        "network": network_problems,
    }
