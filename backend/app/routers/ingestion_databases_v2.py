from __future__ import annotations

import io

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.modules.ingestion_core.databases_ingestion_v2 import (
    ingest_databases_from_csv,
)
from app.modules.ingestion_core.databases_ingestion_db_v2 import (
    persist_database_records_v2,
)

router = APIRouter(
    prefix="/v2/ingestion/databases",
    tags=["ingestion-v2-databases"],
)


@router.post(
    "/csv",
    summary="Ingest databases CSV (v2)",
)
async def ingest_databases_csv_v2(
    run_id: str,
    file: UploadFile = File(...),
):
    """
    Ingest a databases CSV for a given run_id into the v2 databases table.

    - Validates each row with Pydantic (DatabaseRow)
    - Skips invalid rows but reports their errors
    - Persists valid rows into inventory_databases_v2
    """
    # Don't over-enforce content-type (Excel, browsers send odd types)
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

    # Read file into text stream
    raw_bytes = await file.read()
    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not decode file as UTF-8 text.",
        )

    stream = io.StringIO(text)

    # Step 1: CSV → validated DatabaseRow records
    result = ingest_databases_from_csv(run_id=run_id, file_like=stream)

    # Step 2: Valid records → DB
    inserted = 0
    if result.records:
        inserted = persist_database_records_v2(run_id=run_id, records=result.records)

    # Step 3: Return a clean summary
    return {
        "run_id": result.run_id,
        "rows_processed": result.rows_processed,
        "rows_successful": result.rows_successful,
        "rows_failed": result.rows_failed,
        "rows_inserted": inserted,
        "errors": result.errors,
    }
