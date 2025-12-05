from sqlalchemy import Column, Integer, String, Float, Boolean
from app.db import Base


class InventoryLicenseV2(Base):
    __tablename__ = "inventory_licenses_v2"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, index=True, nullable=False)

    hostname = Column(String, index=True, nullable=True)
    product_name = Column(String, index=True, nullable=False)
    vendor = Column(String, nullable=True)
    license_type = Column(String, nullable=True)
    metric = Column(String, nullable=True)
    environment = Column(String, index=True, nullable=True)

    cores_licensed = Column(Float, nullable=True)
    users_licensed = Column(Float, nullable=True)

    expiry_date = Column(String, nullable=True)
    cost_per_year = Column(Float, nullable=True)
    maintenance_per_year = Column(Float, nullable=True)

    po_number = Column(String, nullable=True)
    owner = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    tags = Column(String, nullable=True)
