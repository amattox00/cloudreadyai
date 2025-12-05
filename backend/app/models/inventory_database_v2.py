from sqlalchemy import Boolean, Column, Float, Integer, String

from app.db import Base


class InventoryDatabaseV2(Base):
    """
    Inventory of databases for v2 ingestion.

    One row per (run_id, db_name, hostname).
    """

    __tablename__ = "inventory_databases_v2"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, index=True, nullable=False)

    hostname = Column(String, nullable=False, index=True)
    db_name = Column(String, nullable=False, index=True)
    db_engine = Column(String, nullable=False)
    engine_version = Column(String, nullable=True)

    environment = Column(String, nullable=True)
    platform = Column(String, nullable=True)
    cluster_name = Column(String, nullable=True)
    port = Column(Integer, nullable=True)
    db_role = Column(String, nullable=True)
    ha_enabled = Column(Boolean, nullable=True)
    criticality = Column(String, nullable=True)
    owner = Column(String, nullable=True)

    cpu_cores = Column(Integer, nullable=True)
    memory_gb = Column(Float, nullable=True)
    storage_gb = Column(Float, nullable=True)
    allocated_storage_gb = Column(Float, nullable=True)
    used_storage_gb = Column(Float, nullable=True)

    is_cloud = Column(Boolean, nullable=True)
    cloud_provider = Column(String, nullable=True)
    region = Column(String, nullable=True)

    tags = Column(String, nullable=True)
