from __future__ import annotations

import csv
from dataclasses import dataclass, field
from typing import Callable, List, Optional

from pydantic import BaseModel, ValidationError, field_validator

from app.modules.ingestion.normalization.servers_normalizer import (
    normalize_server_record,
)


class ServerRow(BaseModel):
    """
    Normalized representation of one server row from the CSV.
    This is the only place we parse/filter raw CSV -> typed Python.
    """

    hostname: str
    environment: Optional[str] = None
    os: Optional[str] = None
    role: Optional[str] = None
    cpu_cores: Optional[int] = None
    memory_gb: Optional[float] = None

    @field_validator("hostname")
    @classmethod
    def hostname_not_empty(cls, v: str) -> str:
        v = (v or "").strip()
        if not v:
            raise ValueError("hostname is required")
        return v

    @field_validator("environment", "os", "role", mode="before")
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
                # allow either memory_gb or ram_gb in the CSV
                mem_raw = (raw.get("memory_gb") or raw.get("ram_gb") or "").strip()

                # First pass: basic CSV → typed ServerRow
                row = ServerRow(
                    hostname=(raw.get("hostname") or "").strip(),
                    environment=(raw.get("environment") or "").strip() or None,
                    os=(raw.get("os") or "").strip() or None,
                    role=(raw.get("role") or "").strip() or None,
                    cpu_cores=int(cpu_raw) if cpu_raw else None,
                    memory_gb=float(mem_raw) if mem_raw else None,
                )

                # Second pass: use shared normalizer for env/OS/role consistency.
                # Convert the typed row → dict, normalize, then rebuild ServerRow.
                raw_record = row.model_dump()

                normalized_record, warnings = normalize_server_record(raw_record)

                # Prefer normalized environment if provided; otherwise keep original
                normalized_env = normalized_record.get("environment") or row.environment

                # Prefer canonical OS name if provided; otherwise keep original
                normalized_os = (
                    normalized_record.get("os_name")
                    or normalized_record.get("os")
                    or row.os
                )

                # Prefer normalized role if provided; otherwise keep original
                normalized_role = normalized_record.get("role") or row.role

                row = ServerRow(
                    hostname=row.hostname,
                    environment=normalized_env,
                    os=normalized_os,
                    role=normalized_role,
                    cpu_cores=row.cpu_cores,
                    memory_gb=row.memory_gb,
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
                f"role={row.role or '-'}, "
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
