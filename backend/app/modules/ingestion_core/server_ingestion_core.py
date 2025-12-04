import csv
from typing import IO, Callable, List
from pydantic import BaseModel, Field, ValidationError


class ServerRow(BaseModel):
    hostname: str
    environment: str | None = None
    os: str | None = None
    platform: str | None = None
    vm_id: str | None = None
    ip_address: str | None = None
    subnet: str | None = None
    datacenter: str | None = None
    cluster_name: str | None = None
    role: str | None = None
    app_name: str | None = None
    owner: str | None = None
    criticality: str | None = None
    cpu_cores: int | None = Field(default=None, ge=0)
    memory_gb: float | None = Field(default=None, ge=0)
    storage_gb: float | None = Field(default=None, ge=0)
    is_virtual: bool | None = None
    is_cloud: bool | None = None
    tags: str | None = None

    class Config:
        extra = "allow"


class IngestionResult(BaseModel):
    rows_processed: int
    rows_successful: int
    rows_failed: int
    errors: List[str]


PersistFn = Callable[[ServerRow], None]


def ingest_servers_from_csv(
    file_like: IO[str],
    persist_row: PersistFn,
) -> IngestionResult:
    reader = csv.DictReader(file_like)

    rows_processed = 0
    rows_successful = 0
    errors: list[str] = []

    for idx, raw_row in enumerate(reader, start=1):
        rows_processed += 1

        try:
            row = ServerRow(**raw_row)
        except ValidationError as ve:
            errors.append(f"Row {idx}: validation error: {ve.errors()}")
            continue

        try:
            persist_row(row)
            rows_successful += 1
        except Exception as e:  # noqa: BLE001
            errors.append(f"Row {idx}: persist error: {e!r}")

    rows_failed = rows_processed - rows_successful

    return IngestionResult(
        rows_processed=rows_processed,
        rows_successful=rows_successful,
        rows_failed=rows_failed,
        errors=errors,
    )
