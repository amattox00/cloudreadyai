import csv
from dataclasses import dataclass
from typing import List, Optional, TextIO


@dataclass
class IngestionResult:
    run_id: str
    rows_processed: int
    rows_successful: int
    rows_failed: int
    errors: List[str]


@dataclass
class UtilizationRow:
    run_id: str
    hostname: str
    environment: Optional[str]
    metric_window: Optional[str]
    avg_cpu_percent: Optional[float]
    peak_cpu_percent: Optional[float]
    avg_ram_percent: Optional[float]
    peak_ram_percent: Optional[float]
    avg_disk_percent: Optional[float]
    peak_disk_percent: Optional[float]
    avg_net_mbps: Optional[float]
    peak_net_mbps: Optional[float]
    sample_count: Optional[int]
    tags: Optional[str]


def _to_float(value: str) -> Optional[float]:
    value = (value or "").strip()
    if value == "":
        return None
    return float(value)


def _to_int(value: str) -> Optional[int]:
    value = (value or "").strip()
    if value == "":
        return None
    return int(value)


def ingest_utilization_from_csv(run_id: str, file_like: TextIO) -> tuple[IngestionResult, List[UtilizationRow]]:
    """
    Parse utilization CSV for a given run_id.

    The CSV is expected to have columns:
    hostname,environment,metric_window,
    avg_cpu_percent,peak_cpu_percent,
    avg_ram_percent,peak_ram_percent,
    avg_disk_percent,peak_disk_percent,
    avg_net_mbps,peak_net_mbps,
    sample_count,tags
    """
    reader = csv.DictReader(file_like)
    rows: List[UtilizationRow] = []
    errors: List[str] = []

    rows_processed = 0
    rows_successful = 0

    for idx, raw in enumerate(reader, start=2):  # header = line 1, first data row = 2
        rows_processed += 1
        try:
            hostname = (raw.get("hostname") or "").strip()
            if not hostname:
                raise ValueError("hostname is required")

            environment = (raw.get("environment") or "").strip() or None
            metric_window = (raw.get("metric_window") or "").strip() or None

            avg_cpu = _to_float(raw.get("avg_cpu_percent", ""))
            peak_cpu = _to_float(raw.get("peak_cpu_percent", ""))
            avg_ram = _to_float(raw.get("avg_ram_percent", ""))
            peak_ram = _to_float(raw.get("peak_ram_percent", ""))
            avg_disk = _to_float(raw.get("avg_disk_percent", ""))
            peak_disk = _to_float(raw.get("peak_disk_percent", ""))
            avg_net = _to_float(raw.get("avg_net_mbps", ""))
            peak_net = _to_float(raw.get("peak_net_mbps", ""))
            sample_count = _to_int(raw.get("sample_count", ""))

            tags = (raw.get("tags") or "").strip() or None

            row = UtilizationRow(
                run_id=run_id,
                hostname=hostname,
                environment=environment,
                metric_window=metric_window,
                avg_cpu_percent=avg_cpu,
                peak_cpu_percent=peak_cpu,
                avg_ram_percent=avg_ram,
                peak_ram_percent=peak_ram,
                avg_disk_percent=avg_disk,
                peak_disk_percent=peak_disk,
                avg_net_mbps=avg_net,
                peak_net_mbps=peak_net,
                sample_count=sample_count,
                tags=tags,
            )
            rows.append(row)
            rows_successful += 1
        except Exception as exc:
            errors.append(f"Row {idx}: validation error: {exc}")

    result = IngestionResult(
        run_id=run_id,
        rows_processed=rows_processed,
        rows_successful=rows_successful,
        rows_failed=rows_processed - rows_successful,
        errors=errors,
    )
    return result, rows
