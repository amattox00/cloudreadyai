"""
CLI test for Dependencies ingestion v2.

Reads ../templates/dependencies_template_v2.csv, runs validation,
and prints a summary plus a few sample records.

This does NOT write to the DB yet – it's just the core ingestion slice.
"""

from pathlib import Path

from app.modules.ingestion_core.dependencies_ingestion_v2 import (
    ingest_dependencies_from_csv,
)


def main() -> None:
    run_id = "run-deps-v2-cli-test-001"

    csv_path = (
        Path(__file__)
        .resolve()
        .parent  # tools/
        .parent  # backend/
        .parent  # cloudreadyai/
        / "templates"
        / "dependencies_template_v2.csv"
    )

    print(f"Testing dependencies ingestion v2 with: {csv_path}")
    if not csv_path.exists():
        print(f"ERROR: CSV file not found at {csv_path}")
        return

    with csv_path.open("r", encoding="utf-8") as f:
        result = ingest_dependencies_from_csv(run_id=run_id, file_like=f)

    print("\n--- Dependencies Ingestion v2 Result ---")
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
        print("\nNo valid dependency records parsed.")
        return

    print("\nFirst few parsed records:")
    for dep in result.records[:5]:
        print(
            f"  - app={dep.app_name}, env={dep.environment}, "
            f"type={dep.dependency_type}, server={dep.server_hostname}, "
            f"db={dep.database_name}, engine={dep.database_engine}"
        )


if __name__ == "__main__":
    main()
