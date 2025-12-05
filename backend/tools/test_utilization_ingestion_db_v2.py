import pathlib

from app.modules.ingestion_core.utilization_ingestion_db_v2 import (
    ingest_utilization_from_csv_db,
)


def main() -> None:
    project_root = pathlib.Path(__file__).resolve().parents[2]
    csv_path = project_root / "templates" / "utilization_template_v2.csv"

    print(f"Using CSV: {csv_path}")

    if not csv_path.exists():
        print(f"ERROR: CSV file not found at {csv_path}")
        return

    with csv_path.open("r", encoding="utf-8") as f:
        result, rows_inserted = ingest_utilization_from_csv_db(
            run_id="run-utilization-v2-dbtest-001",
            file_like=f,
        )

    print("\n--- Utilization Ingestion v2 (Validation) ---")
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

    print("\n--- DB Write ---")
    print(f"Inserted rows into inventory_utilization_v2: {rows_inserted}")


if __name__ == "__main__":
    main()
