from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
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


async def _run_slice_ingest(
    *,
    slice_name: str,
    fn,
    db: Session,
    run_id: str,
    file: UploadFile,
) -> Dict[str, Any]:
    """
    Tiny wrapper so all slices behave the same. It lets the underlying
    ingestion_engine handle CSV parsing + DB writes.
    """
    if not run_id:
        raise HTTPException(status_code=400, detail="run_id query parameter is required")

    try:
        result = await fn(db=db, run_id=run_id, file=file)
    except HTTPException:
        # Let explicit HTTP errors bubble through
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=500,
            detail=f"{slice_name} ingestion failed: {exc}",
        ) from exc

    # Normalise response shape a bit
    if not isinstance(result, dict):
        result = {"raw_result": str(result)}

    return {
        "ok": True,
        "slice": slice_name,
        "run_id": run_id,
        "details": result,
    }


# ------------------------------
# Servers
# ------------------------------


@router.post("/servers")
async def ingest_servers_endpoint(
    run_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    UI servers CSV upload endpoint.

    Frontend calls:
      POST /v1/ingest/servers?run_id=<run-id>
      Content-Type: multipart/form-data with field "file"
    """
    return await _run_slice_ingest(
        slice_name="servers",
        fn=ingest_servers,
        db=db,
        run_id=run_id,
        file=file,
    )


# ------------------------------
# Storage volumes
# ------------------------------


@router.post("/storage")
async def ingest_storage_endpoint(
    run_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Storage volumes CSV upload.

    Frontend will call:
      POST /v1/ingest/storage?run_id=<run-id>
    """
    return await _run_slice_ingest(
        slice_name="storage",
        fn=ingest_storage,
        db=db,
        run_id=run_id,
        file=file,
    )


# ------------------------------
# Databases
# ------------------------------


@router.post("/databases")
async def ingest_databases_endpoint(
    run_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Databases CSV upload.

    Frontend will call:
      POST /v1/ingest/databases?run_id=<run-id>
    """
    return await _run_slice_ingest(
        slice_name="databases",
        fn=ingest_databases,
        db=db,
        run_id=run_id,
        file=file,
    )


# ------------------------------
# (Optional) other slices wiring
# ------------------------------
# These are here so we can easily plug them in later from the UI
# if we want to expose uploads for business metadata, apps, etc.


@router.post("/applications")
async def ingest_applications_endpoint(
    run_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    return await _run_slice_ingest(
        slice_name="applications",
        fn=ingest_applications,
        db=db,
        run_id=run_id,
        file=file,
    )


@router.post("/business")
async def ingest_business_endpoint(
    run_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    return await _run_slice_ingest(
        slice_name="business",
        fn=ingest_business,
        db=db,
        run_id=run_id,
        file=file,
    )


@router.post("/dependencies")
async def ingest_dependencies_endpoint(
    run_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    return await _run_slice_ingest(
        slice_name="dependencies",
        fn=ingest_dependencies,
        db=db,
        run_id=run_id,
        file=file,
    )


@router.post("/licensing")
async def ingest_licensing_endpoint(
    run_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    return await _run_slice_ingest(
        slice_name="licensing",
        fn=ingest_licensing,
        db=db,
        run_id=run_id,
        file=file,
    )


@router.post("/os-metadata")
async def ingest_os_metadata_endpoint(
    run_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    return await _run_slice_ingest(
        slice_name="os_metadata",
        fn=ingest_os_metadata,
        db=db,
        run_id=run_id,
        file=file,
    )


@router.post("/networks")
async def ingest_networks_endpoint(
    run_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    return await _run_slice_ingest(
        slice_name="networks",
        fn=ingest_networks,
        db=db,
        run_id=run_id,
        file=file,
    )


@router.post("/utilization")
async def ingest_utilization_endpoint(
    run_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    return await _run_slice_ingest(
        slice_name="utilization",
        fn=ingest_utilization,
        db=db,
        run_id=run_id,
        file=file,
    )


# ------------------------------
# Utility: list available ingest routes
# ------------------------------


@router.get("/routes")
async def get_ingest_routes() -> List[Dict[str, str]]:
    """
    Simple debug helper – shows which ingestion routes are wired.
    """
    return list_ingest_routes()
