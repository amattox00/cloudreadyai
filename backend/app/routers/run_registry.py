from datetime import datetime
import uuid
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.ingestion_run_v2 import IngestionRunV2
from app.schemas.run_schemas import RunSchema, RunListResponse

router = APIRouter(
    prefix="/v1/run_registry",
    tags=["run_registry"],
)


def _run_to_schema(run: IngestionRunV2) -> RunSchema:
    """
    Convert an IngestionRunV2 ORM object into a RunSchema.
    We use getattr() for optional fields so this stays safe even if the
    underlying model doesn't define customer/updated_at yet.
    """
    return RunSchema(
        run_id=getattr(run, "run_id", None),
        name=getattr(run, "name", getattr(run, "run_id", None)),
        status=getattr(run, "status", None),
        customer=getattr(run, "customer", None),
        created_at=getattr(run, "created_at", None),
        updated_at=getattr(run, "updated_at", None),
    )


def list_runs(db: Session) -> RunListResponse:
    """
    Return all runs ordered by created_at DESC.
    """
    runs: List[IngestionRunV2] = (
        db.query(IngestionRunV2)
        .order_by(IngestionRunV2.created_at.desc())
        .all()
    )
    return RunListResponse(runs=[_run_to_schema(r) for r in runs])


@router.get("", response_model=RunListResponse)
def get_run_registry(db: Session = Depends(get_db)) -> RunListResponse:
    """
    GET /v1/run_registry
    Return the registry of assessment runs as:
      { "runs": [ {run_id, name, ...}, ... ] }
    """
    return list_runs(db=db)


@router.post("", response_model=RunSchema, status_code=status.HTTP_201_CREATED)
def create_run_registry_entry(db: Session = Depends(get_db)) -> RunSchema:
    """
    POST /v1/run_registry
    Create a new assessment run and return its metadata.
    """
    # Generate a run_id like: RUN-20251128-193355-abcdef12
    run_id_suffix = uuid.uuid4().hex[:8]
    run_id = f"RUN-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}-{run_id_suffix}"

    now = datetime.utcnow()

    # IMPORTANT: only pass fields that definitely exist on IngestionRunV2.
    new_run = IngestionRunV2(
        run_id=run_id,
        name=f"Assessment {run_id}",
        status="NEW",
        created_at=now,
    )

    db.add(new_run)
    db.commit()
    db.refresh(new_run)

    return _run_to_schema(new_run)
