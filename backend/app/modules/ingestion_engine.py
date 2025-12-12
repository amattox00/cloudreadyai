from __future__ import annotations

import io
import csv
from pathlib import Path
from typing import Any, Dict, List

from fastapi import UploadFile
from sqlalchemy import text
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

# Template guardrails (validate headers + normalize aliases)
from app.modules.ingestion_templates.template_validator import (
    validate_headers,
    normalize_csv_headers,
)

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
# Shared helpers
# -----------------------------

def _write_tmp_upload(file_bytes: bytes, tmp_name: str) -> Path:
    """
    Persist uploaded file bytes to /tmp and return the path.
    """
    tmp_path = Path(f"/tmp/{tmp_name}")
    tmp_path.write_bytes(file_bytes)
    return tmp_path


def _read_csv_headers(csv_path: str) -> List[str]:
    """
    Lightweight CSV header read (first row only).
    """
    p = Path(csv_path)
    if not p.exists():
        return []
    first = p.read_text(encoding="utf-8", errors="ignore").splitlines()
    if not first:
        return []
    # naive split is fine for header row; we only need raw names
    return [h.strip() for h in first[0].split(",") if h.strip()]


def _apply_guardrails(*, slice_name: str, csv_path: str) -> Dict[str, Any]:
    """
    Validate headers against template.
    If aliases are detected, normalize to canonical headers by rewriting a temp CSV.

    Returns:
      {
        "status": "ok"|"blocked",
        "guardrails": <TemplateValidationResult as dict>,
        "csv_path": <maybe normalized path>,
      }
    """
    headers = _read_csv_headers(csv_path)
    result = validate_headers(slice_name=slice_name, headers=headers)

    guardrails_payload = {
        "slice": result.slice,
        "valid": result.valid,
        "missing_required": result.missing_required,
        "missing_optional": result.missing_optional,
        "unknown_columns": result.unknown_columns,
        "used_aliases": result.used_aliases,
        "header_renames": result.header_renames,
        "warnings": result.warnings,
        "blockers": result.blockers,
    }

    if not result.valid:
        return {
            "status": "blocked",
            "guardrails": guardrails_payload,
            "csv_path": csv_path,
        }

    normalized_path = normalize_csv_headers(
        csv_path=csv_path,
        header_renames=result.header_renames,
        output_path=f"{csv_path}.normalized",
    )

    return {
        "status": "ok",
        "guardrails": guardrails_payload,
        "csv_path": normalized_path,
    }

def _storage_linkage_guardrail_warn(
    *,
    db: Session,
    run_id: str,
    csv_path: str,
    sample_limit: int = 25,
) -> Dict[str, Any]:
    """
    WARN-only guardrail: identify storage rows whose hostname does not exist
    in inventory_servers_v2 for the same run_id.

    This does NOT block ingestion because many users ingest storage before servers.
    """
    # Collect hostnames from the uploaded (normalized) CSV
    storage_hosts: set[str] = set()
    try:
        with open(csv_path, "r", encoding="utf-8", errors="ignore", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                h = (row.get("hostname") or "").strip()
                if h:
                    storage_hosts.add(h.lower())
    except Exception:
        # If we can't parse for some reason, don't block anything
        return {
            "ok": True,
            "orphan_hostnames_count": 0,
            "orphan_hostnames_sample": [],
            "note": "Linkage guardrail skipped (unable to parse storage CSV)."
        }

    if not storage_hosts:
        return {
            "ok": True,
            "orphan_hostnames_count": 0,
            "orphan_hostnames_sample": [],
            "note": "No hostnames found in storage CSV."
        }

    # Pull server hostnames for this run_id
    rows = db.execute(
        text(
            """
            SELECT hostname
            FROM inventory_servers_v2
            WHERE run_id = :run_id
              AND hostname IS NOT NULL
              AND hostname <> ''
            """
        ),
        {"run_id": run_id},
    ).fetchall()

    server_hosts = {str(r[0]).strip().lower() for r in rows if r and r[0]}
    if not server_hosts:
        return {
            "ok": True,
            "orphan_hostnames_count": len(storage_hosts),
            "orphan_hostnames_sample": sorted(list(storage_hosts))[:sample_limit],
            "note": "No servers found for this run_id yet (storage may have been ingested first)."
        }

    orphan = sorted(list(storage_hosts - server_hosts))
    return {
        "ok": True,
        "orphan_hostnames_count": len(orphan),
        "orphan_hostnames_sample": orphan[:sample_limit],
        "note": "These storage hostnames were not found in inventory_servers_v2 for this run_id."
    }

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

    g = _apply_guardrails(slice_name="servers", csv_path=str(tmp_path))
    if g["status"] == "blocked":
        return {
            "slice": "servers",
            "run_id": run_id,
            "status": "blocked",
            "servers_ingested": 0,
            "guardrails": g["guardrails"],
            "message": "Servers CSV blocked by template guardrails. Fix the CSV headers and re-upload.",
        }

    summary: ServersIngestionSummary = ingest_servers_v2_from_csv_to_db(
        csv_path=str(g["csv_path"]),
        db=db,
        run_id=run_id or "",
    )

    rows_processed = int(getattr(summary, "rows_processed", 0) or 0)
    rows_successful = int(getattr(summary, "rows_successful", 0) or 0)
    rows_failed = int(getattr(summary, "rows_failed", 0) or 0)

    servers_ingested = max(rows_successful, 0)
    increment_ingest_counts(run_id=run_id, servers=servers_ingested)

    return {
        "slice": "servers",
        "run_id": run_id,
        "status": "ok",
        "servers_ingested": servers_ingested,
        "rows_processed": rows_processed,
        "rows_successful": rows_successful,
        "rows_failed": rows_failed,
        "guardrails": g["guardrails"],
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

    g = _apply_guardrails(slice_name="storage", csv_path=str(tmp_path))
    if g["status"] == "blocked":
        return {
            "slice": "storage",
            "run_id": run_id,
            "status": "blocked",
            "storage_ingested": 0,
            "rows_processed": 0,
            "rows_successful": 0,
            "rows_failed": 0,
            "guardrails": g["guardrails"],
            "message": "Storage CSV blocked by template guardrails. Fix the CSV headers and re-upload.",
        }

    summary = ingest_storage_v2_from_csv_to_db(
        csv_path=str(g["csv_path"]),
        db=db,
        run_id=run_id or "",
    )

    rows_processed = int(getattr(summary, "rows_processed", 0) or 0)
    rows_successful = int(getattr(summary, "rows_successful", 0) or 0)
    rows_failed = int(getattr(summary, "rows_failed", 0) or 0)

    storage_ingested = max(rows_successful, 0)
    increment_ingest_counts(run_id=run_id, storage=storage_ingested)

    linkage = _storage_linkage_guardrail_warn(
        db=db,
        run_id=run_id or "",
        csv_path=str(g["csv_path"]),
    )

    if int(linkage.get("orphan_hostnames_count", 0) or 0) > 0:
        g["guardrails"].setdefault("warnings", []).append(
            f"Storage references {linkage['orphan_hostnames_count']} hostname(s) not present in servers for this run_id (or servers not ingested yet)."
        )

    return {
        "slice": "storage",
        "run_id": run_id,
        "status": "ok",
        "storage_ingested": storage_ingested,
        "rows_processed": rows_processed,
        "rows_successful": rows_successful,
        "rows_failed": rows_failed,
        "guardrails": g["guardrails"],
        "linkage": linkage,
        "message": f"Storage CSV ingested successfully ({storage_ingested} rows)",
    }

# -----------------------------------------
# Databases ingestion (v2-backed) + guardrails
# -----------------------------------------

async def ingest_databases(
    db: Session,
    run_id: str,
    file: UploadFile,
) -> Dict[str, Any]:
    contents = await file.read()
    tmp_path = _write_tmp_upload(contents, "ingest_databases.csv")

    g = _apply_guardrails(slice_name="databases", csv_path=str(tmp_path))
    if g["status"] == "blocked":
        return {
            "slice": "databases",
            "run_id": run_id,
            "status": "blocked",
            "databases_ingested": 0,
            "rows_processed": 0,
            "rows_successful": 0,
            "rows_failed": 0,
            "errors": [],
            "guardrails": g["guardrails"],
            "message": "Databases CSV blocked by template guardrails. Fix the CSV headers and re-upload.",
        }

    text = Path(str(g["csv_path"])).read_text(encoding="utf-8", errors="ignore")
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
        "rows_processed": int(getattr(result, "rows_processed", 0) or 0),
        "rows_successful": int(getattr(result, "rows_successful", 0) or 0),
        "rows_failed": int(getattr(result, "rows_failed", 0) or 0),
        "errors": getattr(result, "errors", []),
        "guardrails": g["guardrails"],
        "message": f"Databases CSV ingested successfully ({inserted} rows)",
    }


# -----------------------------------------
# Applications ingestion (v2-backed) + guardrails
# -----------------------------------------

async def ingest_applications(
    db: Session,
    run_id: str,
    file: UploadFile,
) -> Dict[str, Any]:
    contents = await file.read()
    tmp_path = _write_tmp_upload(contents, "ingest_applications.csv")

    g = _apply_guardrails(slice_name="applications", csv_path=str(tmp_path))
    if g["status"] == "blocked":
        return {
            "slice": "applications",
            "run_id": run_id,
            "status": "blocked",
            "applications_ingested": 0,
            "rows_processed": 0,
            "rows_successful": 0,
            "rows_failed": 0,
            "errors": [],
            "guardrails": g["guardrails"],
            "message": "Applications CSV blocked by template guardrails. Fix the CSV headers and re-upload.",
        }

    text = Path(str(g["csv_path"])).read_text(encoding="utf-8", errors="ignore")
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
        "rows_processed": int(getattr(result, "rows_processed", 0) or 0),
        "rows_successful": int(getattr(result, "rows_successful", 0) or 0),
        "rows_failed": int(getattr(result, "rows_failed", 0) or 0),
        "errors": getattr(result, "errors", []),
        "guardrails": g["guardrails"],
        "message": f"Applications CSV ingested successfully ({inserted} rows)",
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

    g = _apply_guardrails(slice_name="dependencies", csv_path=str(tmp_path))
    if g["status"] == "blocked":
        return {
            "slice": "dependencies",
            "run_id": run_id,
            "status": "blocked",
            "dependencies_ingested": 0,
            "rows_processed": 0,
            "rows_successful": 0,
            "rows_failed": 0,
            "duplicates_skipped": 0,
            "deleted_existing": 0,
            "replaced_existing": False,
            "cycles_detected": 0,
            "errors": [],
            "guardrails": g["guardrails"],
            "message": "Dependencies CSV blocked by template guardrails. Fix the CSV headers and re-upload.",
        }

    result = ingest_dependencies_csv(
        db=db,
        run_id=run_id or "",
        csv_path=str(g["csv_path"]),
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

    # attach guardrails payload
    result["guardrails"] = g["guardrails"]

    return {
        "slice": "dependencies",
        "run_id": run_id,
        "status": result.get("status", "ok"),
        "dependencies_ingested": rows_successful,
        "rows_processed": int(result.get("rows_processed", 0)),
        "rows_successful": rows_successful,
        "rows_failed": int(result.get("rows_failed", 0)),
        "duplicates_skipped": int(result.get("duplicates_skipped", 0)),
        "deleted_existing": int(result.get("deleted_existing", 0)),
        "replaced_existing": replaced_existing,
        "cycles_detected": int(result.get("cycles_detected", 0)),
        "errors": result.get("errors", []),
        "guardrails": g["guardrails"],
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
