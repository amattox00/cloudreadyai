from __future__ import annotations

from sqlalchemy import Column, Integer, String

from app.db import Base


class InventoryOSSoftwareV2(Base):
    """
    v2 inventory: OS + key software per host.
    """

    __tablename__ = "inventory_os_software_v2"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, index=True, nullable=False)

    hostname = Column(String, index=True, nullable=False)
    environment = Column(String, index=True, nullable=True)

    os_name = Column(String, nullable=False)
    os_version = Column(String, nullable=True)
    os_release = Column(String, nullable=True)
    kernel_version = Column(String, nullable=True)

    patch_level = Column(String, nullable=True)

    middleware_stack = Column(String, nullable=True)
    java_version = Column(String, nullable=True)
    dotnet_version = Column(String, nullable=True)
    web_server = Column(String, nullable=True)
    db_client = Column(String, nullable=True)

    installed_software = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    tags = Column(String, nullable=True)
