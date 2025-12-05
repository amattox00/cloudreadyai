from __future__ import annotations

from typing import TextIO, Tuple, List
from sqlalchemy.orm import Session

from app.models.inventory_license_v2 import InventoryLicenseV2
from app.modules.ingestion_core.licenses_ingestion_v2 import (
    ingest_licenses_from_csv,
    LicenseIngestionResult,
    LicenseRow,
)


def ingest_licenses_from_csv_db(
    run_id: str,
    file_like: TextIO,
    db: Session,
) -> Tuple[LicenseIngestionResult, int]:
    """
    Wraps the core CSV validator and writes good rows into inventory_licenses_v2.
    """
    result, rows = ingest_licenses_from_csv(run_id=run_id, file_like=file_like)

    inserted = 0
    for row in rows:
        record = InventoryLicenseV2(
            run_id=run_id,
            hostname=row.hostname,
            product_name=row.product_name,
            vendor=row.vendor,
            license_type=row.license_type,
            metric=row.metric,
            environment=row.environment,
            cores_licensed=row.cores_licensed,
            users_licensed=row.users_licensed,
            expiry_date=row.expiry_date,
            cost_per_year=row.cost_per_year,
            maintenance_per_year=row.maintenance_per_year,
            po_number=row.po_number,
            owner=row.owner,
            notes=row.notes,
            tags=row.tags,
        )
        db.add(record)
        inserted += 1

    db.commit()
    return result, inserted
