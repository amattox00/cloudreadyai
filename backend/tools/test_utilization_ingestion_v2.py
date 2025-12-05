import pathlib

from app.modules.ingestion_core.utilization_ingestion_v2 import (
    ingest_utilization_from_csv,
)


def main() -> None:
    # project_root should be .../cloudreadyai
    project_root = pathlib.Path(__file__).resolve().parents[2]
    csv_path = project_root / "templates" / "utilization_template_v2.csv"

    print(f"Testing utilization ingestion v2 with: {csv_path}")

    if not csv_path.exists():
        print(f"ERROR: CSV file not found at {csv_path}")
        return

    with csv_path.open("r", encoding="utf-8") as f:
        result, rows = ingest_utilization_from_csv(
            run_id="run-utilization-v2-cli-test-001",
            file_like=f,
        )

    print("\n--- Utilization Ingestion v2 Result ---")
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
    for row in rows[:5]:
        print(
            f"  - host={row.hostname}, env={row.environment}, "
            f"avg_cpu={row.avg_cpu_percent}, peak_cpu={row.peak_cpu_percent}, "
            f"avg_ram={row.avg_ram_percent}, peak_ram={row.peak_ram_percent}"
        )


if __name__ == "__main__":
    main()
