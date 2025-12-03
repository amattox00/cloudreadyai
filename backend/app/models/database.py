from sqlalchemy import Column, Integer, String, Float, DateTime, func
from app.db import Base


class Database(Base):
    __tablename__ = "databases"

    id = Column(Integer, primary_key=True, index=True)

    # Link to CloudReadyAI run
    run_id = Column(String, index=True, nullable=False)

    # Database identifiers
    db_id = Column(String, index=True)
    server_id = Column(String, index=True)

    # Core DB attributes
    db_type = Column(String, nullable=False)        # PostgreSQL, Oracle, SQL Server, MySQL
    version = Column(String)
    instance_name = Column(String)

    # Capacity
    size_gb = Column(Float)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
