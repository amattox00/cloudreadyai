from sqlalchemy import Column, String, Integer, Numeric, JSON, TIMESTAMP
from sqlalchemy.sql import func
from app.db import Base

class Server(Base):
    __tablename__ = "servers"

    server_id = Column(String, primary_key=True, index=True)
    run_id = Column(String, index=True)
    hostname = Column(String)
    ip = Column(String)
    cpu_cores = Column(Integer)
    memory_gb = Column(Numeric)
    os = Column(String)
    environment = Column(String)

    raw = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=func.now())
