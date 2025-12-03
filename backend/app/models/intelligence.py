import uuid
from sqlalchemy import Column, String, Float, Integer, DateTime, Text, JSON
from sqlalchemy.sql import func

# ✅ Use the same Base your other models use
# If your other models import Base from a different module, mirror that.
from app.db import Base


class WorkloadFingerprint(Base):
    __tablename__ = "workload_fingerprints"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workload_id = Column(String, index=True, nullable=False)
    run_id = Column(String, index=True, nullable=False)

    # Aggregated metrics
    avg_cpu_pct = Column(Float)
    peak_cpu_pct = Column(Float)
    avg_mem_pct = Column(Float)
    peak_mem_pct = Column(Float)
    avg_disk_read_iops = Column(Float, nullable=True)
    avg_disk_write_iops = Column(Float, nullable=True)
    avg_disk_latency_ms = Column(Float, nullable=True)
    avg_net_in_kbps = Column(Float, nullable=True)
    avg_net_out_kbps = Column(Float, nullable=True)

    # Derived classifications
    cpu_profile = Column(String)       # idle / steady / bursty / saturated / mixed
    mem_profile = Column(String)       # overprovisioned / balanced / constrained / moderate
    storage_profile = Column(String)   # hot_healthy / hot_constrained / cold / mixed / unknown
    role = Column(String, nullable=True)  # db / app / web / batch / other

    risk_flags = Column(JSON, nullable=True)          # list[str]
    optimization_flags = Column(JSON, nullable=True)  # list[str]

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ReadinessScore(Base):
    __tablename__ = "readiness_scores"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workload_id = Column(String, index=True, nullable=False)
    run_id = Column(String, index=True, nullable=False)

    total_score = Column(Integer, nullable=False)  # 0–100

    compute_score = Column(Integer)
    storage_score = Column(Integer)
    network_score = Column(Integer)
    app_complexity_score = Column(Integer)
    security_risk_score = Column(Integer)

    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MigrationRecommendation(Base):
    __tablename__ = "migration_recommendations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workload_id = Column(String, index=True, nullable=False)
    run_id = Column(String, index=True, nullable=False)

    recommended_strategy = Column(String, nullable=False)  # rehost/replatform/...
    confidence = Column(Float, nullable=False)              # 0–1

    rationale = Column(JSON, nullable=True)               # list[str]
    alternative_strategies = Column(JSON, nullable=True)  # list[{"strategy","reason"}]

    created_at = Column(DateTime(timezone=True), server_default=func.now())
