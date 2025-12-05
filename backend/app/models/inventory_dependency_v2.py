from __future__ import annotations

from sqlalchemy import Boolean, Column, Integer, String

from app.db import Base


class InventoryDependencyV2(Base):
    """
    Application dependency (v2) records:

    - app_name + environment
    - dependency_type = "server" or "database"
    - server_hostname for server dependencies
    - database_name + database_engine for DB dependencies
    """

    __tablename__ = "inventory_dependencies_v2"

    id = Column(Integer, primary_key=True, index=True)

    run_id = Column(String, index=True, nullable=False)

    app_name = Column(String, index=True, nullable=False)
    environment = Column(String, index=True, nullable=True)

    dependency_type = Column(String, index=True, nullable=False)  # "server" or "database"

    server_hostname = Column(String, index=True, nullable=True)
    database_name = Column(String, index=True, nullable=True)
    database_engine = Column(String, nullable=True)

    notes = Column(String, nullable=True)
    tags = Column(String, nullable=True)
