from sqlalchemy import Column, Integer, String, DateTime, Float, func
from app.db import Base


class LicensingMetadata(Base):
    __tablename__ = "licensing_metadata"

    id = Column(Integer, primary_key=True, index=True)

    # Link to CloudReadyAI run
    run_id = Column(String, index=True, nullable=False)

    # Optional linkage to server/app
    server_id = Column(String, index=True)
    app_id = Column(String, index=True)

    # License details
    product_name = Column(String)        # e.g., SQL Server Enterprise
    vendor = Column(String)              # e.g., Microsoft
    license_model = Column(String)       # e.g., per-core, per-CPU, per-user
    license_count = Column(Float)        # e.g., 16 cores, 100 users
    license_key_masked = Column(String)  # partially masked key if needed
    maintenance_expiry = Column(String)  # e.g., "2026-12-31"

    notes = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
