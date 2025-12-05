from __future__ import annotations

import csv
from typing import List, Optional, TextIO, Union

from pydantic import BaseModel, Field, ValidationError, field_validator


class NetworkRow(BaseModel):
    """
    Represents a single network/subnet record from the CSV.
    """

    subnet_id: str = Field(..., description="Logical ID for the subnet (e.g. subnet-app-prod-01)")
    subnet_cidr: str = Field(..., description="CIDR block, e.g. 10.10.1.0/24")

    vlan_id: Optional[str] = Field(None, description="VLAN ID, can be numeric or string")
    environment: Optional[str] = None
    datacenter: Optional[str] = None
    zone: Optional[str] = None
    network_name: Optional[str] = None
    purpose: Optional[str] = None

    is_public: Optional[bool] = None
    is_dmz: Optional[bool] = None

    connected_to: Optional[str] = Field(
        None,
        description="Semi-colon separated list of connected devices/nets (e.g. core-router-01;fw-01)",
    )
    tags: Optional[str] = None

    @field_validator("subnet_id")
    @classmethod
    def subnet_id_required(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("subnet_id is required")
        return v.strip()

    @field_validator("subnet_cidr")
    @classmethod
    def cidr_required(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("subnet_cidr is required")
        return v.strip()

    @field_validator("is_public", "is_dmz", mode="before")
    @classmethod
    def parse_bool(cls, v):
        if v is None or v == "":
            return None
        if isinstance(v, bool):
            return v
        s = str(v).strip().lower()
        if s in {"1", "true", "yes", "y"}:
            return True
        if s in {"0", "false", "no", "n"}:
            return False
        # if weird, leave as None so we don't blow up
        return None


class NetworkIngestionResult(BaseModel):
    run_id: str
    rows_processed: int
    rows_successful: int
    rows_failed: int
    errors: List[str]
    records: List[NetworkRow]


def ingest_networks_from_csv(
    run_id: str,
    file_like: Optional[TextIO] = None,
    file_path: Optional[str] = None,
) -> NetworkIngestionResult:
    """
    Core CSV → validated NetworkRow list.

    You can pass either:
      - file_like: an in-memory text stream (from API upload)
      - file_path: a path on disk (for CLI tests)
    """
    if file_like is None and not file_path:
        raise ValueError("Either file_like or file_path must be provided")

    close_after = False
    f: TextIO

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
        records: List[NetworkRow] = []

        for idx, row in enumerate(reader, start=2):  # data starts on line 2
            rows_processed += 1
            try:
                record = NetworkRow(**row)
                records.append(record)
                rows_successful += 1
            except ValidationError as exc:
                rows_failed += 1
                errors.append(f"Row {idx}: validation error: {exc}")

        return NetworkIngestionResult(
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
