from __future__ import annotations

import csv
from dataclasses import dataclass, field
from typing import Callable, List, Optional

from pydantic import BaseModel, ValidationError, field_validator


class ServerRow(BaseModel):
    """
    Normalized representation of one server row from the CSV.
    This is the only place we parse/filter raw CSV -> typed Python.
    """

    hostname: str
    environment: Optional[str] = None
    os: Optional[str] = None
    cpu_cores: Optional[int] = None
    memory_gb: Optional[float] = None

    @field_validator("hostname")
    @classmethod
    def hostname_not_empty(cls, v: str) -> str:
        v = (v or "").strip()
        if not v:
            raise ValueError("hostname is required")
        return v

    @field_validator("environment", "os", mode="before")
    @classmethod
    def normalize_optional_str(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = str(v).strip()
        return v or None


@dataclass
class ServersIngestionSummary:
    """
    High-level summary for a servers CSV ingestion run.
    This is what both test scripts and the FastAPI endpoint will return.
    """

    rows_processed: int = 0
    rows_successful: int = 0
    rows_failed: int = 0
    errors: List[str] = field(default_factory=list)


def ingest_servers_from_csv(
    csv_path: str,
    persist_row: Optional[Callable[[ServerRow], None]] = None,
) -> ServersIngestionSummary:
    """
    Core ingestion loop:

    * Reads a CSV file.
    * Validates/normalizes rows into ServerRow.
    * Optionally calls persist_row(row) for DB writes, etc.
    * Returns a ServersIngestionSummary.

    This function is deliberately pure/boring so it can be safely used by:
      - tools/test_server_ingestion.py
      - tools/test_server_ingestion_db_v2.py
      - app.routers.ingestion_servers_v2
    """

    summary = ServersIngestionSummary()

    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)

        # Start at 2 because row 1 is the CSV header (nicer error messages)
        for idx, raw in enumerate(reader, start=2):
            summary.rows_processed += 1

            try:
                # Defensive parsing: missing / empty values become None
                cpu_raw = (raw.get("cpu_cores") or "").strip()
                mem_raw = (raw.get("memory_gb") or "").strip()

                row = ServerRow(
                    hostname=(raw.get("hostname") or "").strip(),
                    environment=(raw.get("environment") or "").strip() or None,
                    os=(raw.get("os") or "").strip() or None,
                    cpu_cores=int(cpu_raw) if cpu_raw else None,
                    memory_gb=float(mem_raw) if mem_raw else None,
                )
            except (ValidationError, ValueError) as e:
                summary.rows_failed += 1
                summary.errors.append(
                    f"Row {idx}: validation error: {e}"
                )
                continue

            # Helpful log for CLI test scripts
            print(
                f"Ingesting server: {row.hostname} "
                f"(env={row.environment or '-'}, "
                f"os={row.os or '-'}, "
                f"cpu={row.cpu_cores or '-'}, "
                f"mem={row.memory_gb or '-'} GB)"
            )

            if persist_row:
                try:
                    persist_row(row)
                except Exception as e:
                    summary.rows_failed += 1
                    summary.errors.append(
                        f"Row {idx}: persist error: {repr(e)}"
                    )
                    continue

            summary.rows_successful += 1

    return summary
