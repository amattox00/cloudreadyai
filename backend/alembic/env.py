import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# -------------------------------------------------------------------
# Make sure the 'app' package is importable
# -------------------------------------------------------------------
# This puts the backend root (which contains 'app/') on sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, os.pardir))
if project_root not in sys.path:
    sys.path.append(project_root)

# -------------------------------------------------------------------
# Alembic Config object
# -------------------------------------------------------------------
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# -------------------------------------------------------------------
# Import your SQLAlchemy Base and models so Alembic can see them
# -------------------------------------------------------------------
from app.db import Base

# Import ALL models that should be migratable
# (Core models are likely imported elsewhere; here we make sure
#  the new Analysis models are included.)
from app.modules.analysis.models.analysis_run import AnalysisRun
from app.modules.analysis.models.server_profile import ServerProfile
from app.modules.analysis.models.app_profile import AppProfile
from app.modules.analysis.models.dependency_link import DependencyLink
from app.modules.analysis.models.rightsizing_result import RightsizingResult
from app.modules.analysis.models.placement_result import PlacementResult
from app.modules.analysis.models.risk_flag import RiskFlag

# If you have other existing models (runs, ingestion, etc.) that were already
# in use with Alembic, they are usually imported in app.db or other modules
# brought into that file. As long as they are reachable from Base.metadata,
# Alembic will see them.

# This is what Alembic uses to autogenerate migrations
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    configuration = config.get_section(config.config_ini_section)
    if configuration is None:
        raise RuntimeError("Alembic configuration section not found.")

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
