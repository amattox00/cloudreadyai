from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, JSON
from app.db import Base


class AnalysisRun(Base):
    __tablename__ = "analysis_run"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String(255), unique=True, nullable=False, index=True)
    summary_json = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
