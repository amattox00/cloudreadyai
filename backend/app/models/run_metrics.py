# app/models/run_metrics.py

from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func

from app.db import Base


class RunSliceMetrics(Base):
    """
    Stores per-slice analysis metrics for an ingestion run.

    Example row:
      run_id = "run-69a54e8f"
      slice_name = "apps"
      row_count = 14
      metrics_json = {
        "row_count": 14,
        "env_counts": {"prod": 10, "dev": 4}
      }
    """

    __tablename__ = "run_slice_metrics"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, index=True, nullable=False)
    slice_name = Column(String, index=True, nullable=False)
    row_count = Column(Integer, nullable=False, default=0)
    metrics_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
