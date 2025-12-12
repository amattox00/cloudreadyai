from __future__ import annotations

import io
from pathlib import Path
from typing import Any, Dict, List

from fastapi import UploadFile
from sqlalchemy.orm import Session

# -----------------------------
# v2 ingestion engines
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

# Databases v2 ingestion:
from app.modules.ingestion_core.databases_ingestion_v2 import (
    ingest_databases_from_csv,
)
from app.modules.ingestion_core.databases_ingestion_db_v2 import (
    persist_database_records_v2,
)

# Applications v2 ingestion:
from app.modules.ingestion_core.applications_ingestion_v2 import (
    ingest_applications_from_csv,
)
from app.modules.ingestion_core.applications_ingestion_db_v2 import (
    persist_application_records_v2,
)

# Dependencies (hardened MVP module)
from app.modules.ingest.dependencies import ingest_dependencies_csv

# Run registry – used to update per-run ingestion counters
from app.routers.runs import increment_ingest_counts, set_ingest_counts


# -----------------------------
# Listed ingestion routes for UI
# -----------------------------

def list_ingest_routes() -> List[Dict[str, str]]:
    """
    Lightweight descriptor of ingest routes.

    For the MVP, servers, storage, databases, applications, and dependencies are exposed via /v1/ingest.
    """
    return [
        {"slice": "servers", "method": "POST", "path": "/v1/ingest/servers"},
        {"slice": "storage", "method": "POST", "path": "/v1/ingest/storage"},
        {"slice": "databases", "method": "POST", "path": "/v1/ingest/databases"},
        {"slice": "applications", "method": "POST", "path": "/v1/ingest/applications"},
        {"slice": "dependencies", "method": "POST", "path": "/v1/ingest/dependencies"},
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
# Databases ingestion (v2-backed)
# -----------------------------------------

async def ingest_databases(
    db: Session,
    run_id: str,
    file: UploadFile,
) -> Dict[str, Any]:
    contents = await file.read()
    text = contents.decode("utf-8", errors="ignore")
    stream = io.StringIO(text)

    result = ingest_databases_from_csv(run_id=run_id or "", file_like=stream)

    inserted = 0
    if result.records:
        inserted = persist_database_records_v2(
            run_id=run_id or "",
            records=result.records,
        )

    increment_ingest_counts(run_id=run_id, databases=inserted)

    return {
        "slice": "databases",
        "run_id": run_id,
        "status": "ok",
        "databases_ingested": inserted,
        "rows_processed": result.rows_processed,
        "rows_successful": result.rows_successful,
        "rows_failed": result.rows_failed,
        "message": f"Databases CSV ingested successfully ({inserted} rows)",
        "errors": result.errors,
    }


# -----------------------------------------
# Applications ingestion (v2-backed)
# -----------------------------------------

async def ingest_applications(
    db: Session,
    run_id: str,
    file: UploadFile,
) -> Dict[str, Any]:
    contents = await file.read()
    text = contents.decode("utf-8", errors="ignore")
    stream = io.StringIO(text)

    result = ingest_applications_from_csv(run_id=run_id or "", file_like=stream)

    inserted = 0
    if result.records:
        inserted = persist_application_records_v2(
            run_id=run_id or "",
            records=result.records,
        )

    increment_ingest_counts(run_id=run_id, applications=inserted)

    return {
        "slice": "applications",
        "run_id": run_id,
        "status": "ok",
        "applications_ingested": inserted,
        "rows_processed": result.rows_processed,
        "rows_successful": result.rows_successful,
        "rows_failed": result.rows_failed,
        "message": f"Applications CSV ingested successfully ({inserted} rows)",
        "errors": result.errors,
    }


# -----------------------------------------
# Dependencies ingestion (hardened MVP)
# -----------------------------------------

async def ingest_dependencies(
    db: Session,
    run_id: str,
    file: UploadFile,
) -> Dict[str, Any]:
    """
    Dependencies ingestion (hardened MVP)

    Expected CSV headers:
      app_id, depends_on_app_id, dependency_type, notes

    Idempotence:
      - We replace existing DB rows for this run_id
      - We SET the run_registry counter to the newly-inserted count (no ballooning)
    """
    contents = await file.read()
    tmp_path = _write_tmp_upload(contents, "ingest_dependencies.csv")

    result = ingest_dependencies_csv(
        db=db,
        run_id=run_id or "",
        csv_path=str(tmp_path),
        replace_existing=True,
        detect_cycles=True,
        max_errors=50,
    )

    rows_successful = int(result.get("rows_successful", 0))
    replaced_existing = bool(result.get("replaced_existing", False))

    # If we replaced existing, do NOT increment; set absolute count.
    if replaced_existing:
        set_ingest_counts(run_id=run_id, dependencies=rows_successful)
    else:
        increment_ingest_counts(run_id=run_id, dependencies=rows_successful)

    return {
        "slice": "dependencies",
        "run_id": run_id,
        "status": "ok",
        "dependencies_ingested": rows_successful,
        "rows_processed": int(result.get("rows_processed", 0)),
        "rows_successful": rows_successful,
        "rows_failed": int(result.get("rows_failed", 0)),
        "duplicates_skipped": int(result.get("duplicates_skipped", 0)),
        "deleted_existing": int(result.get("deleted_existing", 0)),
        "replaced_existing": replaced_existing,
        "cycles_detected": int(result.get("cycles_detected", 0)),
        "errors": result.get("errors", []),
        "message": result.get("message", f"Dependencies CSV ingested successfully ({rows_successful} rows)"),
    }


# -----------------------------------------
# Placeholders for other ingestion slices
# -----------------------------------------

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
