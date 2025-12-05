from sqlalchemy import Boolean, Column, Float, Integer, String

from app.db import Base


class InventoryStorageV2(Base):
    """
    Inventory of storage volumes for v2 ingestion.

    One row per (run_id, volume_id).
    """

    __tablename__ = "inventory_storage_v2"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, index=True, nullable=False)

    volume_id = Column(String, nullable=False, index=True)
    datastore = Column(String, nullable=True)
    storage_array = Column(String, nullable=True)

    hostname = Column(String, nullable=True)
    environment = Column(String, nullable=True)

    protocol = Column(String, nullable=True)
    tier = Column(String, nullable=True)
    raid_type = Column(String, nullable=True)

    capacity_gb = Column(Float, nullable=True)
    used_gb = Column(Float, nullable=True)
    provisioned_gb = Column(Float, nullable=True)
    iops = Column(Float, nullable=True)
    latency_ms = Column(Float, nullable=True)

    storage_type = Column(String, nullable=True)  # block, file, object, etc.
    is_replicated = Column(Boolean, nullable=True)

    notes = Column(String, nullable=True)
