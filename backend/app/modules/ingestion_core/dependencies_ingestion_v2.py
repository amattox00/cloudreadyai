from __future__ import annotations

import csv
from dataclasses import dataclass
from typing import List, TextIO, Optional, Literal

from pydantic import BaseModel, Field, ValidationError, model_validator


@dataclass
class DependencyIngestionResult:
    """
    Standard ingestion result for dependencies v2.
    Mirrors the pattern used by servers/storage/databases/applications.
    """

    run_id: str
    rows_processed: int
    rows_successful: int
    rows_failed: int
    errors: List[str]
    records: List["DependencyRow"]


class DependencyRow(BaseModel):
    """
    One dependency edge between an application and either a server or a database.
    """

    app_name: str = Field(..., min_length=1)
    environment: Optional[str] = None

    # "server" → requires server_hostname
    # "database" → requires database_name
    dependency_type: Literal["server", "database"]

    server_hostname: Optional[str] = None
    database_name: Optional[str] = None
    database_engine: Optional[str] = None

    notes: Optional[str] = None
    tags: Optional[str] = None

    @model_validator(mode="after")
    def check_target(self) -> "DependencyRow":
        """
        Enforce that the right target fields are present based on dependency_type.
        """
        if self.dependency_type == "server":
            if not self.server_hostname or not self.server_hostname.strip():
                raise ValueError(
                    "server_hostname is required when dependency_type='server'"
                )
        elif self.dependency_type == "database":
            if not self.database_name or not self.database_name.strip():
                raise ValueError(
                    "database_name is required when dependency_type='database'"
                )
        return self


def ingest_dependencies_from_csv(
    run_id: str,
    file_like: TextIO,
) -> DependencyIngestionResult:
    """
    Core CSV ingestion for dependencies v2.

    - Reads dependencies_template_v2.csv style files
    - Validates each row with DependencyRow
    - Skips bad rows but records errors
    """

    reader = csv.DictReader(file_like)

    rows_processed = 0
    rows_successful = 0
    rows_failed = 0
    errors: List[str] = []
    records: List[DependencyRow] = []

    # Assume header is on line 1; data starts from line 2
    for line_number, raw in enumerate(reader, start=2):
        rows_processed += 1

        try:
            dependency_type_raw = (raw.get("dependency_type") or "").strip().lower()

            row = DependencyRow(
                app_name=(raw.get("app_name") or "").strip(),
                environment=(raw.get("environment") or "").strip() or None,
                dependency_type=dependency_type_raw,  # will be validated as "server" or "database"
                server_hostname=(raw.get("server_hostname") or "").strip() or None,
                database_name=(raw.get("database_name") or "").strip() or None,
                database_engine=(raw.get("database_engine") or "").strip() or None,
                notes=(raw.get("notes") or "").strip() or None,
                tags=(raw.get("tags") or "").strip() or None,
            )

            records.append(row)
            rows_successful += 1

        except ValidationError as ve:
            rows_failed += 1
            errors.append(f"Row {line_number}: validation error: {ve}")
        except Exception as exc:  # Catch-all just in case
            rows_failed += 1
            errors.append(f"Row {line_number}: unexpected error: {exc}")

    return DependencyIngestionResult(
        run_id=run_id,
        rows_processed=rows_processed,
        rows_successful=rows_successful,
        rows_failed=rows_failed,
        errors=errors,
        records=records,
    )
