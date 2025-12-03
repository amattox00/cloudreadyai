from sqlalchemy import Column, String, Integer, Float
from app.db import Base


class ServerProfile(Base):
    """
    Derived metrics per server for a given run:
    - utilization
    - role
    - environment
    - OS, etc.
    """
    __tablename__ = "server_profiles"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, index=True)
    server_id = Column(String, index=True)

    role = Column(String, nullable=True)  # e.g., "app", "db", "file", "domain_controller"
    cpu_usage = Column(Float, default=0.0)      # avg CPU %
    ram_usage = Column(Float, default=0.0)      # avg RAM %
    storage_usage = Column(Float, default=0.0)  # % or normalized GB

    os = Column(String, nullable=True)
    environment = Column(String, nullable=True)  # prod / dev / test
