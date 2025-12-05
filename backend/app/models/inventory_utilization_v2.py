from sqlalchemy import Column, Integer, String, Float
from app.db import Base


class InventoryUtilizationV2(Base):
    """
    Per-host utilization snapshot for a given run_id.

    This is intentionally simple: enough for analysis and R-score without
    overfitting to any one monitoring tool.
    """

    __tablename__ = "inventory_utilization_v2"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, index=True, nullable=False)

    hostname = Column(String, index=True, nullable=False)
    environment = Column(String, index=True, nullable=True)

    avg_cpu_percent = Column(Float, nullable=True)
    peak_cpu_percent = Column(Float, nullable=True)
    avg_ram_percent = Column(Float, nullable=True)
    peak_ram_percent = Column(Float, nullable=True)

    # Room for future metrics (IOPS, latency, etc.) if you want later
    notes = Column(String, nullable=True)
