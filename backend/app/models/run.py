from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db import Base


class Run(Base):
    __tablename__ = "runs"

    # Primary key for the run, matches what the rest of the app expects
    id = Column(String, primary_key=True, index=True)

    # Optional metadata
    name = Column(String, nullable=True)
    description = Column(String, nullable=True)
    status = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # One-to-many: a run can have many workloads
    workloads = relationship(
        "Workload",
        back_populates="run",
        cascade="all, delete-orphan",
    )
