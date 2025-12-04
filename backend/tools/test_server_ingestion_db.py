from pathlib import Path

from app.modules.ingestion_core.server_ingestion_core import ingest_servers_from_csv
from app.modules.ingestion_core.server_ingestion_core import ServerRow
from app.modules.ingestion_core.server_ingestion_db import persist_row_to_db
from app.db import get_db
from app.models.ingestion_runs import IngestionRun

# We will reuse your existing DB dependency to get a Session.
# If this path is slightly different in your project, adjust the import.
def ensure_test_run(db, run_id: str) -> None:
    """
    Make sure there's an ingestion_runs row for this run_id,
    so the servers FK constraint is satisfied.
    """
    run = db.query(IngestionRun).filter(IngestionRun.run_id == run_id).one_or_none()
    if run is not None:
        return

    # Minimal row; tweak fields if your model requires more
    run = IngestionRun(
        run_id=run_id,
        status="NEW",  # change if your status field is different
        # name or other fields can go here if required by your model
    )
    db.add(run)
    db.commit()


def main() -> None:
    csv_path = Path("sample_data/servers_sample.csv")
    run_id = "run-servers-db-test-001"

    if not csv_path.exists():
        raise SystemExit(f"CSV file not found: {csv_path}")

    db_gen = get_db()
    db = next(db_gen)

    try:
        # Ensure parent ingestion_runs row exists
        ensure_test_run(db, run_id)

        with csv_path.open("r", encoding="utf-8") as f:
            result = ingest_servers_from_csv(
                file_like=f,
                persist_row=lambda row: persist_row_to_db(
                    row=row,
                    db=db,
                    run_id=run_id,
                ),
            )

        db.commit()

        print("\n--- DB-backed ingestion finished ---")
        print("Run ID        :", run_id)
        print("Rows processed:", result.rows_processed)
        print("Rows successful:", result.rows_successful)
        print("Rows failed   :", result.rows_failed)
        print("Errors:")
        for err in result.errors:
            print("  -", err)

    finally:
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
