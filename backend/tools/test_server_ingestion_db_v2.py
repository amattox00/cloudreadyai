"""
tools/test_server_ingestion_db_v2.py

Offline test harness for the servers ingestion slice, targeting the
*v2* ingestion tables:

  - ingestion_runs_v2
  - inventory_server_v2

No FastAPI, no systemd, no routers. Just:

  CSV -> ServerRow (via core ingestion) -> v2 DB tables
"""

from __future__ import annotations

from pathlib import Path

from app.modules.ingestion_core.server_ingestion_core import (
    ingest_servers_from_csv,
)
from app.modules.ingestion_core.server_ingestion_db_v2 import (
    ensure_run_v2,
    persist_server_row_v2,
)
from app.db import get_db


def main() -> None:
    # You can change this run_id anytime; it's just for testing.
    run_id = "run-servers-v2-test-001"
    csv_path = Path("sample_data/servers_sample.csv")

    if not csv_path.exists():
        raise SystemExit(f"CSV file not found: {csv_path}")

    # Use the same DB session factory the main app uses
    db_gen = get_db()
    db = next(db_gen)

    try:
        # 1) Ensure we have a v2 ingestion run row
        ensure_run_v2(db, run_id)

        # 2) Run the core ingestion against the CSV, piping rows into v2 DB
        with csv_path.open("r", encoding="utf-8") as f:
            result = ingest_servers_from_csv(
                file_like=f,
                persist_row=lambda row: persist_server_row_v2(
                    db=db,
                    row=row,
                    run_id=run_id,
                ),
            )

        # 3) Commit all successful rows
        db.commit()

        # 4) Print a nice summary
        print("\n--- DB-backed v2 ingestion finished ---")
        print("Run ID        :", run_id)
        print("CSV file      :", csv_path)
        print("Rows processed:", result.rows_processed)
        print("Rows successful:", result.rows_successful)
        print("Rows failed   :", result.rows_failed)
        print("Errors:")
        if not result.errors:
            print("  (none)")
        else:
            for err in result.errors:
                print("  -", err)

    finally:
        # Cleanly close DB generator/session
        try:
            db.close()
        except Exception:
            pass

        try:
            db_gen.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
