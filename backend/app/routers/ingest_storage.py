from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
import tempfile
import shutil

from app.db import get_db
from app.modules.ingest.storage import ingest_storage_csv

router = APIRouter(tags=["ingest-storage"])


@router.post("/ingest/storage/{run_id}")
def ingest_storage(
    run_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # Save uploaded file to a temporary path on disk
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    result = ingest_storage_csv(db, run_id, tmp_path)
    return result
