from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.modules.ingest.base import (
    IngestError,
    read_csv,
    require_run_exists,
)


REQUIRED_FIELDS = {
    "hostname": ["hostname", "server_name", "name"],
    "cpu_cores": ["vcpu", "cpu_count", "cpu_cores", "cpu", "cores"],
    "ram_gb": ["ram_gb", "memory_gb", "memory", "ram"],
}

OPTIONAL_FIELDS = {
    "environment": ["environment", "env"],
    "server_id": ["server_id", "id", "server"],
}


def normalize_header(headers: List[str]) -> Dict[str, Optional[str]]:
    """
    Map canonical fields → actual CSV headers.
    """
    header_map = {}
    lower = {h.lower(): h for h in headers}

    def pick(candidates):
        for c in candidates:
            if c.lower() in lower:
                return lower[c.lower()]
        return None

    # required
    for canonical, variants in REQUIRED_FIELDS.items():
        col = pick(variants)
        if not col:
            raise IngestError(
                f"Missing required column for '{canonical}'. "
                f"Acceptable: {', '.join(variants)}"
            )
        header_map[canonical] = col

    # optional
    for canonical, variants in OPTIONAL_FIELDS.items():
        header_map[canonical] = pick(variants)

    return header_map


def ingest_servers_csv(db: Session, run_id: str, csv_path: str) -> Dict[str, int]:
    """
    Clean, consistent server ingestion pipeline.
    """
    require_run_exists(db, run_id)

    rows = read_csv(csv_path)
    if not rows:
        return {"rows_ingested": 0, "rows_error": 0, "rows_skipped": 0}

    headers = list(rows[0].keys())
    header_map = normalize_header(headers)

    insert_stmt = text("""
        INSERT INTO servers (
            server_id,
            run_id,
            hostname,
            cpu_cores,
            ram_gb,
            environment
        )
        VALUES (
            :server_id,
            :run_id,
            :hostname,
            :cpu_cores,
            :ram_gb,
            :environment
        )
    """)

    ingested = 0
    skipped = 0
    errors = 0

    for row in rows:
        try:
            hostname = row[header_map["hostname"]].strip()
            cpu = row[header_map["cpu_cores"]].strip()
            ram = row[header_map["ram_gb"]].strip()

            if not hostname or not cpu or not ram:
                skipped += 1
                continue

            server_id = None
            if header_map["server_id"]:
                server_id = row.get(header_map["server_id"], "").strip()
            if not server_id:
                server_id = hostname

            environment = None
            if header_map["environment"]:
                environment = row.get(header_map["environment"], "").strip() or None

            params = {
                "server_id": server_id,
                "run_id": run_id,
                "hostname": hostname,
                "cpu_cores": int(cpu),
                "ram_gb": float(ram),
                "environment": environment,
            }

            db.execute(insert_stmt, params)
            ingested += 1

        except Exception:
            errors += 1
            continue

    db.commit()

    return {
        "rows_ingested": ingested,
        "rows_error": errors,
        "rows_skipped": skipped,
    }
