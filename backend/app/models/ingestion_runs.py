# app/models/ingestion_runs.py

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.db import Base


class IngestionRun(Base):
    """
    Tracks top-level ingestion run metadata.
    """

    __tablename__ = "ingestion_runs"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, unique=True, index=True, nullable=False)

    # Add missing column
    source = Column(String, nullable=True)

    status = Column(String, nullable=True, default="pending")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
