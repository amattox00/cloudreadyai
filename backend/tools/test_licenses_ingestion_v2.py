from pathlib import Path

from app.modules.ingestion_core.licenses_ingestion_v2 import ingest_licenses_from_csv


def main() -> None:
    base_dir = Path(__file__).resolve().parents[1]  # .../cloudreadyai/backend
    csv_path = base_dir.parent / "templates" / "licenses_template_v2.csv"

    print(f"Testing licenses ingestion v2 with: {csv_path}")

    if not csv_path.exists():
        print(f"ERROR: CSV file not found at {csv_path}")
        return

    with csv_path.open("r", encoding="utf-8") as f:
        result, rows = ingest_licenses_from_csv(
            run_id="run-licenses-v2-cli-test-001",
            file_like=f,
        )

    print("\n--- Licenses Ingestion v2 Result ---")
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

    print("\nFirst few parsed records:")
    for row in rows[:5]:
        print(
            f"  - host={row.hostname}, product={row.product_name}, vendor={row.vendor}, "
            f"metric={row.metric}, env={row.environment}, cores={row.cores_licensed}, "
            f"users={row.users_licensed}, cost_per_year={row.cost_per_year}"
        )


if __name__ == "__main__":
    main()
