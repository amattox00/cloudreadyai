from pathlib import Path

from app.modules.ingestion_core.server_ingestion_core import (
    ingest_servers_from_csv,
    ServerRow,
)


def persist_row_to_console(row: ServerRow) -> None:
    print(
        f"Ingesting server: {row.hostname} "
        f"(env={row.environment}, os={row.os}, cpu={row.cpu_cores}, mem={row.memory_gb} GB)"
    )


def main() -> None:
    csv_path = Path("sample_data/servers_sample.csv")
    if not csv_path.exists():
        raise SystemExit(f"CSV file not found: {csv_path}")

    with csv_path.open("r", encoding="utf-8") as f:
        result = ingest_servers_from_csv(
            file_like=f,
            persist_row=persist_row_to_console,
        )

    print("\n--- Ingestion finished ---")
    print("Rows processed :", result.rows_processed)
    print("Rows successful:", result.rows_successful)
    print("Rows failed    :", result.rows_failed)
    print("Errors:")
    for err in result.errors:
        print("  -", err)


if __name__ == "__main__":
    main()
