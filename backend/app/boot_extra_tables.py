"""
Bootstraps extra tables that are not yet managed by Alembic migrations.

Currently:
  - ingestion_runs_v2
  - inventory_servers_v2

This module is imported for its side effects from routers, so that the
tables are created automatically on startup if they do not already exist.
"""

from app.db import Base, get_db
from app.models.ingestion_run_v2 import IngestionRunV2
from app.models.inventory_server_v2 import InventoryServerV2
from app.models.inventory_storage_v2 import InventoryStorageV2
from app.models.inventory_database_v2 import InventoryDatabaseV2
from app.models.inventory_application_v2 import InventoryApplicationV2
from app.models.inventory_dependency_v2 import InventoryDependencyV2
from app.models.inventory_network_v2 import InventoryNetworkV2
from app.models.inventory_os_software_v2 import InventoryOSSoftwareV2
from app.models.inventory_business_v2 import InventoryBusinessV2
from app.models.inventory_utilization_v2 import InventoryUtilizationV2
from app.models.inventory_license_v2 import InventoryLicenseV2

def _get_engine():
    """
    Obtain the SQLAlchemy engine indirectly via a DB session.

    We don't import `engine` directly from app.db to avoid issues if the
    symbol isn't exported there.
    """
    db_gen = get_db()
    db = next(db_gen)
    try:
        return db.get_bind()
    finally:
        try:
            db_gen.close()  # close generator if possible
        except Exception:
            db.close()


_engine = _get_engine()

# Create only the new v2 tables; this will not touch other tables.
Base.metadata.create_all(
    bind=_engine,
    tables=[
        IngestionRunV2.__table__,
        InventoryServerV2.__table__,
        InventoryStorageV2.__table__,
        InventoryDatabaseV2.__table__,
        InventoryApplicationV2.__table__,
        InventoryDependencyV2.__table__,
        InventoryNetworkV2.__table__,
        InventoryOSSoftwareV2.__table__,
        InventoryBusinessV2.__table__,
        InventoryUtilizationV2.__table__,
        InventoryLicenseV2.__table__,


    ],
)
