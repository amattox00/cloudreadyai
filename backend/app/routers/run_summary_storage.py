from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.modules.summary.storage import summarize_storage

router = APIRouter(prefix="/v1/runs")

@router.get("/{run_id}/summary/storage")
def summary_storage_route(run_id: str, db: Session = Depends(get_db)):
    return summarize_storage(db, run_id)
