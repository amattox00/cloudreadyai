# app/create_tables.py

from app.db import Base, SessionLocal

# Import all models so they are registered on Base.metadata
# (They don't need to be used directly here.)
from app.models import (  # noqa: F401
    ingestion_runs,
    run_slice_metrics,
    storage,
    workload,
    server,
    networks,
)


def main() -> None:
    """
    Create all database tables defined on SQLAlchemy models.

    This reuses the same engine that SessionLocal is bound to,
    so it will create tables in the same Postgres DB the app uses.
    """
    print("🔧 Creating all tables...")

    db = SessionLocal()
    try:
        engine = db.get_bind()
        Base.metadata.create_all(bind=engine)
    finally:
        db.close()

    print("✅ Done creating tables.")


if __name__ == "__main__":
    main()
