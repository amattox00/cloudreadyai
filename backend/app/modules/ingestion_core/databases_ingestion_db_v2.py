from __future__ import annotations

from typing import List

from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models.inventory_database_v2 import InventoryDatabaseV2
from app.modules.ingestion_core.databases_ingestion_v2 import DatabaseRow


def persist_database_records_v2(run_id: str, records: List[DatabaseRow]) -> int:
    """
    Persist validated DatabaseRow records into inventory_databases_v2.

    Returns the number of records inserted.
    """
    db: Session = SessionLocal()
    inserted = 0

    try:
        for rec in records:
            obj = InventoryDatabaseV2(
                run_id=run_id,
                hostname=rec.hostname,
                db_name=rec.db_name,
                db_engine=rec.db_engine,
                engine_version=rec.engine_version,
                environment=rec.environment,
                platform=rec.platform,
                cluster_name=rec.cluster_name,
                port=rec.port,
                db_role=rec.db_role,
                ha_enabled=rec.ha_enabled,
                criticality=rec.criticality,
                owner=rec.owner,
                cpu_cores=rec.cpu_cores,
                memory_gb=rec.memory_gb,
                storage_gb=rec.storage_gb,
                allocated_storage_gb=rec.allocated_storage_gb,
                used_storage_gb=rec.used_storage_gb,
                is_cloud=rec.is_cloud,
                cloud_provider=rec.cloud_provider,
                region=rec.region,
                tags=rec.tags,
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
