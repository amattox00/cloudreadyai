from sqlalchemy import Column, Integer, String, Float
from app.db import Base


class RightsizingResult(Base):
    """
    Rightsizing recommendation per server:
    - current vs recommended vCPU/RAM/storage
    """
    __tablename__ = "rightsizing_results"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, index=True)

    server_id = Column(String)

    current_vcpu = Column(Integer)
    recommended_vcpu = Column(Integer)

    current_ram = Column(Float)          # GB
    recommended_ram = Column(Float)      # GB

    current_storage = Column(Float)      # GB
    recommended_storage = Column(Float)  # GB
