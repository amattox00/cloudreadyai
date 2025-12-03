from sqlalchemy import Column, Integer, String, DateTime, Float, func
from app.db import Base


class UtilizationMetric(Base):
    __tablename__ = "utilization_metrics"

    id = Column(Integer, primary_key=True, index=True)

    # Link to CloudReadyAI run
    run_id = Column(String, index=True, nullable=False)

    # Link back to the server
    server_id = Column(String, index=True, nullable=False)

    # Utilization metrics (averages / peaks over an observation window)
    cpu_avg = Column(Float)          # percent
    cpu_peak = Column(Float)         # percent
    ram_avg_gb = Column(Float)
    ram_peak_gb = Column(Float)
    storage_avg_gb = Column(Float)
    storage_peak_gb = Column(Float)

    observation_window = Column(String)  # e.g., "30d", "7d", "90d"
    notes = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
