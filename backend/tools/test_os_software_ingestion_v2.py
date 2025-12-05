from pathlib import Path

from app.modules.ingestion_core.os_software_ingestion_v2 import (
    ingest_os_software_from_csv,
)


def main() -> None:
    base_dir = Path(__file__).resolve().parent.parent  # .../backend
    csv_path = base_dir.parent / "templates" / "os_software_template_v2.csv"

    print(f"Testing OS/Software ingestion v2 with: {csv_path}")
    if not csv_path.exists():
        print(f"ERROR: CSV file not found at {csv_path}")
        raise SystemExit(1)

    result = ingest_os_software_from_csv(
        run_id="run-ossoft-v2-cli-test-001",
        file_path=str(csv_path),
    )

    print("\n--- OS/Software Ingestion v2 Result ---")
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
            f"  - host={rec.hostname}, env={rec.environment}, "
            f"os={rec.os_name} {rec.os_version or ''}, patch={rec.patch_level}, "
            f"middleware={rec.middleware_stack}"
        )


if __name__ == "__main__":
    main()
