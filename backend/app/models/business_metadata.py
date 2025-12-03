from sqlalchemy import Column, Integer, String, DateTime, func
from app.db import Base


class BusinessMetadata(Base):
    __tablename__ = "business_metadata"

    id = Column(Integer, primary_key=True, index=True)

    # Link to CloudReadyAI run
    run_id = Column(String, index=True, nullable=False)

    # Link back to the application
    app_id = Column(String, index=True, nullable=False)

    # Business context
    owner = Column(String)             # e.g., Jane Doe
    business_unit = Column(String)     # e.g., Finance, HR, Sales
    criticality = Column(String)       # e.g., Critical, High, Medium, Low
    sla_tier = Column(String)          # e.g., Gold, Silver, Bronze
    rto = Column(String)               # Recovery Time Objective, e.g., "1h", "4h"
    rpo = Column(String)               # Recovery Point Objective, e.g., "15m", "1h"

    notes = Column(String)             # freeform notes (optional)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
