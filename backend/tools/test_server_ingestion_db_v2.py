from __future__ import annotations

from pathlib import Path
import subprocess
import textwrap


def main() -> None:
    """
    Helper script for servers ingestion v2.

    Note:
    - In this branch, servers v2 ingestion is implemented via the FastAPI router
      (/v2/ingestion/servers/csv) instead of a shared ingestion_core module.
    - This script does NOT call Python ingestion functions directly. Instead it
      shows you exactly how to test the pipeline via curl + Postgres.
    """

    repo_root = Path(__file__).resolve().parents[1]
    csv_path = repo_root.parent / "templates" / "servers_sample1.csv"

    print(f"Servers v2 test helper")
    print(f"Using CSV: {csv_path}")
    print()

    curl_cmd = textwrap.dedent(
        f"""
        curl -X POST "http://localhost:8000/v2/ingestion/servers/csv?run_id=run-servers-v2-dbtest-001" \\
          -H "accept: application/json" \\
          -H "Content-Type: multipart/form-data" \\
          -F "file=@{csv_path};type=text/csv"
        """
    ).strip()

    print("--- 1) Run this curl command in another shell to ingest: ---")
    print(curl_cmd)
    print()

    print("--- 2) Then verify in Postgres with something like: ---")
    print(
        textwrap.dedent(
            """
            PGPASSWORD=cloudready psql -h 127.0.0.1 -p 5432 -U cloudready -d cloudready

            SELECT run_id,
                   hostname,
                   environment,
                   os,
                   cpu_usage,
                   ram_usage,
                   storage_usage
            FROM inventory_servers_v2
            WHERE run_id = 'run-servers-v2-dbtest-001'
            ORDER BY hostname;
            """
        ).rstrip()
    )
    print()

    # Exit cleanly so this script doesn't cause failures in automation
    print("Note: servers v2 ingestion core is wired via the API router in this branch.")
    print("This helper script is informational only and does not execute the ingestion directly.")


if __name__ == "__main__":
    main()
