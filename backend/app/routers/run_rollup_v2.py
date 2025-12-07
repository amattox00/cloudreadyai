from datetime import datetime
from typing import Dict, Any, Optional

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db import get_db
from app.models.ingestion_run_v2 import IngestionRunV2
from app.models.inventory_server_v2 import InventoryServerV2
from app.models.inventory_storage_v2 import InventoryStorageV2
from app.models.inventory_database_v2 import InventoryDatabaseV2
from app.models.inventory_application_v2 import InventoryApplicationV2
from app.models.inventory_dependency_v2 import InventoryDependencyV2
from app.models.inventory_network_v2 import InventoryNetworkV2
from app.models.inventory_business_v2 import InventoryBusinessV2
from app.models.inventory_license_v2 import InventoryLicenseV2
from app.models.inventory_utilization_v2 import InventoryUtilizationV2
from app.models.inventory_os_software_v2 import InventoryOsSoftwareV2

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/v2",
    tags=["Runs v2"],
)


def _safe_count_for_run(
    db: Session,
    model,
    run_id: str,
    label: str,
) -> int:
    """
    Return count(*) for a given run_id on a model.
    Never raises – logs and returns -1 if anything goes wrong.
    """
    try:
        value = (
            db.query(func.count(model.id))
            .filter(model.run_id == run_id)
            .scalar()
        )
        return int(value or 0)
    except Exception as ex:  # noqa: BLE001
        logger.exception(
            "Error counting %s for run_id=%s: %s", label, run_id, ex
        )
        # Important: reset failed transaction so later counts can proceed
        try:
            db.rollback()
        except Exception:
            # If rollback itself fails, just ignore – we still return -1
            logger.exception(
                "Rollback failed after error counting %s for run_id=%s",
                label,
                run_id,
            )
        return -1


@router.get("/runs/{run_id}/rollup")
def get_run_rollup_v2(
    run_id: str,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Lightweight rollup summary for a v2 ingestion run.

    Extremely defensive:
      * Only relies on model.id and model.run_id
      * Wraps all DB access in try/except so we don't throw 500s
    """
    # Try to read the run row, but don't crash if the table/model is off
    run_row: Optional[IngestionRunV2] = None
    try:
        run_row = (
            db.query(IngestionRunV2)
            .filter(IngestionRunV2.run_id == run_id)
            .one_or_none()
        )
    except Exception as ex:  # noqa: BLE001
        logger.exception(
            "Error loading IngestionRunV2 for run_id=%s: %s", run_id, ex
        )

    slice_counts = {
        "servers": _safe_count_for_run(db, InventoryServerV2, run_id, "servers"),
        "storage": _safe_count_for_run(db, InventoryStorageV2, run_id, "storage"),
        "databases": _safe_count_for_run(db, InventoryDatabaseV2, run_id, "databases"),
        "applications": _safe_count_for_run(db, InventoryApplicationV2, run_id, "applications"),
        "dependencies": _safe_count_for_run(db, InventoryDependencyV2, run_id, "dependencies"),
        "networks": _safe_count_for_run(db, InventoryNetworkV2, run_id, "networks"),
        "business": _safe_count_for_run(db, InventoryBusinessV2, run_id, "business"),
        "licenses": _safe_count_for_run(db, InventoryLicenseV2, run_id, "licenses"),
        "utilization": _safe_count_for_run(db, InventoryUtilizationV2, run_id, "utilization"),
        "os_software": _safe_count_for_run(db, InventoryOsSoftwareV2, run_id, "os_software"),
    }

    # Only count non-negative slice counts when summing
    total_assets = sum(v for v in slice_counts.values() if v >= 0)

    # If literally everything is 0 or -1 and there's no run row, treat as 404
    if total_assets == 0 and run_row is None:
        raise HTTPException(
            status_code=404,
            detail=f"No v2 ingestion data found for run_id={run_id}",
        )

    return {
        "run_id": run_id,
        "status": getattr(run_row, "status", "UNKNOWN"),
        "name": getattr(run_row, "name", None),
        "created_at": getattr(run_row, "created_at", None),
        "totals": {
            "assets_ingested": total_assets,
        },
        "slices": slice_counts,
    }
