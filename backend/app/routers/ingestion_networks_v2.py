from __future__ import annotations

import io

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.modules.ingestion_core.networks_ingestion_v2 import (
    ingest_networks_from_csv,
)
from app.modules.ingestion_core.networks_ingestion_db_v2 import (
    persist_network_records_v2,
)

router = APIRouter(
    prefix="/v2/ingestion/networks",
    tags=["ingestion-v2-networks"],
)


@router.post("/csv")
async def ingest_networks_csv(
    run_id: str,
    file: UploadFile = File(...),
):
    """
    v2 CSV ingestion endpoint for network/subnet inventory.

    - Accepts a CSV matching templates/networks_template_v2.csv
    - Validates each row with NetworkRow
    - Writes valid rows to inventory_networks_v2
    - Returns a summary with success/failure counts
    """
    if file.filename is None:
        raise HTTPException(status_code=400, detail="No file uploaded")

    raw_bytes = await file.read()
    try:
        text_stream = io.StringIO(raw_bytes.decode("utf-8-sig"))
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Could not decode uploaded file as UTF-8",
        )

    # Step 1: CSV → validated records
    result = ingest_networks_from_csv(run_id=run_id, file_like=text_stream)

    # Step 2: Valid records → DB
    rows_inserted = 0
    if result.records:
        rows_inserted = persist_network_records_v2(
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
