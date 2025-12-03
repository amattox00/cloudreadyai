from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.modules.normalization.storage import normalize_storage

router = APIRouter(prefix="/v1/runs")

@router.post("/{run_id}/normalize/storage")
def normalize_storage_route(run_id: str, db: Session = Depends(get_db)):
    return normalize_storage(db, run_id)
