from __future__ import annotations

from sqlalchemy.orm import Session
from sqlalchemy import text

from app.modules.ingestion_core.server_ingestion_core import (
    ingest_servers_from_csv,
    ServersIngestionSummary,
    ServerRow,
)


def ingest_servers_v2_from_csv_to_db(
    csv_path: str,
    db: Session,
    run_id: str,
) -> ServersIngestionSummary:
    """
    Read a servers CSV file and persist rows into inventory_servers_v2.

    This version does NOT rely on a SQLAlchemy ORM model for InventoryServersV2.
    Instead, it uses a direct INSERT into the inventory_servers_v2 table,
    matching the actual Postgres schema:

        id            | integer           | PK (serial)
        run_id        | character varying | not null
        hostname      | character varying | not null
        role          | character varying
        os            | character varying
        environment   | character varying
        cpu_usage     | double precision
        ram_usage     | double precision
        storage_usage | double precision
    """

    def persist_row(row: ServerRow) -> None:
        # Insert one row into inventory_servers_v2 using normalized fields.
        stmt = text(
            """
            INSERT INTO inventory_servers_v2
                (run_id, hostname, role, os, environment, cpu_usage, ram_usage, storage_usage)
            VALUES
                (:run_id, :hostname, :role, :os, :environment, :cpu_usage, :ram_usage, :storage_usage)
            """
        )

        db.execute(
            stmt,
            {
                "run_id": run_id,
                "hostname": row.hostname,
                "role": row.role,
                "os": row.os,
                "environment": row.environment,
                # Usage metrics are populated by the utilization slice, not here.
                "cpu_usage": None,
                "ram_usage": None,
                "storage_usage": None,
            },
        )

    summary: ServersIngestionSummary = ingest_servers_from_csv(
        csv_path=csv_path,
        persist_row=persist_row,
    )
    db.commit()
    return summary
