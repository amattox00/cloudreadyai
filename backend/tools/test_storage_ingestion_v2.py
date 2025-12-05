from pathlib import Path

from app.modules.ingestion_core.storage_ingestion_v2 import (
    ingest_storage_from_csv,
)


def main() -> None:
    # Resolve: cloudreadyai/templates/storage_template_v2.csv
    csv_path = (
        Path(__file__)
        .resolve()
        .parent  # tools/
        .parent  # backend/
        .parent  # cloudreadyai/
        / "templates"
        / "storage_template_v2.csv"
    )

    print(f"Testing storage ingestion v2 with: {csv_path}")

    if not csv_path.exists():
        print(f"ERROR: CSV file not found at {csv_path}")
        return

    # Open the CSV and pass a file-like object to ingest_storage_from_csv
    with csv_path.open("r", encoding="utf-8") as f:
        result = ingest_storage_from_csv(
            run_id="run-storage-v2-cli-test-001",
            file_like=f,
        )

    print("\n--- Storage Ingestion v2 Result ---")
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

    print("\nFirst few records:")
    for rec in result.records[:5]:
        print(
            f"  - volume_id={rec.volume_id}, "
            f"host={rec.hostname}, "
            f"env={rec.environment}, "
            f"capacity_gb={rec.capacity_gb}, "
            f"used_gb={rec.used_gb}, "
            f"array={rec.storage_array}"
        )


if __name__ == "__main__":
    main()
