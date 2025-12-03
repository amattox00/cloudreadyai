from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.modules.validation.storage import storage_problems

router = APIRouter(prefix="/v1/runs")

@router.get("/{run_id}/problems/storage")
def storage_problems_route(run_id: str, db: Session = Depends(get_db)):
    return storage_problems(db, run_id)
