from __future__ import annotations

import csv
from typing import List, Optional, TextIO

from pydantic import BaseModel, Field, ValidationError, field_validator


class OSSoftwareRow(BaseModel):
    """
    Represents a single host OS / software record from the CSV.
    """

    hostname: str = Field(..., description="Hostname of the server/VM")
    environment: Optional[str] = Field(None, description="Environment (prod/dev/qa/stage/etc.)")

    os_name: str = Field(..., description="OS family/name, e.g. Windows Server, RHEL, Ubuntu")
    os_version: Optional[str] = None
    os_release: Optional[str] = None
    kernel_version: Optional[str] = None

    patch_level: Optional[str] = Field(
        None,
        description="Patch level string, e.g. 2024-10 or KB bundle",
    )

    middleware_stack: Optional[str] = Field(
        None,
        description="Key middleware: IIS; .NET; nginx; Tomcat, etc.",
    )
    java_version: Optional[str] = None
    dotnet_version: Optional[str] = None
    web_server: Optional[str] = None
    db_client: Optional[str] = None

    installed_software: Optional[str] = Field(
        None,
        description="Freeform: major agents, monitoring, AV, etc.",
    )
    notes: Optional[str] = None
    tags: Optional[str] = None

    @field_validator("hostname")
    @classmethod
    def hostname_required(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("hostname is required")
        return v.strip()

    @field_validator("os_name")
    @classmethod
    def os_name_required(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("os_name is required")
        return v.strip()


class OSSoftwareIngestionResult(BaseModel):
    run_id: str
    rows_processed: int
    rows_successful: int
    rows_failed: int
    errors: List[str]
    records: List[OSSoftwareRow]


def ingest_os_software_from_csv(
    run_id: str,
    file_like: Optional[TextIO] = None,
    file_path: Optional[str] = None,
) -> OSSoftwareIngestionResult:
    """
    Core CSV → validated OSSoftwareRow list.

    You can pass either:
      - file_like: an in-memory text stream (from API upload)
      - file_path: a path on disk (for CLI tests)
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
        records: List[OSSoftwareRow] = []

        for idx, row in enumerate(reader, start=2):  # data begins at line 2
            rows_processed += 1
            try:
                record = OSSoftwareRow(**row)
                records.append(record)
                rows_successful += 1
            except ValidationError as exc:
                rows_failed += 1
                errors.append(f"Row {idx}: validation error: {exc}")

        return OSSoftwareIngestionResult(
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
