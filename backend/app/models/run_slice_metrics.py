from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.dialects.postgresql import JSON

from app.db import Base


class RunSliceMetric(Base):
    """
    Stores per-run, per-slice analysis metrics as a single JSON blob.

    Example row:

      run_id      = "run-69a54e8f"
      slice_name  = "storage"
      row_count   = 4
      metrics_json = {"row_count": 4, "total_size_gb": 0.0}
    """

    __tablename__ = "run_slice_metrics"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, index=True, nullable=False)
    slice_name = Column(String, index=True, nullable=False)

    # High-level summary number (e.g., row count)
    row_count = Column(Integer, nullable=False, default=0)

    # Native Postgres JSON column for arbitrary metrics
    metrics_json = Column(JSON, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
