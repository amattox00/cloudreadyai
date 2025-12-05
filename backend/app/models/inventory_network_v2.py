from __future__ import annotations

from sqlalchemy import Boolean, Column, Integer, String

from app.db import Base


class InventoryNetworkV2(Base):
    """
    v2 network/subnet inventory.
    """

    __tablename__ = "inventory_networks_v2"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, index=True, nullable=False)

    subnet_id = Column(String, index=True, nullable=False)
    subnet_cidr = Column(String, nullable=False)

    vlan_id = Column(String, index=True, nullable=True)
    environment = Column(String, index=True, nullable=True)
    datacenter = Column(String, nullable=True)
    zone = Column(String, nullable=True)
    network_name = Column(String, nullable=True)
    purpose = Column(String, nullable=True)

    is_public = Column(Boolean, nullable=True)
    is_dmz = Column(Boolean, nullable=True)

    connected_to = Column(String, nullable=True)
    tags = Column(String, nullable=True)
