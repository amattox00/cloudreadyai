from __future__ import annotations

from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.modules.ingestion_core.storage_ingestion_core import (
    StorageRow,
    StorageIngestionSummary,
    ingest_storage_from_csv,
)


def persist_storage_records_v2(
    csv_path: str,
    db: Session,
    run_id: str,
) -> StorageIngestionSummary:
    """
    Read a storage CSV file and persist rows into inventory_storage_v2.

    This mirrors the servers_v2 pattern:
      * Parse + normalize CSV rows via ingest_storage_from_csv(...)
      * For each valid StorageRow, insert into inventory_storage_v2
      * Commit once at the end
    """

    def persist_row(row: StorageRow) -> None:
        # Compute a simple utilization percentage if we have capacity + used.
        utilization_pct: Optional[float] = None
        if row.capacity_gb and row.used_gb is not None and row.capacity_gb > 0:
            utilization_pct = (row.used_gb / row.capacity_gb) * 100.0

        stmt = text(
            """
            INSERT INTO inventory_storage_v2
                (
                    run_id,
                    hostname,
                    volume_id,
                    storage_type,
                    capacity_gb,
                    used_gb,
                    environment,
                    utilization_pct
                )
            VALUES
                (
                    :run_id,
                    :hostname,
                    :volume_id,
                    :storage_type,
                    :capacity_gb,
                    :used_gb,
                    :environment,
                    :utilization_pct
                )
            """
        )

        db.execute(
            stmt,
            {
                "run_id": run_id,
                "hostname": row.hostname,
                "volume_id": row.volume_id,
                "storage_type": row.storage_type,
                "capacity_gb": row.capacity_gb,
                "used_gb": row.used_gb,
                "environment": row.environment,
                "utilization_pct": utilization_pct,
            },
        )

    summary: StorageIngestionSummary = ingest_storage_from_csv(
        csv_path=csv_path,
        persist_row=persist_row,
    )
    db.commit()
    return summary


def ingest_storage_v2_from_csv_to_db(
    csv_path: str,
    db: Session,
    run_id: str,
) -> StorageIngestionSummary:
    """
    Thin alias so other modules can call the more descriptive name.
    """
    return persist_storage_records_v2(csv_path=csv_path, db=db, run_id=run_id)
