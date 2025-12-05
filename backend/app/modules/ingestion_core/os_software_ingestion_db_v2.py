from __future__ import annotations

from typing import Iterable

from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models.inventory_os_software_v2 import InventoryOSSoftwareV2
from app.modules.ingestion_core.os_software_ingestion_v2 import OSSoftwareRow


def persist_os_software_records_v2(
    run_id: str,
    records: Iterable[OSSoftwareRow],
) -> int:
    """
    Persist validated OSSoftwareRow records into inventory_os_software_v2.
    """
    db: Session = SessionLocal()
    inserted = 0
    try:
        for rec in records:
            row = InventoryOSSoftwareV2(
                run_id=run_id,
                hostname=rec.hostname,
                environment=rec.environment,
                os_name=rec.os_name,
                os_version=rec.os_version,
                os_release=rec.os_release,
                kernel_version=rec.kernel_version,
                patch_level=rec.patch_level,
                middleware_stack=rec.middleware_stack,
                java_version=rec.java_version,
                dotnet_version=rec.dotnet_version,
                web_server=rec.web_server,
                db_client=rec.db_client,
                installed_software=rec.installed_software,
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
