import csv
from typing import Dict

from sqlalchemy.orm import Session

from app.models.app_dependency import AppDependency


EXPECTED_HEADERS = [
    "app_id",
    "depends_on_app_id",
    "dependency_type",
    "notes",
]


def ingest_dependencies_csv(db: Session, run_id: str, csv_path: str) -> Dict[str, int]:
    """
    Ingest an Application Dependencies CSV from a local file path.

    Expected columns:
      app_id, depends_on_app_id, dependency_type, notes
    """
    rows_ingested = 0

    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)

        if reader.fieldnames is None:
            raise ValueError("Dependencies CSV appears to have no header row.")

        missing = [h for h in EXPECTED_HEADERS if h not in reader.fieldnames]
        if missing:
            raise ValueError(
                f"Missing expected columns in dependencies CSV: {', '.join(missing)}"
            )

        for row in reader:
            if not row:
                continue

            record = AppDependency(
                run_id=run_id,
                app_id=(row.get("app_id") or "").strip(),
                depends_on_app_id=(row.get("depends_on_app_id") or "").strip(),
                dependency_type=(row.get("dependency_type") or "").strip(),
                notes=(row.get("notes") or "").strip(),
            )

            db.add(record)
            rows_ingested += 1

        db.commit()

    return {"rows_ingested": rows_ingested}
