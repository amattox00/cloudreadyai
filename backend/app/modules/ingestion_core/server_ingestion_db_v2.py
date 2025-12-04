"""
app/modules/ingestion_core/server_ingestion_db_v2.py

DB helper functions for writing server ingestion results
into the *v2* tables:

  - ingestion_runs_v2
  - inventory_server_v2

This keeps us completely separate from the legacy `servers` /
`ingestion_runs` schema.
"""

from __future__ import annotations

from typing import Optional
from uuid import uuid4

from sqlalchemy.orm import Session

from app.modules.ingestion_core.server_ingestion_core import ServerRow
from app.models.ingestion_run_v2 import IngestionRunV2
from app.models.inventory_server_v2 import InventoryServerV2


def ensure_run_v2(db: Session, run_id: str) -> IngestionRunV2:
    """
    Make sure there's a row in ingestion_runs_v2 for this run_id.

    We keep this as minimal as possible so we don't fight unknown
    columns on the model. If the model has a `status` field, we'll set it.
    """
    run = (
        db.query(IngestionRunV2)
        .filter(IngestionRunV2.run_id == run_id)
        .one_or_none()
    )
    if run is not None:
        return run

    # Minimal constructor: only pass run_id (which we know exists)
    run = IngestionRunV2(run_id=run_id)

    # If the model happens to have a 'status' column, set a default
    if hasattr(run, "status"):
        setattr(run, "status", "NEW")

    db.add(run)
    db.flush()
    return run


def persist_server_row_v2(
    db: Session,
    row: ServerRow,
    run_id: str,
) -> InventoryServerV2:
    """
    Persist a single validated ServerRow into inventory_servers_v2.

    We map only fields that actually exist on InventoryServerV2.
    Later we can derive cpu_usage/ram_usage/storage_usage from
    performance data instead of raw cores/GB.
    """

    # Optional role if your ServerRow has it; otherwise this will be None
    role_value = getattr(row, "role", None)

    server = InventoryServerV2(
        run_id=run_id,
        hostname=row.hostname,
        role=role_value,
        os=row.os,
        environment=row.environment,
        # cpu_usage, ram_usage, storage_usage left as NULL for now
    )

    db.add(server)
    return server
