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

    This is aligned with:
      * Your sample CSV headers
      * The inventory_storage_v2 table schema

    Expected CSV columns (extra columns are ignored):
      - volume_id            (required)
      - hostname             (optional)
      - environment          (optional)
      - storage_type         (optional)
      - capacity_gb / size_gb  (numeric, optional)
      - used_gb              (numeric, optional)
      - iops                 (numeric, optional)
      - throughput_mbps      (numeric, optional – not used yet)
    """

    volume_id: str
    hostname: Optional[str] = None
    environment: Optional[str] = None
    storage_type: Optional[str] = None
    capacity_gb: Optional[float] = None
    used_gb: Optional[float] = None
    iops: Optional[int] = None
    throughput_mbps: Optional[float] = None

    @field_validator("volume_id")
    @classmethod
    def volume_id_not_empty(cls, v: str) -> str:
        v = (v or "").strip()
        if not v:
            raise ValueError("volume_id is required")
        return v

    @field_validator("hostname", "environment", "storage_type", mode="before")
    @classmethod
    def normalize_optional_str(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        s = str(v).strip()
        return s or None

    @field_validator("capacity_gb", "used_gb", "throughput_mbps", mode="before")
    @classmethod
    def parse_float(cls, v):
        if v is None:
            return None
        s = str(v).strip()
        if s == "" or s == "-":
            return None
        try:
            return float(s)
        except ValueError:
            raise ValueError(f"Invalid float value: {s!r}")

    @field_validator("iops", mode="before")
    @classmethod
    def parse_int(cls, v):
        if v is None:
            return None
        s = str(v).strip()
        if s == "" or s == "-":
            return None
        try:
            return int(s)
        except ValueError:
            raise ValueError(f"Invalid int value: {s!r}")


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
    Reads a storage CSV at csv_path and returns StorageIngestionSummary.

    - Uses DictReader to read the header row.
    - Maps relevant columns into StorageRow.
    - If persist_row is provided, it will be called for each valid row.
    """

    summary = StorageIngestionSummary()

    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)

        for idx, raw in enumerate(reader, start=2):  # header is line 1
            # Skip completely blank rows
            if not any((v or "").strip() for v in raw.values()):
                continue

            summary.rows_processed += 1

            try:
                row = StorageRow(
                    volume_id=raw.get("volume_id"),
                    hostname=raw.get("hostname") or raw.get("server_hostname"),
                    environment=raw.get("environment"),
                    storage_type=raw.get("storage_type"),
                    # Accept either capacity_gb or size_gb as the source
                    capacity_gb=raw.get("capacity_gb") or raw.get("size_gb"),
                    used_gb=raw.get("used_gb"),
                    iops=raw.get("iops"),
                    throughput_mbps=raw.get("throughput_mbps"),
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
