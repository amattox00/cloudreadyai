from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.db import Base
from app.models.run import Run  # <-- import the actual Run class


class Workload(Base):
    __tablename__ = "workloads"

    id = Column(Integer, primary_key=True, index=True)

    # FK to the runs table
    run_id = Column(String, ForeignKey("runs.id"), index=True, nullable=False)

    # Basic identity / metadata
    name = Column(String, nullable=False)
    environment = Column(String, nullable=True)  # e.g. "prod", "dev"
    tier = Column(String, nullable=True)         # e.g. "web", "app", "db"
    criticality = Column(String, nullable=True)  # e.g. "high", "medium", "low"

    # Sizing
    cpu_cores = Column(Float, nullable=True)
    memory_gb = Column(Float, nullable=True)
    storage_gb = Column(Float, nullable=True)

    # Utilization (percentages 0–100)
    utilization_cpu = Column(Float, nullable=True)
    utilization_memory = Column(Float, nullable=True)

    # Simple analysis outputs (optional; can be null)
    monthly_cost_estimate = Column(Float, nullable=True)
    migration_risk = Column(String, nullable=True)      # e.g. "low", "medium", "high"
    migration_pattern = Column(String, nullable=True)   # e.g. "rehost", "replatform"

    # Relationship back to Run
    run = relationship(
        Run,              # <-- use the actual class, not the string "Run"
        back_populates="workloads",
    )
