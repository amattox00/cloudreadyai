from sqlalchemy import Column, String, Integer
from app.db import Base


class AppProfile(Base):
    """
    Application-level derived metrics for a given server in a run.
    """
    __tablename__ = "app_profiles"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, index=True)
    server_id = Column(String, index=True)

    app_name = Column(String)
    dependency_count = Column(Integer, default=0)
