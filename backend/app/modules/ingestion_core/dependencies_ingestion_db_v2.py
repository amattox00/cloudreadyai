from __future__ import annotations

from typing import Iterable, List

from sqlalchemy.orm import Session

from app.models.app_dependency import AppDependency
from app.modules.ingestion_core.dependencies_ingestion_v2 import DependencyEdge


def persist_dependencies_v2(
    *,
    db: Session,
    run_id: str,
    records: List[DependencyEdge],
    replace_existing: bool = True,
) -> int:
    """
    Persist dependency edges into app_dependencies (AppDependency).

    MVP approach:
      - Optionally delete existing dependencies for run_id
      - Insert rows
    """
    if not run_id:
        return 0

    if replace_existing:
        db.query(AppDependency).filter(AppDependency.run_id == run_id).delete()

    inserted = 0
    for r in records:
        db.add(
            AppDependency(
                run_id=run_id,
                app_id=r.app_id,
                depends_on_app_id=r.depends_on_app_id,
                dependency_type=r.dependency_type,
                notes=r.notes,
            )
        )
        inserted += 1

    db.commit()
    return inserted
