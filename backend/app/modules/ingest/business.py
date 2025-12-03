import csv
from typing import Dict

from sqlalchemy.orm import Session

from app.models.business_metadata import BusinessMetadata


EXPECTED_HEADERS = [
    "app_id",
    "owner",
    "business_unit",
    "criticality",
    "sla_tier",
    "rto",
    "rpo",
    "notes",
]


def ingest_business_csv(db: Session, run_id: str, csv_path: str) -> Dict[str, int]:
    """
    Ingest a Business Metadata CSV from a local file path.

    Expected columns:
      app_id, owner, business_unit, criticality, sla_tier, rto, rpo, notes
    """
    rows_ingested = 0

    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)

        if reader.fieldnames is None:
            raise ValueError("Business metadata CSV appears to have no header row.")

        missing = [h for h in EXPECTED_HEADERS if h not in reader.fieldnames]
        if missing:
            raise ValueError(
                f"Missing expected columns in business metadata CSV: {', '.join(missing)}"
            )

        for row in reader:
            if not row:
                continue

            record = BusinessMetadata(
                run_id=run_id,
                app_id=(row.get("app_id") or "").strip(),
                owner=(row.get("owner") or "").strip(),
                business_unit=(row.get("business_unit") or "").strip(),
                criticality=(row.get("criticality") or "").strip(),
                sla_tier=(row.get("sla_tier") or "").strip(),
                rto=(row.get("rto") or "").strip(),
                rpo=(row.get("rpo") or "").strip(),
                notes=(row.get("notes") or "").strip(),
            )

            db.add(record)
            rows_ingested += 1

        db.commit()

    return {"rows_ingested": rows_ingested}
