import csv
from typing import Dict

from sqlalchemy.orm import Session

from app.models.utilization_metric import UtilizationMetric


EXPECTED_HEADERS = [
    "server_id",
    "cpu_avg",
    "cpu_peak",
    "ram_avg_gb",
    "ram_peak_gb",
    "storage_avg_gb",
    "storage_peak_gb",
    "observation_window",
    "notes",
]


def _parse_float(value: str) -> float | None:
    v = (value or "").strip()
    if not v:
        return None
    try:
        return float(v)
    except ValueError:
        return None


def ingest_utilization_csv(db: Session, run_id: str, csv_path: str) -> Dict[str, int]:
    """
    Ingest utilization metrics from a CSV.

    Expected columns:
      server_id, cpu_avg, cpu_peak, ram_avg_gb, ram_peak_gb,
      storage_avg_gb, storage_peak_gb, observation_window, notes
    """
    rows_ingested = 0

    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)

        if reader.fieldnames is None:
            raise ValueError("Utilization CSV appears to have no header row.")

        missing = [h for h in EXPECTED_HEADERS if h not in reader.fieldnames]
        if missing:
            raise ValueError(
                f"Missing expected columns in utilization CSV: {', '.join(missing)}"
            )

        for row in reader:
            if not row:
                continue

            record = UtilizationMetric(
                run_id=run_id,
                server_id=(row.get("server_id") or "").strip(),
                cpu_avg=_parse_float(row.get("cpu_avg") or ""),
                cpu_peak=_parse_float(row.get("cpu_peak") or ""),
                ram_avg_gb=_parse_float(row.get("ram_avg_gb") or ""),
                ram_peak_gb=_parse_float(row.get("ram_peak_gb") or ""),
                storage_avg_gb=_parse_float(row.get("storage_avg_gb") or ""),
                storage_peak_gb=_parse_float(row.get("storage_peak_gb") or ""),
                observation_window=(row.get("observation_window") or "").strip(),
                notes=(row.get("notes") or "").strip(),
            )

            db.add(record)
            rows_ingested += 1

        db.commit()

    return {"rows_ingested": rows_ingested}
