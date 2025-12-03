from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.modules.ingestion_engine import (
    ingest_applications,
    ingest_business,
    ingest_databases,
    ingest_dependencies,
    ingest_licensing,
    ingest_networks,
    ingest_os_metadata,
    ingest_servers,
    ingest_storage,
    ingest_utilization,
    list_ingest_routes,
)

router = APIRouter(prefix="/v1/ingest", tags=["Ingestion"])

UPLOAD_ROOT = Path("/tmp/cloudready_uploads")


def save_upload(file: UploadFile, run_id: str, entity: str) -> Path:
    """
    Save an uploaded CSV file to /tmp/cloudready_uploads with a consistent naming pattern.
    """
    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    safe_run_id = "".join(ch for ch in run_id if ch.isalnum() or ch in ("-", "_"))
    filename = f"{entity}_{safe_run_id}_{file.filename or 'upload.csv'}"
    path = UPLOAD_ROOT / filename

    with path.open("wb") as buffer:
        buffer.write(file.file.read())

    return path


@router.get("/routes")
def get_ingest_routes() -> Dict[str, List[Dict[str, str]]]:
    """
    Introspection endpoint so the UI (and you via curl) can see what ingestion endpoints exist.
    """
    return {"routes": list_ingest_routes()}


# ---------------------------------------------------------------------------
# Servers
# ---------------------------------------------------------------------------


@router.post("/servers")
async def ingest_servers_endpoint(
    run_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    try:
        csv_path = save_upload(file, run_id, "servers")
        return ingest_servers(db, run_id, csv_path)
    except ValueError as exc:
        # Run not found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ingesting servers CSV: {exc}",
        ) from exc


# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------


@router.post("/storage")
async def ingest_storage_endpoint(
    run_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    try:
        csv_path = save_upload(file, run_id, "storage")
        return ingest_storage(db, run_id, csv_path)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ingesting storage CSV: {exc}",
        ) from exc


# ---------------------------------------------------------------------------
# Networks
# ---------------------------------------------------------------------------


@router.post("/networks")
async def ingest_networks_endpoint(
    run_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    try:
        csv_path = save_upload(file, run_id, "networks")
        return ingest_networks(db, run_id, csv_path)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ingesting networks CSV: {exc}",
        ) from exc


# ---------------------------------------------------------------------------
# Databases
# ---------------------------------------------------------------------------


@router.post("/databases")
async def ingest_databases_endpoint(
    run_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    try:
        csv_path = save_upload(file, run_id, "databases")
        return ingest_databases(db, run_id, csv_path)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ingesting databases CSV: {exc}",
        ) from exc


# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------


@router.post("/applications")
async def ingest_applications_endpoint(
    run_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    try:
        csv_path = save_upload(file, run_id, "applications")
        return ingest_applications(db, run_id, csv_path)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ingesting applications CSV: {exc}",
        ) from exc


# ---------------------------------------------------------------------------
# Dependencies
# ---------------------------------------------------------------------------


@router.post("/dependencies")
async def ingest_dependencies_endpoint(
    run_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    try:
        csv_path = save_upload(file, run_id, "dependencies")
        return ingest_dependencies(db, run_id, csv_path)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ingesting dependencies CSV: {exc}",
        ) from exc


# ---------------------------------------------------------------------------
# OS / Software Metadata
# ---------------------------------------------------------------------------


@router.post("/os-metadata")
async def ingest_os_metadata_endpoint(
    run_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    OS / software ingestion endpoint.

    NOTE: The engine currently accepts the CSV and records metadata about the
    upload, but does not yet persist rows into a specific OsMetadata table,
    because the concrete model class is not yet wired up.
    """
    try:
        csv_path = save_upload(file, run_id, "os_metadata")
        return ingest_os_metadata(db, run_id, csv_path)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ingesting OS metadata CSV: {exc}",
        ) from exc


# ---------------------------------------------------------------------------
# Utilization
# ---------------------------------------------------------------------------


@router.post("/utilization")
async def ingest_utilization_endpoint(
    run_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    try:
        csv_path = save_upload(file, run_id, "utilization")
        return ingest_utilization(db, run_id, csv_path)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ingesting utilization CSV: {exc}",
        ) from exc


# ---------------------------------------------------------------------------
# Business Metadata
# ---------------------------------------------------------------------------


@router.post("/business")
async def ingest_business_endpoint(
    run_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    try:
        csv_path = save_upload(file, run_id, "business")
        return ingest_business(db, run_id, csv_path)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ingesting business metadata CSV: {exc}",
        ) from exc


# ---------------------------------------------------------------------------
# Licensing Metadata
# ---------------------------------------------------------------------------


@router.post("/licensing")
async def ingest_licensing_endpoint(
    run_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    try:
        csv_path = save_upload(file, run_id, "licensing")
        return ingest_licensing(db, run_id, csv_path)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ingesting licensing metadata CSV: {exc}",
        ) from exc
