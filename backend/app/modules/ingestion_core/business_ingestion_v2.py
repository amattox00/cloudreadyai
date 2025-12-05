from __future__ import annotations

import csv
from typing import List, Optional, TextIO

from pydantic import BaseModel, Field, ValidationError, field_validator


class BusinessRow(BaseModel):
    """
    Represents a single business metadata record from the CSV.
    """

    business_service: str = Field(..., description="Business service or capability name")
    app_name: Optional[str] = Field(
        None, description="Logical application name this service maps to"
    )
    environment: Optional[str] = Field(
        None, description="Environment (prod/dev/qa/stage/etc.)"
    )

    business_unit: Optional[str] = None
    business_owner: Optional[str] = None
    executive_owner: Optional[str] = None

    criticality: Optional[str] = Field(
        None,
        description="Business criticality (critical/high/medium/low)",
    )

    rto_hours: Optional[float] = Field(
        None, description="Recovery Time Objective in hours"
    )
    rpo_hours: Optional[float] = Field(
        None, description="Recovery Point Objective in hours"
    )

    revenue_impact_per_hour: Optional[float] = Field(
        None,
        description="Estimated revenue impact per hour of outage",
    )
    customer_impact: Optional[str] = Field(
        None,
        description="internal / external / both, etc.",
    )

    compliance_tags: Optional[str] = Field(
        None,
        description="Comma/semicolon-separated compliance markers (PCI, SOX, HIPAA, etc.)",
    )
    notes: Optional[str] = None
    tags: Optional[str] = None

    @field_validator("business_service")
    @classmethod
    def business_service_required(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("business_service is required")
        return v.strip()

    @field_validator("rto_hours", "rpo_hours", "revenue_impact_per_hour", mode="before")
    @classmethod
    def parse_optional_float(cls, v):
        if v is None:
            return None
        if isinstance(v, (int, float)):
            return float(v)
        s = str(v).strip()
        if s == "":
            return None
        try:
            return float(s)
        except ValueError:
            raise ValueError(f"Cannot parse float from value: {v!r}")


class BusinessIngestionResult(BaseModel):
    run_id: str
    rows_processed: int
    rows_successful: int
    rows_failed: int
    errors: List[str]
    records: List[BusinessRow]


def ingest_business_from_csv(
    run_id: str,
    file_like: Optional[TextIO] = None,
    file_path: Optional[str] = None,
) -> BusinessIngestionResult:
    """
    Core CSV → validated BusinessRow list.

    You can pass either:
      - file_like: in-memory text stream (API upload)
      - file_path: filesystem path (CLI tests)
    """
    if file_like is None and not file_path:
        raise ValueError("Either file_like or file_path must be provided")

    close_after = False
    if file_like is not None:
        f = file_like
    else:
        f = open(file_path, "r", encoding="utf-8-sig", newline="")
        close_after = True

    try:
        reader = csv.DictReader(f)
        rows_processed = 0
        rows_successful = 0
        rows_failed = 0
        errors: List[str] = []
        records: List[BusinessRow] = []

        for idx, row in enumerate(reader, start=2):
            rows_processed += 1
            try:
                rec = BusinessRow(**row)
                records.append(rec)
                rows_successful += 1
            except ValidationError as exc:
                rows_failed += 1
                errors.append(f"Row {idx}: validation error: {exc}")

        return BusinessIngestionResult(
            run_id=run_id,
            rows_processed=rows_processed,
            rows_successful=rows_successful,
            rows_failed=rows_failed,
            errors=errors,
            records=records,
        )
    finally:
        if close_after:
            f.close()
