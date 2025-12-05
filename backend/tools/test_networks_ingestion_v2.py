import sys
from pathlib import Path

from app.modules.ingestion_core.networks_ingestion_v2 import (
    ingest_networks_from_csv,
)


def main() -> None:
    base_dir = Path(__file__).resolve().parent.parent  # .../backend
    csv_path = base_dir.parent / "templates" / "networks_template_v2.csv"

    print(f"Testing networks ingestion v2 with: {csv_path}")
    if not csv_path.exists():
        print(f"ERROR: CSV file not found at {csv_path}")
        sys.exit(1)

    result = ingest_networks_from_csv(
        run_id="run-networks-v2-cli-test-001",
        file_path=str(csv_path),
    )

    print("\n--- Networks Ingestion v2 Result ---")
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
            f"  - subnet_id={rec.subnet_id}, cidr={rec.subnet_cidr}, "
            f"env={rec.environment}, vlan={rec.vlan_id}, public={rec.is_public}, dmz={rec.is_dmz}"
        )


if __name__ == "__main__":
    main()
