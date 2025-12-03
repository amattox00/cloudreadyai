"""
calculator.py

AWS TCO calculator for a single assessment run.

Reads normalized inventory from the database and applies
our region-aware pricing model from aws_pricing.py.

Output shape matches what the Cost & TCO page expects:
- top-level monthly/annual numbers
- 1-year / 3-year modeled discounts
- per-server EC2 costs
- per-volume EBS costs
- NAT + RDS placeholders
"""

from __future__ import annotations

from typing import Any, Dict, List

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.modules.tco import aws_pricing

# Very simple “what-if” discounts vs. On-Demand
DISCOUNT_1YR = 0.75
DISCOUNT_3YR = 0.45


def _fetch_servers(db: Session, run_id: str):
    """
    Fetch servers for a run.

    NOTE: The physical column is cpu_cores, which we alias as vcpu
    so the rest of the code can treat it like vCPU.
    """
    sql = text(
        """
        SELECT
            server_id,
            hostname,
            cpu_cores AS vcpu,
            ram_gb
        FROM servers
        WHERE run_id = :run_id
        ORDER BY hostname, server_id
        """
    )
    return db.execute(sql, {"run_id": run_id}).fetchall()


def _fetch_storage(db: Session, run_id: str):
    sql = text(
        """
        SELECT
            storage_id,
            server_id,
            size_gb,
            storage_type
        FROM storage
        WHERE run_id = :run_id
        ORDER BY server_id, storage_id
        """
    )
    return db.execute(sql, {"run_id": run_id}).fetchall()


def calculate_aws_tco(db: Session, run_id: str, region: str) -> Dict[str, Any]:
    """
    Core entry point used by the /v1/tco/aws/{run_id} endpoint.

    Returns a JSON-serializable dict.
    """
    # Validate region / normalize
    region_code = aws_pricing.normalize_region(region)

    servers = _fetch_servers(db, run_id)
    storage = _fetch_storage(db, run_id)

    # ------------------------------------------------------------------
    # Compute (EC2)
    # ------------------------------------------------------------------
    compute_items: List[Dict[str, Any]] = []
    compute_monthly_total = 0.0

    for row in servers:
        server_id = row.server_id
        hostname = row.hostname or server_id
        vcpu = row.vcpu or 0
        ram_gb = row.ram_gb or 0

        instance_type = aws_pricing.map_server_to_instance(vcpu, ram_gb)
        monthly_ec2 = aws_pricing.get_ec2_monthly(instance_type, region_code)

        compute_monthly_total += monthly_ec2

        compute_items.append(
            {
                "server_id": server_id,
                "hostname": hostname,
                "vcpu": vcpu,
                "ram_gb": ram_gb,
                "aws_instance": instance_type,
                "monthly_cost": round(monthly_ec2, 2),
            }
        )

    # ------------------------------------------------------------------
    # Storage (EBS)
    # ------------------------------------------------------------------
    storage_items: List[Dict[str, Any]] = []
    storage_monthly_total = 0.0

    for row in storage:
        volume_id = row.storage_id
        server_id = row.server_id
        size_gb = float(row.size_gb or 0)
        storage_type = row.storage_type or "gp3"

        gb_price = aws_pricing.get_ebs_price(storage_type, region_code)
        monthly_ebs = size_gb * gb_price

        storage_monthly_total += monthly_ebs

        storage_items.append(
            {
                "volume_id": volume_id,
                "server_id": server_id,
                "storage_type": storage_type,
                "size_gb": size_gb,
                "monthly_cost": round(monthly_ebs, 2),
            }
        )

    # If literally nothing came back, surface a clear error
    if not compute_items and not storage_items:
        raise ValueError(f"No servers or storage found for run_id={run_id}")

    # ------------------------------------------------------------------
    # NAT / RDS placeholders
    # ------------------------------------------------------------------
    nat_monthly = aws_pricing.get_nat_gateway_monthly(region_code, num_gateways=1)
    rds_monthly = 0.0  # we can wire real RDS later

    # ------------------------------------------------------------------
    # Roll up totals & modeled discounts
    # ------------------------------------------------------------------
    monthly_ondemand = compute_monthly_total + storage_monthly_total + nat_monthly + rds_monthly

    monthly_1yr = monthly_ondemand * DISCOUNT_1YR
    monthly_3yr = monthly_ondemand * DISCOUNT_3YR

    result: Dict[str, Any] = {
        "run_id": run_id,
        "region": region_code,
        "monthly_ondemand": round(monthly_ondemand, 2),
        "annual_ondemand": round(monthly_ondemand * 12.0, 2),
        "monthly_1yr": round(monthly_1yr, 2),
        "annual_1yr": round(monthly_1yr * 12.0, 2),
        "monthly_3yr": round(monthly_3yr, 2),
        "annual_3yr": round(monthly_3yr * 12.0, 2),
        "nat_gateway_cost": round(nat_monthly, 2),
        "rds_cost": round(rds_monthly, 2),
        "compute_monthly_total": round(compute_monthly_total, 2),
        "storage_monthly_total": round(storage_monthly_total, 2),
        "compute": compute_items,
        "storage": storage_items,
    }

    return result
