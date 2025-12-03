from sqlalchemy import Column, Integer, String, Float

from app.db import Base


class InventoryServerV2(Base):
    """
    Simple v2 server inventory tied to ingestion_runs_v2 via run_id.

    This is used as the source for building analysis.server_profiles.
    """

    __tablename__ = "inventory_servers_v2"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, index=True, nullable=False)

    hostname = Column(String, nullable=False)
    role = Column(String, nullable=True)
    os = Column(String, nullable=True)
    environment = Column(String, nullable=True)

    cpu_usage = Column(Float, nullable=True)
    ram_usage = Column(Float, nullable=True)
    storage_usage = Column(Float, nullable=True)
