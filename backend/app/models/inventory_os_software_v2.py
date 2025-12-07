from sqlalchemy import Column, Integer, String, Float, Boolean, Index
from app.db import Base


class InventoryOsSoftwareV2(Base):
    __tablename__ = "inventory_os_software_v2"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, index=True, nullable=False)

    hostname = Column(String, index=True, nullable=False)
    environment = Column(String, index=True, nullable=True)

    os_name = Column(String, nullable=True)
    os_version = Column(String, nullable=True)
    os_edition = Column(String, nullable=True)
    os_family = Column(String, nullable=True)
    architecture = Column(String, nullable=True)
    patches = Column(String, nullable=True)
    lifecycle_phase = Column(String, nullable=True)
    eol_date = Column(String, nullable=True)
    support_vendor = Column(String, nullable=True)

    notes = Column(String, nullable=True)
    tags = Column(String, nullable=True)


Index("ix_inventory_os_software_v2_run_id", InventoryOsSoftwareV2.run_id)
Index("ix_inventory_os_software_v2_hostname", InventoryOsSoftwareV2.hostname)
Index("ix_inventory_os_software_v2_environment", InventoryOsSoftwareV2.environment)
