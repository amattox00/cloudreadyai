from pathlib import Path

from app.modules.ingestion_core.business_ingestion_v2 import ingest_business_from_csv


def main() -> None:
    base_dir = Path(__file__).resolve().parent.parent  # .../backend
    csv_path = base_dir.parent / "templates" / "business_template_v2.csv"

    print(f"Testing business metadata ingestion v2 with: {csv_path}")
    if not csv_path.exists():
        print(f"ERROR: CSV file not found at {csv_path}")
        raise SystemExit(1)

    result = ingest_business_from_csv(
        run_id="run-business-v2-cli-test-001",
        file_path=str(csv_path),
    )

    print("\n--- Business Ingestion v2 Result ---")
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
            f"  - service={rec.business_service}, app={rec.app_name}, "
            f"env={rec.environment}, bu={rec.business_unit}, "
            f"criticality={rec.criticality}, rto={rec.rto_hours}, rpo={rec.rpo_hours}"
        )


if __name__ == "__main__":
    main()
