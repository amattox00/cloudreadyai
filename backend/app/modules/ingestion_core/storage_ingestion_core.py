from __future__ import annotations

import csv
from dataclasses import dataclass, field
from typing import Callable, List, Optional

from pydantic import BaseModel, ValidationError, field_validator


# -------------------------------
# Storage Row Definition
# -------------------------------
class StorageRow(BaseModel):
    """
    Normalized representation of one storage row from the CSV.
    """

    volume_id: str
    server_hostname: Optional[str] = None
    size_gb: Optional[float] = None
    storage_type: Optional[str] = None
    iops: Optional[int] = None
    throughput_mbps: Optional[int] = None

    @field_validator("volume_id")
    @classmethod
    def volume_id_not_empty(cls, v: str) -> str:
        v = (v or "").strip()
        if not v:
            raise ValueError("volume_id is required")
        return v

    @field_validator(
        "server_hostname",
        "storage_type",
        mode="before",
    )
    @classmethod
    def normalize_optional_str(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = str(v).strip()
        return v or None


# -------------------------------
# Summary Report
# -------------------------------
@dataclass
class StorageIngestionSummary:
    rows_processed: int = 0
    rows_successful: int = 0
    rows_failed: int = 0
    errors: List[str] = field(default_factory=list)


# -------------------------------
# Core Ingestion Loop
# -------------------------------
def ingest_storage_from_csv(
    csv_path: str,
    persist_row: Optional[Callable[[StorageRow], None]] = None,
) -> StorageIngestionSummary:
    """
    Reads storage CSV + returns StorageIngestionSummary.
    Optional: persist_row(row) writes to DB.
    """
    summary = StorageIngestionSummary()

    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)

        for idx, raw in enumerate(reader, start=2):
            summary.rows_processed += 1

            try:
                row = StorageRow(
                    volume_id=(raw.get("volume_id") or "").strip(),
                    server_hostname=(raw.get("server_hostname") or "").strip() or None,
                    size_gb=float(raw.get("size_gb") or 0) if raw.get("size_gb") else None,
                    storage_type=(raw.get("storage_type") or "").strip() or None,
                    iops=int(raw.get("iops") or 0) if raw.get("iops") else None,
                    throughput_mbps=int(raw.get("throughput_mbps") or 0)
                    if raw.get("throughput_mbps")
                    else None,
                )

            except (ValidationError, ValueError) as e:
                summary.rows_failed += 1
                summary.errors.append(f"Row {idx}: validation error: {e}")
                continue

            if persist_row:
                try:
                    persist_row(row)
                except Exception as e:
                    summary.rows_failed += 1
                    summary.errors.append(f"Row {idx}: persist error: {repr(e)}")
                    continue

            summary.rows_successful += 1

    return summary
