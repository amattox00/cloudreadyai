from sqlalchemy import Column, Integer, String, Float
from app.db import Base


class PlacementResult(Base):
    """
    Multi-cloud placement recommendation per server.
    """
    __tablename__ = "placement_results"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, index=True)

    server_id = Column(String)
    recommended_cloud = Column(String)  # e.g., "AWS", "Azure", "GCP"
    instance_type = Column(String)      # e.g., "m6i.large"

    monthly_cost = Column(Float)        # estimated monthly cost
    confidence = Column(Float)          # 0.0–1.0 confidence score
