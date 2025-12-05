from __future__ import annotations

from typing import Iterable

from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models.inventory_business_v2 import InventoryBusinessV2
from app.modules.ingestion_core.business_ingestion_v2 import BusinessRow


def persist_business_records_v2(
    run_id: str,
    records: Iterable[BusinessRow],
) -> int:
    """
    Persist validated BusinessRow records into inventory_business_v2.
    """
    db: Session = SessionLocal()
    inserted = 0
    try:
        for rec in records:
            row = InventoryBusinessV2(
                run_id=run_id,
                business_service=rec.business_service,
                app_name=rec.app_name,
                environment=rec.environment,
                business_unit=rec.business_unit,
                business_owner=rec.business_owner,
                executive_owner=rec.executive_owner,
                criticality=rec.criticality,
                rto_hours=rec.rto_hours,
                rpo_hours=rec.rpo_hours,
                revenue_impact_per_hour=rec.revenue_impact_per_hour,
                customer_impact=rec.customer_impact,
                compliance_tags=rec.compliance_tags,
                notes=rec.notes,
                tags=rec.tags,
            )
            db.add(row)
            inserted += 1

        db.commit()
        return inserted
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
