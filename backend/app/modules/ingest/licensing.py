import csv
from typing import Dict

from sqlalchemy.orm import Session

from app.models.licensing_metadata import LicensingMetadata


EXPECTED_HEADERS = [
    "server_id",
    "app_id",
    "product_name",
    "vendor",
    "license_model",
    "license_count",
    "license_key_masked",
    "maintenance_expiry",
    "notes",
]


def _parse_float(value: str) -> float | None:
    v = (value or "").strip()
    if not v:
        return None
    try:
        return float(v)
    except ValueError:
        return None


def ingest_licensing_csv(db: Session, run_id: str, csv_path: str) -> Dict[str, int]:
    """
    Ingest licensing metadata from a CSV.

    Expected columns:
      server_id, app_id, product_name, vendor, license_model,
      license_count, license_key_masked, maintenance_expiry, notes
    """
    rows_ingested = 0

    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)

        if reader.fieldnames is None:
            raise ValueError("Licensing CSV appears to have no header row.")

        missing = [h for h in EXPECTED_HEADERS if h not in reader.fieldnames]
        if missing:
            raise ValueError(
                f"Missing expected columns in licensing CSV: {', '.join(missing)}"
            )

        for row in reader:
            if not row:
                continue

            record = LicensingMetadata(
                run_id=run_id,
                server_id=(row.get("server_id") or "").strip(),
                app_id=(row.get("app_id") or "").strip(),
                product_name=(row.get("product_name") or "").strip(),
                vendor=(row.get("vendor") or "").strip(),
                license_model=(row.get("license_model") or "").strip(),
                license_count=_parse_float(row.get("license_count") or ""),
                license_key_masked=(row.get("license_key_masked") or "").strip(),
                maintenance_expiry=(row.get("maintenance_expiry") or "").strip(),
                notes=(row.get("notes") or "").strip(),
            )

            db.add(record)
            rows_ingested += 1

        db.commit()

    return {"rows_ingested": rows_ingested}
