from sqlalchemy import Column, Integer, String

from app.db import Base


class Storage(Base):
    __tablename__ = "storage"

    id = Column(Integer, primary_key=True, index=True)

    # Logical ingestion run ID
    run_id = Column(String, index=True, nullable=False)

    volume_id = Column(String, nullable=False)
    server_id = Column(String, nullable=True)

    size_gb = Column(Integer, nullable=False, default=0)

    # e.g. "block", "file", "object"
    storage_type = Column(String, nullable=True)
