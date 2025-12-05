from __future__ import annotations

from typing import List

from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models.inventory_application_v2 import InventoryApplicationV2
from app.modules.ingestion_core.applications_ingestion_v2 import ApplicationRow


def persist_application_records_v2(run_id: str, records: List[ApplicationRow]) -> int:
    """
    Persist validated ApplicationRow records into inventory_applications_v2.

    Returns the number of records inserted.
    """
    db: Session = SessionLocal()
    inserted = 0

    try:
        for app in records:
            obj = InventoryApplicationV2(
                run_id=run_id,
                app_name=app.app_name,
                owner=app.owner,
                business_unit=app.business_unit,
                environment=app.environment,
                description=app.description,
                tier=app.tier,
                sla_hours=app.sla_hours,
                criticality=app.criticality,
                depends_on_servers=app.depends_on_servers,
                depends_on_databases=app.depends_on_databases,
                tags=app.tags,
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
