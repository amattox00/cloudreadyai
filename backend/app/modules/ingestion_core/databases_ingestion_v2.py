from __future__ import annotations

import csv
from dataclasses import dataclass
from typing import IO, List, Optional

from pydantic import BaseModel, Field, ValidationError, field_validator


class DatabaseRow(BaseModel):
    hostname: str = Field(..., description="Host or instance name where the DB runs")
    db_name: str = Field(..., description="Database name")
    db_engine: str = Field(..., description="Engine family (Oracle, SQLServer, Postgres, MySQL, etc.)")
    engine_version: Optional[str] = Field(None, description="Database engine version")
    environment: Optional[str] = Field(None, description="Environment (prod, dev, stage, qa, etc.)")
    platform: Optional[str] = Field(None, description="Underlying platform (vmware, aws_rds, azure_sql, etc.)")
    cluster_name: Optional[str] = None
    port: Optional[int] = None
    db_role: Optional[str] = Field(None, description="primary, standby, read_replica, etc.")
    ha_enabled: Optional[bool] = None
    criticality: Optional[str] = None
    owner: Optional[str] = None

    cpu_cores: Optional[int] = None
    memory_gb: Optional[float] = None
    storage_gb: Optional[float] = None
    allocated_storage_gb: Optional[float] = None
    used_storage_gb: Optional[float] = None

    is_cloud: Optional[bool] = None
    cloud_provider: Optional[str] = None
    region: Optional[str] = None
    tags: Optional[str] = None

    @field_validator(
        "cpu_cores", mode="before"
    )
    def parse_int_nullable(cls, v):
        if v is None:
            return None
        if isinstance(v, int):
            return v
        v_str = str(v).strip()
        if v_str == "":
            return None
        return int(v_str)

    @field_validator(
        "memory_gb",
        "storage_gb",
        "allocated_storage_gb",
        "used_storage_gb",
        mode="before",
    )
    def parse_float_nullable(cls, v):
        if v is None:
            return None
        if isinstance(v, (int, float)):
            return float(v)
        v_str = str(v).strip()
        if v_str == "":
            return None
        return float(v_str)

    @field_validator("port", mode="before")
    def parse_port_nullable(cls, v):
        if v is None:
            return None
        if isinstance(v, int):
            return v
        v_str = str(v).strip()
        if v_str == "":
            return None
        return int(v_str)

    @field_validator("ha_enabled", "is_cloud", mode="before")
    def parse_bool_nullable(cls, v):
        if v is None:
            return None
        if isinstance(v, bool):
            return v
        v_str = str(v).strip().lower()
        if v_str in ("", "n/a"):
            return None
        if v_str in ("true", "yes", "y", "1"):
            return True
        if v_str in ("false", "no", "n", "0"):
            return False
        # If it's something weird like "maybe", treat as None
        return None

    @field_validator(
        "hostname",
        "db_name",
        "db_engine",
        mode="after",
    )
    def required_non_empty(cls, v, info):
        if v is None:
            raise ValueError(f"{info.field_name} is required")
        if isinstance(v, str) and v.strip() == "":
            raise ValueError(f"{info.field_name} is required")
        return v


@dataclass
class DatabaseIngestionResult:
    run_id: str
    rows_processed: int
    rows_successful: int
    rows_failed: int
    errors: List[str]
    records: List[DatabaseRow]


def ingest_databases_from_csv(run_id: str, file_like: IO[str]) -> DatabaseIngestionResult:
    """
    Ingest a databases CSV into validated DatabaseRow objects.

    This does not write to the database; it just parses and validates.
    """
    reader = csv.DictReader(file_like)
    rows_processed = 0
    rows_successful = 0
    rows_failed = 0
    errors: List[str] = []
    records: List[DatabaseRow] = []

    for idx, raw in enumerate(reader, start=2):  # header is row 1
        rows_processed += 1
        try:
            row = DatabaseRow(**raw)
            records.append(row)
            rows_successful += 1
        except ValidationError as ve:
            rows_failed += 1
            errors.append(f"Row {idx}: validation error: {ve}")

    return DatabaseIngestionResult(
        run_id=run_id,
        rows_processed=rows_processed,
        rows_successful=rows_successful,
        rows_failed=rows_failed,
        errors=errors,
        records=records,
    )
