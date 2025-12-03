from __future__ import annotations

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.modules import ingestion_engine as ie

router = APIRouter(prefix="/v1/ingest", tags=["ingestion"])


@router.get("/routes")
def get_ingest_routes() -> dict:
    """Return the list of available ingestion endpoints."""
    return {"routes": ie.list_ingest_routes()}


def _handle_ingestion(
    func,
    db: Session,
    run_id: str,
    upload: UploadFile,
    entity_name: str,
):
    try:
        return func(db=db, run_id=run_id, upload=upload)
    except ie.IngestionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Keep this generic for now; you can log details to sentry/logger later.
        raise HTTPException(
            status_code=500,
            detail=f"Error ingesting {entity_name} CSV: {e}",
        )


# ---------------------------------------------------------------------------
# Slice endpoints
# ---------------------------------------------------------------------------


@router.post("/servers")
async def ingest_servers(
    run_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    return _handle_ingestion(ie.ingest_servers, db, run_id, file, "servers")


@router.post("/storage")
async def ingest_storage(
    run_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    return _handle_ingestion(ie.ingest_storage, db, run_id, file, "storage")


@router.post("/network")
async def ingest_network(
    run_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    return _handle_ingestion(ie.ingest_networks, db, run_id, file, "network")


@router.post("/databases")
async def ingest_databases(
    run_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    return _handle_ingestion(ie.ingest_databases, db, run_id, file, "databases")


@router.post("/applications")
async def ingest_applications(
    run_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    return _handle_ingestion(ie.ingest_applications, db, run_id, file, "applications")


@router.post("/dependencies")
async def ingest_dependencies(
    run_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    return _handle_ingestion(ie.ingest_dependencies, db, run_id, file, "dependencies")


@router.post("/utilization")
async def ingest_utilization(
    run_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    return _handle_ingestion(ie.ingest_utilization, db, run_id, file, "utilization")


@router.post("/business")
async def ingest_business(
    run_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    return _handle_ingestion(
        ie.ingest_business_metadata, db, run_id, file, "business_metadata"
    )


@router.post("/licensing")
async def ingest_licensing(
    run_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    return _handle_ingestion(
        ie.ingest_licensing_metadata, db, run_id, file, "licensing_metadata"
    )


@router.post("/os-metadata")
async def ingest_os_metadata(
    run_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    return _handle_ingestion(
        ie.ingest_os_metadata, db, run_id, file, "os_metadata"
    )

