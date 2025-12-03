import csv
from typing import Dict

from sqlalchemy.orm import Session
from app.models.database import Database


EXPECTED_HEADERS = [
    "db_id",
    "server_id",
    "db_type",
    "version",
    "size_gb",
    "instance_name",
]


def ingest_databases_csv(db: Session, run_id: str, csv_path: str) -> Dict[str, int]:
    """
    Ingest a Databases CSV from a local file path.

    Expected columns:
      db_id, server_id, db_type, version, size_gb, instance_name
    """

    rows_ingested = 0

    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)

        # Validate headers (soft validation)
        missing = [h for h in EXPECTED_HEADERS if h not in reader.fieldnames]
        if missing:
            raise ValueError(f"Missing expected columns: {', '.join(missing)}")

        for row in reader:
            if not row:
                continue

            # Safe parse for float
            size_raw = (row.get("size_gb") or "").strip()
            try:
                size_gb = float(size_raw) if size_raw else None
            except ValueError:
                size_gb = None

            record = Database(
                run_id=run_id,
                db_id=(row.get("db_id") or "").strip(),
                server_id=(row.get("server_id") or "").strip(),
                db_type=(row.get("db_type") or "").strip(),
                version=(row.get("version") or "").strip(),
                instance_name=(row.get("instance_name") or "").strip(),
                size_gb=size_gb,
            )

            db.add(record)
            rows_ingested += 1

        db.commit()

    return {"rows_ingested": rows_ingested}
