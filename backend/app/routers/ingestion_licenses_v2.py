from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
import io

from app.db import get_db
from app.modules.ingestion_core.licenses_ingestion_db_v2 import (
    ingest_licenses_from_csv_db,
)

router = APIRouter()


@router.post("/v2/ingestion/licenses/csv")
async def ingest_licenses_csv_v2(
    run_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Ingest licensing CSV (v2) and persist into inventory_licenses_v2.
    """
    if file.content_type not in ("text/csv", "application/vnd.ms-excel"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    try:
        raw_bytes = await file.read()
        text_stream = io.StringIO(raw_bytes.decode("utf-8"))

        result, rows_inserted = ingest_licenses_from_csv_db(
            run_id=run_id,
            file_like=text_stream,
            db=db,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Licenses ingestion failed: {exc}")

    return {
        "run_id": result.run_id,
        "rows_processed": result.rows_processed,
        "rows_successful": result.rows_successful,
        "rows_failed": result.rows_failed,
        "rows_inserted": rows_inserted,
        "errors": result.errors,
    }
