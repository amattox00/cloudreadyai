from sqlalchemy import Column, String, Integer, JSON, TIMESTAMP
from sqlalchemy.sql import func
from app.db import Base

class Network(Base):
    __tablename__ = "inventory_networks"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, index=True)
    device_name = Column(String)
    device_type = Column(String)
    role = Column(String)
    mgmt_ip = Column(String)
    site = Column(String)
    vlan = Column(String)
    subnet = Column(String)

    raw = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
