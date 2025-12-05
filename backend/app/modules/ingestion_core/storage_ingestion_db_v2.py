from typing import List

from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models.inventory_storage_v2 import InventoryStorageV2
from app.modules.ingestion_core.storage_ingestion_v2 import StorageRow


def persist_storage_records_v2(run_id: str, records: List[StorageRow]) -> int:
    """
    Persist validated StorageRow records into inventory_storage_v2.

    Returns the number of records inserted.
    """
    db: Session = SessionLocal()
    inserted = 0

    try:
        for rec in records:
            obj = InventoryStorageV2(
                run_id=run_id,
                volume_id=rec.volume_id,
                datastore=rec.datastore,
                storage_array=rec.storage_array,
                hostname=rec.hostname,
                environment=rec.environment,
                protocol=rec.protocol,
                tier=rec.tier,
                raid_type=rec.raid_type,
                capacity_gb=rec.capacity_gb,
                used_gb=rec.used_gb,
                provisioned_gb=rec.provisioned_gb,
                iops=rec.iops,
                latency_ms=rec.latency_ms,
                storage_type=rec.storage_type,
                is_replicated=rec.is_replicated,
                notes=rec.notes,
            )
            db.add(obj)
            inserted += 1

        db.commit()
        return inserted

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()
