from __future__ import annotations

import io

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.modules.ingestion_core.dependencies_ingestion_v2 import (
    ingest_dependencies_from_csv,
)
from app.modules.ingestion_core.dependencies_ingestion_db_v2 import (
    persist_dependency_records_v2,
)

router = APIRouter(
    prefix="/v2/ingestion/dependencies",
    tags=["ingestion-v2-dependencies"],
)


@router.post("/csv")
async def ingest_dependencies_csv(
    run_id: str,
    file: UploadFile = File(...),
):
    """
    v2 CSV ingestion endpoint for application dependencies.

    - Accepts a CSV matching templates/dependencies_template_v2.csv
    - Validates each row with DependencyRow
    - Writes valid rows to inventory_dependencies_v2
    - Returns a summary with success/failure counts
    """

    if file.filename is None:
        raise HTTPException(status_code=400, detail="No file uploaded")

    # Read file into a text stream
    raw_bytes = await file.read()
    try:
        text_stream = io.StringIO(raw_bytes.decode("utf-8-sig"))
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Could not decode uploaded file as UTF-8",
        )

    # Step 1: CSV → validated records
    result = ingest_dependencies_from_csv(run_id=run_id, file_like=text_stream)

    # Step 2: Valid records → DB
    rows_inserted = 0
    if result.records:
        rows_inserted = persist_dependency_records_v2(
            run_id=run_id,
            records=result.records,
        )

    return {
        "run_id": run_id,
        "rows_processed": result.rows_processed,
        "rows_successful": result.rows_successful,
        "rows_failed": result.rows_failed,
        "rows_inserted": rows_inserted,
        "errors": result.errors,
    }
