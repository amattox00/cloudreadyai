from pathlib import Path

from app.modules.ingestion_core.databases_ingestion_v2 import (
    ingest_databases_from_csv,
)


def main() -> None:
    run_id = "run-databases-v2-cli-test-001"

    csv_path = (
        Path(__file__)
        .resolve()
        .parent  # tools/
        .parent  # backend/
        .parent  # cloudreadyai/
        / "templates"
        / "databases_template_v2.csv"
    )

    print(f"Testing databases ingestion v2 with: {csv_path}")

    if not csv_path.exists():
        print(f"ERROR: CSV file not found at {csv_path}")
        return

    with csv_path.open("r", encoding="utf-8") as f:
        result = ingest_databases_from_csv(run_id=run_id, file_like=f)

    print("\n--- Databases Ingestion v2 Result ---")
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
            f"  - host={rec.hostname}, "
            f"db_name={rec.db_name}, "
            f"engine={rec.db_engine}, "
            f"env={rec.environment}, "
            f"cpu_cores={rec.cpu_cores}, "
            f"memory_gb={rec.memory_gb}, "
            f"storage_gb={rec.storage_gb}"
        )


if __name__ == "__main__":
    main()
