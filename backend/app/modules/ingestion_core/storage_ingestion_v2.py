from __future__ import annotations

import csv
from dataclasses import dataclass
from typing import IO, List, Optional

from pydantic import BaseModel, ValidationError, field_validator


class StorageRow(BaseModel):
    """
    Validated representation of a single storage volume row from CSV.
    Adjust / extend fields as needed later.
    """

    volume_id: str
    datastore: Optional[str] = None
    storage_array: Optional[str] = None
    hostname: Optional[str] = None
    environment: Optional[str] = None
    protocol: Optional[str] = None
    tier: Optional[str] = None
    raid_type: Optional[str] = None
    capacity_gb: float
    used_gb: float
    provisioned_gb: Optional[float] = None
    iops: Optional[float] = None
    latency_ms: Optional[float] = None
    storage_type: Optional[str] = None
    is_replicated: Optional[bool] = None
    notes: Optional[str] = None

    @field_validator("volume_id")
    @classmethod
    def require_volume_id(cls, v: str) -> str:
        if v is None or str(v).strip() == "":
            raise ValueError("volume_id is required")
        return str(v).strip()

    @field_validator("capacity_gb", "used_gb", "provisioned_gb", "iops", "latency_ms", mode="before")
    @classmethod
    def parse_float(cls, v):
        if v is None:
            return None
        s = str(v).strip()
        if s == "" or s == "-":
            return None
        return float(s)

    @field_validator("is_replicated", mode="before")
    @classmethod
    def parse_bool(cls, v):
        if v is None:
            return None
        s = str(v).strip().lower()
        if s in ("true", "t", "yes", "y", "1"):
            return True
        if s in ("false", "f", "no", "n", "0"):
            return False
        # treat weird values as None instead of hard error
        return None


@dataclass
class StorageIngestionResult:
    run_id: str
    rows_processed: int
    rows_successful: int
    rows_failed: int
    errors: List[str]
    records: List[StorageRow]


def ingest_storage_from_csv(
    run_id: str,
    file_like: IO[str],
) -> StorageIngestionResult:
    """
    Core CSV ingestion for storage v2.

    - Reads CSV with a header row.
    - Tries to validate each row into StorageRow.
    - Returns a summary + list of validated storage records.
    - Does NOT write to the database; that is handled by a separate DB helper.
    """

    reader = csv.DictReader(file_like)
    processed = 0
    ok = 0
    failed = 0
    errors: List[str] = []
    records: List[StorageRow] = []

    for idx, row in enumerate(reader, start=2):  # header is row 1, data starts at 2
        # Skip completely empty lines
        if not any(str(v).strip() for v in row.values() if v is not None):
            continue

        processed += 1
        try:
            storage_row = StorageRow(
                volume_id=row.get("volume_id"),
                datastore=row.get("datastore"),
                storage_array=row.get("storage_array"),
                hostname=row.get("hostname"),
                environment=row.get("environment"),
                protocol=row.get("protocol"),
                tier=row.get("tier"),
                raid_type=row.get("raid_type"),
                capacity_gb=row.get("capacity_gb"),
                used_gb=row.get("used_gb"),
                provisioned_gb=row.get("provisioned_gb"),
                iops=row.get("iops"),
                latency_ms=row.get("latency_ms"),
                storage_type=row.get("storage_type"),
                is_replicated=row.get("is_replicated"),
                notes=row.get("notes"),
            )
            records.append(storage_row)
            ok += 1
        except ValidationError as e:
            failed += 1
            errors.append(f"Row {idx}: validation error: {e}")

    return StorageIngestionResult(
        run_id=run_id,
        rows_processed=processed,
        rows_successful=ok,
        rows_failed=failed,
        errors=errors,
        records=records,
    )
