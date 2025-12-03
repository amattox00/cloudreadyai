import csv
from pathlib import Path
from typing import Dict, List

from sqlalchemy.orm import Session
from sqlalchemy import text


class NetworkIngestError(Exception):
    """Custom exception for network ingestion errors."""


def _validate_headers(fieldnames: List[str]) -> None:
    """
    Ensure the CSV has the columns we expect.

    Expected headers:
      device_name, device_type, role, mgmt_ip, site, vlan, subnet
    """
    required = {"device_name", "device_type", "role", "mgmt_ip", "site", "vlan", "subnet"}
    present = set(fieldnames or [])
    missing = required - present
    if missing:
        raise NetworkIngestError(
            f"CSV missing required columns: {', '.join(sorted(missing))}"
        )


def ingest_network_csv(db: Session, run_id: str, csv_path: str) -> Dict[str, int]:
    """
    Ingest a network inventory CSV into the inventory_networks table.

    CSV headers:
      device_name, device_type, role, mgmt_ip, site, vlan, subnet

    DB table: inventory_networks
      id           INTEGER (PK, auto)
      run_id       VARCHAR
      device_name  VARCHAR
      device_type  VARCHAR
      role         VARCHAR
      mgmt_ip      VARCHAR
      site         VARCHAR
      vlan         VARCHAR
      subnet       VARCHAR
    """
    path = Path(csv_path)

    if not path.exists():
        raise FileNotFoundError(f"Network CSV not found: {csv_path}")

    rows_read = 0
    rows_created = 0
    rows_skipped = 0
    rows_error = 0
    rows_updated = 0  # not doing updates in this version

    insert_stmt = text(
        """
        INSERT INTO inventory_networks (
            run_id,
            device_name,
            device_type,
            role,
            mgmt_ip,
            site,
            vlan,
            subnet
        )
        VALUES (
            :run_id,
            :device_name,
            :device_type,
            :role,
            :mgmt_ip,
            :site,
            :vlan,
            :subnet
        )
        """
    )

    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        _validate_headers(reader.fieldnames)

        for row in reader:
            rows_read += 1
            if not row:
                rows_skipped += 1
                continue

            try:
                device_name = (row.get("device_name") or "").strip()
                device_type = (row.get("device_type") or "").strip()
                role = (row.get("role") or "").strip()
                mgmt_ip = (row.get("mgmt_ip") or "").strip()
                site = (row.get("site") or "").strip()
                vlan = (row.get("vlan") or "").strip()
                subnet = (row.get("subnet") or "").strip()

                # Require at least device_name or mgmt_ip to consider it a valid row
                if not device_name and not mgmt_ip:
                    rows_skipped += 1
                    continue

                params = {
                    "run_id": run_id,
                    "device_name": device_name,
                    "device_type": device_type,
                    "role": role,
                    "mgmt_ip": mgmt_ip,
                    "site": site,
                    "vlan": vlan,
                    "subnet": subnet,
                }

                db.execute(insert_stmt, params)
                rows_created += 1

            except Exception as e:
                print(f"[network ingest] error on row {rows_read}: {e!r}")
                rows_error += 1
                continue

    db.commit()

    return {
        "rows_read": rows_read,
        "rows_created": rows_created,
        "rows_updated": rows_updated,
        "rows_skipped": rows_skipped,
        "rows_error": rows_error,
        "rows_ingested": rows_created,
    }
