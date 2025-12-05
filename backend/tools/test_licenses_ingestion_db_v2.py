from pathlib import Path

from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.modules.ingestion_core.licenses_ingestion_db_v2 import (
    ingest_licenses_from_csv_db,
)


def main() -> None:
    base_dir = Path(__file__).resolve().parents[1]  # .../cloudreadyai/backend
    csv_path = base_dir.parent / "templates" / "licenses_template_v2.csv"

    print(f"Using CSV: {csv_path}")

    if not csv_path.exists():
        print(f"ERROR: CSV file not found at {csv_path}")
        return

    with csv_path.open("r", encoding="utf-8") as f:
        db: Session = SessionLocal()
        try:
            result, inserted = ingest_licenses_from_csv_db(
                run_id="run-licenses-v2-dbtest-001",
                file_like=f,
                db=db,
            )
        finally:
            db.close()

    print("\n--- Licenses Ingestion v2 (Validation) ---")
    print(f"run_id         : {result.run_id}")
    print(f"rows_processed : {result.rows_processed}")
    print(f"rows_successful: {result.rows_successful}")
    print(f"rows_failed    : {result.rows_failed}")
    print("errors:")
    if not result.errors:
        print("  (none)")
    else:
        for e in result.errors:
            print(f"  - {e}")

    print("\n--- DB Write ---")
    print(f"Inserted rows into inventory_licenses_v2: {inserted}")


if __name__ == "__main__":
    main()
