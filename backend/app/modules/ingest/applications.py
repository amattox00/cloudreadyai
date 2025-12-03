import csv
from typing import Dict

from sqlalchemy.orm import Session

from app.models.application import Application


EXPECTED_HEADERS = [
    "app_id",
    "app_name",
    "server_id",
    "owner",
    "criticality",
    "business_unit",
]


def ingest_applications_csv(db: Session, run_id: str, csv_path: str) -> Dict[str, int]:
    """
    Ingest an Applications CSV from a local file path.

    Expected columns:
      app_id, app_name, server_id, owner, criticality, business_unit
    """
    rows_ingested = 0

    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)

        # Soft header validation
        if reader.fieldnames is None:
            raise ValueError("Applications CSV appears to have no header row.")

        missing = [h for h in EXPECTED_HEADERS if h not in reader.fieldnames]
        if missing:
            raise ValueError(f"Missing expected columns in applications CSV: {', '.join(missing)}")

        for row in reader:
            if not row:
                continue

            record = Application(
                run_id=run_id,
                app_id=(row.get("app_id") or "").strip(),
                app_name=(row.get("app_name") or "").strip(),
                server_id=(row.get("server_id") or "").strip(),
                owner=(row.get("owner") or "").strip(),
                criticality=(row.get("criticality") or "").strip(),
                business_unit=(row.get("business_unit") or "").strip(),
            )

            db.add(record)
            rows_ingested += 1

        db.commit()

    return {"rows_ingested": rows_ingested}
