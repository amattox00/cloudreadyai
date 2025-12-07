from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.db import Base


class IngestionRunV2(Base):
    """
    Tracks high-level ingestion + rollup status for a given run_id.

    NOTE:
    - We deliberately do NOT try to be super fancy here.
    - Counts can be populated either by the ingestion endpoints
      OR by a rollup job that recomputes counts from inventory_*_v2 tables.
    """

    __tablename__ = "ingestion_runs_v2"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, unique=True, index=True, nullable=False)

    # Where this run came from (csv, vcenter, snow, etc.)
    source = Column(String, nullable=True)

    # Simple lifecycle:
    #  - pending   → created, no data yet
    #  - in_progress → some slices arriving
    #  - partial   → not all slices present, but usable
    #  - complete  → all expected slices present
    #  - failed    → ingestion errors
    status = Column(String, nullable=False, default="pending")

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    last_ingested_at = Column(DateTime(timezone=True), nullable=True)

    # Slice counts (row counts by run_id)
    servers_count = Column(Integer, nullable=False, default=0)
    storage_count = Column(Integer, nullable=False, default=0)
    databases_count = Column(Integer, nullable=False, default=0)
    applications_count = Column(Integer, nullable=False, default=0)
    dependencies_count = Column(Integer, nullable=False, default=0)
    networks_count = Column(Integer, nullable=False, default=0)
    os_software_count = Column(Integer, nullable=False, default=0)
    business_count = Column(Integer, nullable=False, default=0)
    utilization_count = Column(Integer, nullable=False, default=0)
    licenses_count = Column(Integer, nullable=False, default=0)

    notes = Column(Text, nullable=True)
