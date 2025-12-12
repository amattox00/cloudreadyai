from __future__ import annotations

import csv
import io
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Set, Tuple


EXPECTED_HEADERS = [
    "app_id",
    "depends_on_app_id",
    "dependency_type",
    "notes",
]

# Keep this permissive for MVP. You can tighten later.
ALLOWED_DEP_TYPES = {
    "http",
    "https",
    "api",
    "grpc",
    "mq",
    "kafka",
    "amqp",
    "sqs",
    "sns",
    "event",
    "batch",
    "file",
    "ftp",
    "sftp",
    "sql",
    "jdbc",
    "odbc",
    "db",
    "cache",
    "redis",
    "memcached",
    "rpc",
    "other",
    "",
}


@dataclass
class DependencyEdge:
    app_id: str
    depends_on_app_id: str
    dependency_type: str = ""
    notes: str = ""


@dataclass
class DependenciesIngestionResult:
    rows_processed: int = 0
    rows_successful: int = 0
    rows_failed: int = 0
    errors: List[str] = field(default_factory=list)

    # validation counters (non-fatal unless you choose otherwise)
    self_dependencies: int = 0
    invalid_type: int = 0
    missing_required: int = 0
    normalized_blanks: int = 0

    # derived coverage counters (filled later if caller provides app ids)
    unknown_targets: int = 0
    unknown_sources: int = 0

    records: List[DependencyEdge] = field(default_factory=list)


def _norm(s: Optional[str]) -> str:
    return (s or "").strip()


def _rownum(idx: int) -> int:
    # idx is 0-based for data rows
    return idx + 2  # + header row


def parse_dependencies_from_csv(
    *,
    file_like: io.StringIO,
    known_app_ids: Optional[Set[str]] = None,
) -> DependenciesIngestionResult:
    """
    Parse + validate Dependencies CSV into DependencyEdge records.

    - Required: app_id, depends_on_app_id
    - Normalizes whitespace
    - Rejects self-dependencies (counts + skips)
    - Validates dependency_type against ALLOWED_DEP_TYPES (counts + coerces to 'other')
    - Tracks unknown sources/targets if known_app_ids is provided
    """
    result = DependenciesIngestionResult()
    reader = csv.DictReader(file_like)

    if reader.fieldnames is None:
        result.errors.append("Dependencies CSV has no header row.")
        result.rows_failed = 0
        return result

    missing_headers = [h for h in EXPECTED_HEADERS if h not in reader.fieldnames]
    if missing_headers:
        result.errors.append(
            f"Missing expected columns: {', '.join(missing_headers)}"
        )
        return result

    for i, row in enumerate(reader):
        if not row:
            continue

        result.rows_processed += 1

        app_id = _norm(row.get("app_id"))
        depends_on = _norm(row.get("depends_on_app_id"))
        dep_type = _norm(row.get("dependency_type")).lower()
        notes = _norm(row.get("notes"))

        # required fields
        if not app_id or not depends_on:
            result.rows_failed += 1
            result.missing_required += 1
            result.errors.append(
                f"Row {_rownum(i)} missing required app_id/depends_on_app_id."
            )
            continue

        # self-dependency
        if app_id == depends_on:
            result.rows_failed += 1
            result.self_dependencies += 1
            result.errors.append(
                f"Row {_rownum(i)} invalid: app_id depends on itself ({app_id})."
            )
            continue

        # dependency type validation (non-fatal)
        if dep_type not in ALLOWED_DEP_TYPES:
            result.invalid_type += 1
            dep_type = "other"

        # unknown app coverage (non-fatal)
        if known_app_ids is not None:
            if app_id not in known_app_ids:
                result.unknown_sources += 1
            if depends_on not in known_app_ids:
                result.unknown_targets += 1

        result.records.append(
            DependencyEdge(
                app_id=app_id,
                depends_on_app_id=depends_on,
                dependency_type=dep_type,
                notes=notes,
            )
        )
        result.rows_successful += 1

    result.rows_failed = max(result.rows_processed - result.rows_successful, result.rows_failed)
    return result
