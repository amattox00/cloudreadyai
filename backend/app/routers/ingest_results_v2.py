from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.inspection import inspect as sa_inspect

from app.db import get_db

from app.models.inventory_server_v2 import InventoryServerV2
from app.models.inventory_storage_v2 import InventoryStorageV2
from app.models.inventory_database_v2 import InventoryDatabaseV2
from app.models.inventory_application_v2 import InventoryApplicationV2
from app.models.inventory_dependency_v2 import InventoryDependencyV2


router = APIRouter(
    prefix="/v1/ingest/results",
    tags=["ingest-results"],
)


# Slice → (Model, default ordering column name)
SLICE_MODEL_MAP: Dict[str, Tuple[Any, str]] = {
    "servers": (InventoryServerV2, "id"),
    "storage": (InventoryStorageV2, "id"),
    "databases": (InventoryDatabaseV2, "id"),
    "applications": (InventoryApplicationV2, "id"),
    "dependencies": (InventoryDependencyV2, "id"),
}


def _serialize_sqlalchemy(obj: Any) -> Dict[str, Any]:
    """
    Convert a SQLAlchemy model instance to a JSON-safe dict.
    - Only includes mapped column attributes
    - Converts non-serializable types to string as a fallback
    """
    if obj is None:
        return {}

    data: Dict[str, Any] = {}
    mapper = sa_inspect(obj).mapper
    for attr in mapper.column_attrs:
        key = attr.key
        try:
            val = getattr(obj, key)
            # JSON-friendly conversion fallback
            if isinstance(val, (dict, list, str, int, float, bool)) or val is None:
                data[key] = val
            else:
                data[key] = str(val)
        except Exception:
            data[key] = None
    return data


@router.get("/{slice_name}")
def list_ingest_results(
    slice_name: str,
    run_id: str = Query(..., description="Run ID (assessment ID)"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """
    Paginated results explorer for ingested inventory rows (V2 tables).
    This is read-only and safe for MVP demos.
    """
    if slice_name not in SLICE_MODEL_MAP:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported slice '{slice_name}'. Supported: {', '.join(sorted(SLICE_MODEL_MAP.keys()))}",
        )

    Model, order_col_name = SLICE_MODEL_MAP[slice_name]

    # Validate Model has run_id column (expected for inventory v2)
    if not hasattr(Model, "run_id"):
        raise HTTPException(status_code=500, detail=f"Model for slice '{slice_name}' does not have run_id")

    # Total count
    total = (
        db.query(func.count())
        .select_from(Model)
        .filter(Model.run_id == run_id)
        .scalar()
    ) or 0

    # Ordering (best effort)
    order_col = getattr(Model, order_col_name, None)
    q = db.query(Model).filter(Model.run_id == run_id)
    if order_col is not None:
        q = q.order_by(order_col.asc())

    rows = q.offset(offset).limit(limit).all()

    return {
        "slice": slice_name,
        "run_id": run_id,
        "limit": limit,
        "offset": offset,
        "total": int(total),
        "items": [_serialize_sqlalchemy(r) for r in rows],
    }
