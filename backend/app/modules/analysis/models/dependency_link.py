from sqlalchemy import Column, Integer, String
from app.db import Base


class DependencyLink(Base):
    """
    Directed dependency edge: source_server -> target_server : port/protocol
    """
    __tablename__ = "dependency_links"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, index=True)

    source_server = Column(String)
    target_server = Column(String)
    protocol = Column(String, nullable=True)  # e.g., TCP, UDP
    port = Column(Integer, nullable=True)
