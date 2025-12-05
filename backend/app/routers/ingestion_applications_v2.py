from __future__ import annotations

import io

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.modules.ingestion_core.applications_ingestion_v2 import (
    ingest_applications_from_csv,
)
from app.modules.ingestion_core.applications_ingestion_db_v2 import (
    persist_application_records_v2,
)

router = APIRouter(
    prefix="/v2/ingestion/applications",
    tags=["ingestion-v2-applications"],
)


@router.post(
    "/csv",
    summary="Ingest applications CSV (v2)",
)
async def ingest_applications_csv_v2(
    run_id: str,
    file: UploadFile = File(...),
):
    """
    Ingest an applications CSV for a given run_id into the v2 applications table.

    - Validates each row with Pydantic (ApplicationRow)
    - Skips invalid rows but reports their errors
    - Persists valid rows into inventory_applications_v2
    """
    if file.content_type not in (
        "text/csv",
        "application/vnd.ms-excel",
        "application/octet-stream",
        "text/plain",
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file content type: {file.content_type}. Expected CSV.",
        )

    raw_bytes = await file.read()
    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not decode file as UTF-8 text.",
        )

    stream = io.StringIO(text)

    # Step 1: CSV → validated ApplicationRow records
    result = ingest_applications_from_csv(run_id=run_id, file_like=stream)

    # Step 2: Valid records → DB
    inserted = 0
    if result.records:
        inserted = persist_application_records_v2(run_id=run_id, records=result.records)

    return {
        "run_id": result.run_id,
        "rows_processed": result.rows_processed,
        "rows_successful": result.rows_successful,
        "rows_failed": result.rows_failed,
        "rows_inserted": inserted,
        "errors": result.errors,
    }
