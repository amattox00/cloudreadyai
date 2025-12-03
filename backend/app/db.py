import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def _sync_url_from_env() -> str:
    url = os.getenv("DATABASE_URL", "postgresql+psycopg://cloudready:cloudready@127.0.0.1:5432/cloudready")
    return url.replace("+asyncpg", "+psycopg")

ENGINE = create_engine(_sync_url_from_env(), pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=ENGINE, autoflush=False, autocommit=False, future=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----------------------------------------------------------------------
# Ensure SQLAlchemy Base is available for model modules
# ----------------------------------------------------------------------
try:
    Base  # type: ignore[name-defined]
except NameError:  # pragma: no cover
    from sqlalchemy.orm import declarative_base
    Base = declarative_base()
