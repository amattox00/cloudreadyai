from sqlalchemy import Column, Integer, String, DateTime, func
from app.db import Base


class OSMetadata(Base):
    __tablename__ = "os_metadata"

    id = Column(Integer, primary_key=True, index=True)

    # Link to CloudReadyAI run
    run_id = Column(String, index=True, nullable=False)

    # Link back to the server
    server_id = Column(String, index=True, nullable=False)
    hostname = Column(String, index=True)

    # OS / software details
    os_name = Column(String)         # e.g., Windows Server, RHEL, Ubuntu
    os_version = Column(String)      # e.g., 2019, 8.6, 22.04
    os_family = Column(String)       # e.g., Windows, Linux, Unix
    architecture = Column(String)    # e.g., x86_64, arm64
    primary_role = Column(String)    # e.g., DB Server, Web Server, App Server
    notes = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
