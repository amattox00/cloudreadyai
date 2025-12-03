from sqlalchemy import Column, Integer, String, DateTime, func
from app.db import Base


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)

    # Link to CloudReadyAI run
    run_id = Column(String, index=True, nullable=False)

    # Application identifiers
    app_id = Column(String, index=True)
    app_name = Column(String, index=True)
    server_id = Column(String, index=True)

    # Ownership / business context
    owner = Column(String)
    criticality = Column(String)      # e.g. Critical, High, Medium, Low
    business_unit = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
