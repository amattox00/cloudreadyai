from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.sql import func

from app.db import Base


class AnalysisRun(Base):
    """
    Represents an analysis execution for a given ingestion run_id.
    """
    __tablename__ = "analysis_runs"

    # Same run_id as the ingestion run
    run_id = Column(String, primary_key=True, index=True)

    status = Column(String, default="PENDING")  # PENDING, RUNNING, COMPLETED, FAILED
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Optional overall JSON summary (high-level metrics, charts, etc.)
    summary = Column(JSON, nullable=True)
