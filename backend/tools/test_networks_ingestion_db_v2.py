from pathlib import Path

from app.modules.ingestion_core.networks_ingestion_v2 import (
    ingest_networks_from_csv,
)
from app.modules.ingestion_core.networks_ingestion_db_v2 import (
    persist_network_records_v2,
)


def main() -> None:
    base_dir = Path(__file__).resolve().parent.parent  # .../backend
    csv_path = base_dir.parent / "templates" / "networks_template_v2.csv"

    print(f"Using CSV: {csv_path}")

    result = ingest_networks_from_csv(
        run_id="run-networks-v2-dbtest-001",
        file_path=str(csv_path),
    )

    print("\n--- Networks Ingestion v2 (Validation) ---")
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
    rows_inserted = persist_network_records_v2(
        run_id=result.run_id,
        records=result.records,
    )
    print(f"Inserted rows into inventory_networks_v2: {rows_inserted}")


if __name__ == "__main__":
    main()
