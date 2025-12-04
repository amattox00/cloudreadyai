# app/routers/ingestion_servers_v2.py

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.modules.ingestion_core.server_ingestion_db_v2 import (
    ingest_servers_v2_from_csv_to_db,
    ServersIngestionSummary,
)

import os
import shutil
import tempfile

router = APIRouter(
    prefix="/v2/ingestion/servers",
    tags=["ingestion_v2_servers"],
)


@router.post("/csv")
def upload_servers_csv_v2(
    run_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload a servers CSV and ingest it into the v2 tables.

    - Writes the uploaded file to a temporary path
    - Calls ingest_servers_v2_from_csv_to_db(csv_path=..., db=..., run_id=...)
    - Returns the same summary shape as the CLI test:
      { rows_processed, rows_successful, rows_failed, errors }
    """
    tmp_path: str | None = None

    try:
        # Create a real temp file on disk and copy the upload there
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name  # <--- this is a real filesystem path (string)

        # Call the DB helper with the *path*, not a file handle
        summary: ServersIngestionSummary = ingest_servers_v2_from_csv_to_db(
            csv_path=tmp_path,
            db=db,
            run_id=run_id,
        )

        # Return a JSON-friendly summary
        return {
            "run_id": run_id,
            "rows_processed": summary.rows_processed,
            "rows_successful": summary.rows_successful,
            "rows_failed": summary.rows_failed,
            "errors": summary.errors,
        }

    except Exception as e:
        # Surface a clear message in the HTTP response
        raise HTTPException(
            status_code=500,
            detail=f"Ingestion failed: {e}",
        )
    finally:
        # Always clean up the temp file if it was created
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
