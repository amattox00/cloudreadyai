from __future__ import annotations

import csv
from typing import List, Optional, TextIO

from pydantic import BaseModel, Field, ValidationError


class ApplicationRow(BaseModel):
    """
    One row of applications CSV (v2).
    """

    app_name: str = Field(..., description="Application name")
    owner: Optional[str] = None
    business_unit: Optional[str] = None
    environment: str
    description: Optional[str] = None
    tier: Optional[str] = None
    sla_hours: Optional[float] = None
    criticality: Optional[str] = None
    depends_on_servers: Optional[str] = None
    depends_on_databases: Optional[str] = None
    tags: Optional[str] = None


class ApplicationsIngestionResult(BaseModel):
    """
    Result of ingesting an applications CSV.
    """

    run_id: str
    rows_processed: int
    rows_successful: int
    rows_failed: int
    errors: List[str]
    records: List[ApplicationRow]


def ingest_applications_from_csv(run_id: str, file_like: TextIO) -> ApplicationsIngestionResult:
    """
    Validate applications CSV rows for a given run_id.

    - Expects a text file-like object (already opened)
    - Skips bad rows but records their errors
    - Returns structured ApplicationRow records for DB insertion
    """
    reader = csv.DictReader(file_like)
    processed = 0
    success = 0
    failed = 0
    errors: List[str] = []
    records: List[ApplicationRow] = []

    # Start counting at 2 because line 1 is the header row
    for line_no, row in enumerate(reader, start=2):
        processed += 1
        try:
            app = ApplicationRow(**row)
            records.append(app)
            success += 1
        except ValidationError as exc:
            errors.append(f"Row {line_no}: validation error: {exc}")
            failed += 1

    return ApplicationsIngestionResult(
        run_id=run_id,
        rows_processed=processed,
        rows_successful=success,
        rows_failed=failed,
        errors=errors,
        records=records,
    )
