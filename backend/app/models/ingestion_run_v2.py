from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime

from app.db import Base


class IngestionRunV2(Base):
    """
    Simple v2 ingestion run registry.

    This is intentionally minimal and separate from any legacy or
    experimental run tables.
    """

    __tablename__ = "ingestion_runs_v2"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    status = Column(String, nullable=False, default="NEW")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
