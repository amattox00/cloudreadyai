# app/modules/ingestion_core/server_ingestion_db_v2.py

from typing import Callable

from sqlalchemy.orm import Session

from app.models.ingestion_run_v2 import IngestionRunV2
from app.models.inventory_server_v2 import InventoryServerV2
from app.modules.ingestion_core.server_ingestion_core import (
    ingest_servers_from_csv,
    ServersIngestionSummary,
    ServerRow,
)


def ensure_run_v2(db: Session, run_id: str) -> IngestionRunV2:
    """
    Make sure there is an ingestion_runs_v2 row for this run_id.
    If it doesn't exist, create one with a basic status.
    """
    run = (
        db.query(IngestionRunV2)
        .filter(IngestionRunV2.run_id == run_id)
        .one_or_none()
    )
    if run is None:
        run = IngestionRunV2(
            run_id=run_id,
            status="created",
        )
        db.add(run)
        db.commit()
        db.refresh(run)
    return run


def persist_server_row_v2(row: ServerRow, db: Session, run_id: str) -> None:
    """
    Map a validated ServerRow into inventory_servers_v2.
    Right now we only populate the basic fields; we can extend later.
    """
    server = InventoryServerV2(
        run_id=run_id,
        hostname=row.hostname,
        role=None,
        os=row.os,
        environment=row.environment,
        cpu_usage=None,
        ram_usage=None,
        storage_usage=None,
    )
    db.add(server)


def ingest_servers_v2_from_csv_to_db(
    csv_path: str,
    db: Session,
    run_id: str,
) -> ServersIngestionSummary:
    """
    High-level helper used by both:
      - CLI tool (test_server_ingestion_db_v2.py)
      - FastAPI route /v2/ingestion/servers/csv

    It:
      1) Ensures an ingestion_runs_v2 row exists for run_id
      2) Uses ingest_servers_from_csv(csv_path=..., persist_row=...)
      3) Commits once after all rows are processed
      4) Returns ServersIngestionSummary
    """
    # 1) Make sure the run exists in ingestion_runs_v2
    ensure_run_v2(db, run_id)

    # 2) Wrap the per-row DB insert
    def _persist(row: ServerRow) -> None:
        persist_server_row_v2(row=row, db=db, run_id=run_id)

    # 3) Call the core ingestion using the *path* to the CSV
    summary: ServersIngestionSummary = ingest_servers_from_csv(
        csv_path=csv_path,   # <-- IMPORTANT: csv_path, NOT csv_source
        persist_row=_persist,
    )

    # 4) Single commit after ingestion
    db.commit()

    return summary
