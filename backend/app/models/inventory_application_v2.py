from sqlalchemy import Boolean, Column, Float, Integer, String

from app.db import Base


class InventoryApplicationV2(Base):
    """
    Inventory of applications for v2 ingestion.

    One row per (run_id, app_name).
    """

    __tablename__ = "inventory_applications_v2"

    id = Column(Integer, primary_key=True, index=True)

    run_id = Column(String, index=True, nullable=False)
    app_name = Column(String, index=True, nullable=False)

    owner = Column(String, nullable=True)
    business_unit = Column(String, nullable=True)
    environment = Column(String, index=True, nullable=True)
    description = Column(String, nullable=True)
    tier = Column(String, nullable=True)
    sla_hours = Column(Float, nullable=True)
    criticality = Column(String, nullable=True)

    depends_on_servers = Column(String, nullable=True)
    depends_on_databases = Column(String, nullable=True)

    tags = Column(String, nullable=True)
