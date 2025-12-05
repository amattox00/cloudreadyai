from __future__ import annotations

from typing import Iterable, List

from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models.inventory_dependency_v2 import InventoryDependencyV2
from app.modules.ingestion_core.dependencies_ingestion_v2 import DependencyRow


def persist_dependency_records_v2(
    run_id: str,
    records: Iterable[DependencyRow],
) -> int:
    """
    Persist dependencies (v2) into inventory_dependencies_v2.

    Mirrors the pattern used by server/storage/databases/applications v2 DB writers.
    """
    session: Session = SessionLocal()
    inserted = 0

    try:
        for row in records:
            dep = InventoryDependencyV2(
                run_id=run_id,
                app_name=row.app_name,
                environment=row.environment,
                dependency_type=row.dependency_type,
                server_hostname=row.server_hostname,
                database_name=row.database_name,
                database_engine=row.database_engine,
                notes=row.notes,
                tags=row.tags,
            )
            session.add(dep)
            inserted += 1

        session.commit()
        return inserted

    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
