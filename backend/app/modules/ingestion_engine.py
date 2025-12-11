from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from fastapi import UploadFile
from sqlalchemy.orm import Session

# -----------------------------
# v2 ingestion engines (servers + storage)
# -----------------------------

# Servers v2 ingestion: CSV → normalized rows → inventory_servers_v2
from app.modules.ingestion_core.server_ingestion_db_v2 import (
    ingest_servers_v2_from_csv_to_db,
    ServersIngestionSummary,
)

# Storage v2 ingestion: CSV → normalized rows → inventory_storage_v2
from app.modules.ingestion_core.storage_ingestion_db_v2 import (
    ingest_storage_v2_from_csv_to_db,
)

# Run registry – used to increment per-run ingestion counters
from app.routers.runs import increment_ingest_counts


# -----------------------------
# Listed ingestion routes for UI
# -----------------------------

def list_ingest_routes() -> List[Dict[str, str]]:
    """
    Lightweight descriptor of ingest routes.

    For the MVP, servers and storage are exposed via /v1/ingest.
    """
    return [
        {"slice": "servers", "method": "POST", "path": "/v1/ingest/servers"},
        {"slice": "storage", "method": "POST", "path": "/v1/ingest/storage"},
    ]


# -----------------------------
# Shared helper
# -----------------------------

def _write_tmp_upload(file_bytes: bytes, tmp_name: str) -> Path:
    """
    Persist uploaded file bytes to /tmp and return the path.
    """
    tmp_path = Path(f"/tmp/{tmp_name}")
    tmp_path.write_bytes(file_bytes)
    return tmp_path


# -----------------------------
# Servers ingestion (v2)
# -----------------------------

async def ingest_servers(
    db: Session,
    run_id: str,
    file: UploadFile,
) -> Dict[str, Any]:
    """
    Servers ingestion:

    - Save CSV to /tmp
    - Invoke v2 ingestion engine to persist into inventory_servers_v2
    - Update run registry counts
    - Return clean JSON payload
    """

    contents = await file.read()
    tmp_path = _write_tmp_upload(contents, "ingest_servers.csv")

    summary: ServersIngestionSummary = ingest_servers_v2_from_csv_to_db(
        csv_path=str(tmp_path),
        db=db,
        run_id=run_id or "",
    )

    servers_ingested = max(summary.rows_successful, 0)

    increment_ingest_counts(run_id=run_id, servers=servers_ingested)

    return {
        "slice": "servers",
        "run_id": run_id,
        "status": "ok",
        "servers_ingested": servers_ingested,
        "message": f"Servers CSV ingested successfully ({servers_ingested} rows)",
    }


# -----------------------------
# Storage volumes ingestion (v2)
# -----------------------------

async def ingest_storage(
    db: Session,
    run_id: str,
    file: UploadFile,
) -> Dict[str, Any]:
    """
    Storage ingestion (v2-backed):

    - Save CSV to /tmp
    - Invoke v2 storage ingestion engine:
        * parse + validate CSV rows
        * compute utilization
        * write into inventory_storage_v2
    - rows_successful → storage counter
    - Update run registry ingestion counts
    - Return clean JSON payload
    """

    contents = await file.read()
    tmp_path = _write_tmp_upload(contents, "ingest_storage.csv")

    summary = ingest_storage_v2_from_csv_to_db(
        csv_path=str(tmp_path),
        db=db,
        run_id=run_id or "",
    )

    storage_ingested = max(getattr(summary, "rows_successful", 0), 0)

    increment_ingest_counts(run_id=run_id, storage=storage_ingested)

    return {
        "slice": "storage",
        "run_id": run_id,
        "status": "ok",
        "storage_ingested": storage_ingested,
        "message": f"Storage CSV ingested successfully ({storage_ingested} rows)",
    }


# -----------------------------------------
# Placeholders for other ingestion slices
# -----------------------------------------

async def ingest_databases(
    db: Session,
    run_id: str,
    file: UploadFile,
) -> Dict[str, Any]:
    raise NotImplementedError("Databases ingestion is not wired yet.")


async def ingest_applications(
    db: Session,
    run_id: str,
    file: UploadFile,
) -> Dict[str, Any]:
    raise NotImplementedError("Applications ingestion is not wired yet.")


async def ingest_networks(
    db: Session,
    run_id: str,
    file: UploadFile,
) -> Dict[str, Any]:
    raise NotImplementedError("Network ingestion is not wired yet.")


async def ingest_business(
    db: Session,
    run_id: str,
    file: UploadFile,
) -> Dict[str, Any]:
    raise NotImplementedError("Business metadata ingestion is not wired yet.")


async def ingest_dependencies(
    db: Session,
    run_id: str,
    file: UploadFile,
) -> Dict[str, Any]:
    raise NotImplementedError("Dependencies ingestion is not wired yet.")


async def ingest_os_metadata(
    db: Session,
    run_id: str,
    file: UploadFile,
) -> Dict[str, Any]:
    raise NotImplementedError("OS / software metadata ingestion is not wired yet.")


async def ingest_licensing(
    db: Session,
    run_id: str,
    file: UploadFile,
) -> Dict[str, Any]:
    raise NotImplementedError("Licensing ingestion is not wired yet.")


async def ingest_utilization(
    db: Session,
    run_id: str,
    file: UploadFile,
) -> Dict[str, Any]:
    raise NotImplementedError("Utilization ingestion is not wired yet.")

