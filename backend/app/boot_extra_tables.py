"""
Create extra tables that are not covered by the main Alembic migrations yet.

We use this as a bridge for the v2 ingestion pipeline while the schema
is still evolving. It is safe to run multiple times.
"""

import os

from sqlalchemy import create_engine

from app.db import Base

# Build our own sync engine here so we don't depend on app.db exporting one.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://cloudready:cloudready@127.0.0.1:5432/cloudready",
)

engine = create_engine(DATABASE_URL, future=True)

# Import model modules so SQLAlchemy registers all mapped classes
# (We don't need the class names here; importing the modules is enough.)
from app.models import (  # noqa: F401
    inventory_server_v2,
    inventory_storage_v2,
    inventory_database_v2,
    inventory_application_v2,
    inventory_dependency_v2,
    inventory_network_v2,
    inventory_os_software_v2,
    inventory_business_v2,
    inventory_utilization_v2,
    inventory_license_v2,
    ingestion_run_v2,
)


def main() -> None:
    print("Creating extra tables for v2 ingestion pipeline...")
    Base.metadata.create_all(bind=engine)
    print("Done creating extra tables.")


if __name__ == "__main__":
    main()
