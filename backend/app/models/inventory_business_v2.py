from __future__ import annotations

from sqlalchemy import Column, Integer, String, Float

from app.db import Base


class InventoryBusinessV2(Base):
    """
    v2 inventory: business metadata per service / app.
    """

    __tablename__ = "inventory_business_v2"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, index=True, nullable=False)

    business_service = Column(String, index=True, nullable=False)
    app_name = Column(String, index=True, nullable=True)
    environment = Column(String, index=True, nullable=True)

    business_unit = Column(String, nullable=True)
    business_owner = Column(String, nullable=True)
    executive_owner = Column(String, nullable=True)

    criticality = Column(String, nullable=True)

    rto_hours = Column(Float, nullable=True)
    rpo_hours = Column(Float, nullable=True)
    revenue_impact_per_hour = Column(Float, nullable=True)

    customer_impact = Column(String, nullable=True)
    compliance_tags = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    tags = Column(String, nullable=True)
