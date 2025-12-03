from sqlalchemy import Column, Integer, String
from app.db import Base


class RiskFlag(Base):
    """
    Risk flags (per server, per run):
    - legacy_os, eol_db, heavy_deps, oversubscribed, etc.
    """
    __tablename__ = "risk_flags"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, index=True)

    server_id = Column(String)
    risk_type = Column(String)   # e.g., "legacy_os", "eol_db", "heavy_deps"
    severity = Column(String)    # e.g., "LOW", "MEDIUM", "HIGH"
    message = Column(String)     # human-readable description
