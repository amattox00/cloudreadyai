from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
import io

from app.db import get_db
from app.modules.ingestion_core.utilization_ingestion_db_v2 import (
    ingest_utilization_from_csv_db,
)

router = APIRouter()


@router.post("/v2/ingestion/utilization/csv")
async def ingest_utilization_csv_v2(
    run_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Ingest utilization CSV (v2) and persist into inventory_utilization_v2.

    Mirrors the other v2 ingestion endpoints, but we must ensure the
    uploaded file is exposed to the CSV reader as *text*, not bytes.
    """
    if file.content_type not in ("text/csv", "application/vnd.ms-excel"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    try:
        # Read the uploaded file as bytes
        raw_bytes = await file.read()
        # Decode to text and wrap in a text file-like object
        text_stream = io.StringIO(raw_bytes.decode("utf-8"))

        # Our DB helper expects a text-mode file_like
        result, rows_inserted = ingest_utilization_from_csv_db(
            run_id=run_id,
            file_like=text_stream,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Utilization ingestion failed: {exc}")

    return {
        "run_id": result.run_id,
        "rows_processed": result.rows_processed,
        "rows_successful": result.rows_successful,
        "rows_failed": result.rows_failed,
        "rows_inserted": rows_inserted,
        "errors": result.errors,
    }
