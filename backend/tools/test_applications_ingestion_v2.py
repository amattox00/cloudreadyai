"""
CLI test for Applications v2 ingestion:

- Reads templates/applications_template_v2.csv
- Validates all rows
- Prints a summary + first few records
"""

from pathlib import Path

from app.modules.ingestion_core.applications_ingestion_v2 import (
    ingest_applications_from_csv,
)


def main() -> None:
    # ../templates/applications_template_v2.csv from this file
    csv_path = (
        Path(__file__)
        .resolve()
        .parent  # tools/
        .parent  # backend/
        .parent  # cloudreadyai/
        / "templates"
        / "applications_template_v2.csv"
    )

    print(f"Testing applications ingestion v2 with: {csv_path}")

    if not csv_path.exists():
        print(f"ERROR: CSV file not found at {csv_path}")
        return

    with csv_path.open("r", encoding="utf-8") as f:
        result = ingest_applications_from_csv(
            run_id="run-apps-v2-cli-test-001",
            file_like=f,
        )

    print("\n--- Applications Ingestion v2 Result ---")
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

    print("\nFirst few parsed records:")
    for app in result.records[:5]:
        print(
            f"  - app={app.app_name}, env={app.environment}, "
            f"owner={app.owner}, tier={app.tier}, bu={app.business_unit}"
        )


if __name__ == "__main__":
    main()
