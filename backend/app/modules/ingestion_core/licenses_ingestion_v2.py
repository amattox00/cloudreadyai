from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, TextIO, Optional
import csv

from pydantic import BaseModel, Field, ValidationError


class LicenseRow(BaseModel):
    hostname: Optional[str] = Field(default=None)
    product_name: str
    vendor: Optional[str] = None
    license_type: Optional[str] = None  # OS, DB, App, Backup, etc.
    metric: Optional[str] = None        # per-core, per-user, per-host, etc.
    environment: Optional[str] = None

    cores_licensed: Optional[float] = None
    users_licensed: Optional[float] = None

    expiry_date: Optional[str] = None   # keep as string to avoid date parsing issues
    cost_per_year: Optional[float] = None
    maintenance_per_year: Optional[float] = None

    po_number: Optional[str] = None
    owner: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[str] = None


@dataclass
class LicenseIngestionResult:
    run_id: str
    rows_processed: int
    rows_successful: int
    rows_failed: int
    errors: List[str]


def _safe_float(value: str | None) -> Optional[float]:
    if value is None:
        return None
    v = value.strip()
    if v == "":
        return None
    try:
        return float(v)
    except ValueError:
        raise ValueError(f"could not convert '{value}' to float")


def ingest_licenses_from_csv(
    run_id: str,
    file_like: TextIO,
) -> Tuple[LicenseIngestionResult, List[LicenseRow]]:
    """
    Core CSV → LicenseRow validator for v2 licensing slice.

    Does NOT touch the database — just parses and validates rows.
    """
    reader = csv.DictReader(file_like)
    rows: List[LicenseRow] = []
    errors: List[str] = []

    rows_processed = 0
    rows_successful = 0
    rows_failed = 0

    for idx, raw in enumerate(reader, start=2):  # header is row 1
        # Skip completely empty lines
        if not any((raw or {}).values()):
            continue

        rows_processed += 1
        try:
            # Normalize numeric fields
            raw["cores_licensed"] = (
                None if raw.get("cores_licensed", "").strip() == "" else _safe_float(raw.get("cores_licensed"))
            )
            raw["users_licensed"] = (
                None if raw.get("users_licensed", "").strip() == "" else _safe_float(raw.get("users_licensed"))
            )
            raw["cost_per_year"] = (
                None if raw.get("cost_per_year", "").strip() == "" else _safe_float(raw.get("cost_per_year"))
            )
            raw["maintenance_per_year"] = (
                None
                if raw.get("maintenance_per_year", "").strip() == ""
                else _safe_float(raw.get("maintenance_per_year"))
            )

            row = LicenseRow(**raw)
            rows.append(row)
            rows_successful += 1
        except (ValidationError, ValueError) as exc:
            rows_failed += 1
            errors.append(f"Row {idx}: validation error: {exc}")

    result = LicenseIngestionResult(
        run_id=run_id,
        rows_processed=rows_processed,
        rows_successful=rows_successful,
        rows_failed=rows_failed,
        errors=errors,
    )
    return result, rows
