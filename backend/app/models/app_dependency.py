from sqlalchemy import Column, Integer, String, DateTime, func
from app.db import Base


class AppDependency(Base):
    __tablename__ = "app_dependencies"

    id = Column(Integer, primary_key=True, index=True)

    # Link to CloudReadyAI run
    run_id = Column(String, index=True, nullable=False)

    # Relationship: app_id depends on depends_on_app_id
    app_id = Column(String, index=True, nullable=False)
    depends_on_app_id = Column(String, index=True, nullable=False)

    # Type of dependency (API, Database, Messaging, Batch, etc.)
    dependency_type = Column(String)

    notes = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
