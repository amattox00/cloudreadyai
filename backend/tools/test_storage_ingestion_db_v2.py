"""
End-to-end test for storage ingestion v2:

- Reads storage_template_v2.csv
- Runs validation (ingest_storage_from_csv)
- Writes records into inventory_storage_v2
- Prints a summary
"""

from pathlib import Path

from app.modules.ingestion_core.storage_ingestion_v2 import ingest_storage_from_csv
from app.modules.ingestion_core.storage_ingestion_db_v2 import (
    persist_storage_records_v2,
)


def main() -> None:
    run_id = "run-storage-v2-dbtest-001"

    csv_path = (
        Path(__file__)
        .resolve()
        .parent  # tools/
        .parent  # backend/
        .parent  # cloudreadyai/
        / "templates"
        / "storage_template_v2.csv"
    )

    print(f"Using CSV: {csv_path}")
    if not csv_path.exists():
        print(f"ERROR: CSV file not found at {csv_path}")
        return

    # Step 1: CSV → validated StorageRow records
    with csv_path.open("r", encoding="utf-8") as f:
        result = ingest_storage_from_csv(run_id=run_id, file_like=f)

    print("\n--- Storage Ingestion v2 (Validation) ---")
    print(f"run_id         : {result.run_id}")
    print(f"rows_processed : {result.rows_processed}")
    print(f"rows_successful: {result.rows_successful}")
    print(f"rows_failed    : {result.rows_failed}")
    print("errors:")
    if not result.errors:
        print("  (none)")
    else:
        for err in result.errors:
            print(f"  - {err}")

    if not result.records:
        print("\nNo valid records to insert into DB.")
        return

    # Step 2: Validated records → DB
    inserted = persist_storage_records_v2(run_id=run_id, records=result.records)

    print("\n--- DB Write ---")
    print(f"Inserted rows into inventory_storage_v2: {inserted}")


if __name__ == "__main__":
    main()
