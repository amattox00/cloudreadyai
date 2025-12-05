from typing import Tuple, List, Any

from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models.inventory_utilization_v2 import InventoryUtilizationV2
from app.modules.ingestion_core.utilization_ingestion_v2 import (
    ingest_utilization_from_csv,
)


def write_utilization_rows_to_db(
    db: Session,
    run_id: str,
    rows: List[Any],
) -> int:
    """
    Persist parsed utilization rows into inventory_utilization_v2.

    We don't depend on the exact Pydantic model type here; we just
    access the expected attributes on each row.
    """
    records = []

    for row in rows:
        record = InventoryUtilizationV2(
            run_id=run_id,
            hostname=row.hostname,
            environment=row.environment,
            avg_cpu_percent=row.avg_cpu_percent,
            peak_cpu_percent=row.peak_cpu_percent,
            avg_ram_percent=row.avg_ram_percent,
            peak_ram_percent=row.peak_ram_percent,
            notes=None,
        )
        records.append(record)

    if records:
        db.add_all(records)
        db.commit()

    return len(records)


def ingest_utilization_from_csv_db(
    run_id: str,
    file_like,
) -> Tuple[Any, int]:
    """
    High-level helper:

    1) Parse + validate the CSV (using ingest_utilization_from_csv)
    2) Write the good rows into inventory_utilization_v2

    Returns: (result, rows_inserted)
    """
    result, rows = ingest_utilization_from_csv(run_id=run_id, file_like=file_like)

    if result.rows_successful == 0:
        return result, 0

    db = SessionLocal()
    try:
        inserted = write_utilization_rows_to_db(db=db, run_id=run_id, rows=rows)
    finally:
        db.close()

    return result, inserted
