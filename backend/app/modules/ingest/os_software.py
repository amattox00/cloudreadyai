import csv
from typing import Dict

from sqlalchemy.orm import Session

from app.models.os_metadata import OSMetadata


EXPECTED_HEADERS = [
    "server_id",
    "hostname",
    "os_name",
    "os_version",
    "os_family",
    "architecture",
    "primary_role",
    "notes",
]


def ingest_os_csv(db: Session, run_id: str, csv_path: str) -> Dict[str, int]:
    """
    Ingest OS & software metadata from a CSV.

    Expected columns:
      server_id, hostname, os_name, os_version, os_family,
      architecture, primary_role, notes
    """
    rows_ingested = 0

    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)

        if reader.fieldnames is None:
            raise ValueError("OS metadata CSV appears to have no header row.")

        missing = [h for h in EXPECTED_HEADERS if h not in reader.fieldnames]
        if missing:
            raise ValueError(
                f"Missing expected columns in OS metadata CSV: {', '.join(missing)}"
            )

        for row in reader:
            if not row:
                continue

            record = OSMetadata(
                run_id=run_id,
                server_id=(row.get("server_id") or "").strip(),
                hostname=(row.get("hostname") or "").strip(),
                os_name=(row.get("os_name") or "").strip(),
                os_version=(row.get("os_version") or "").strip(),
                os_family=(row.get("os_family") or "").strip(),
                architecture=(row.get("architecture") or "").strip(),
                primary_role=(row.get("primary_role") or "").strip(),
                notes=(row.get("notes") or "").strip(),
            )

            db.add(record)
            rows_ingested += 1

        db.commit()

    return {"rows_ingested": rows_ingested}
