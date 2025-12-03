from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.modules.analysis.engine import generate_intelligence_summary
from app.schemas.intelligence import IntelligenceSummary


router = APIRouter(prefix="/v1/intelligence", tags=["intelligence"])


@router.get("/summary", response_model=IntelligenceSummary)
def get_intelligence_summary(run_id: str, db: Session = Depends(get_db)):
    try:
        return generate_intelligence_summary(db, run_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Unable to generate intelligence summary")
