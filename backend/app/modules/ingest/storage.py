from pathlib import Path
from typing import Dict, Any

from sqlalchemy.orm import Session
from app.modules.ingest.base import BaseIngestor


class StorageIngestor(BaseIngestor):
    """Clean storage ingestion with the new BaseIngestor engine."""

    table_name = "storage"

    # Accepted CSV header variants
    header_map = {
        "volume_id": ["volume_id", "vol_id", "id"],
        "server_id": ["server_id", "server", "host"],
        "size_gb": ["size_gb", "capacity_gb", "size", "gb"],
        "storage_type": ["storage_type", "type", "class"],
    }

    required_fields = ["volume_id", "size_gb"]

    db_columns = [
        "run_id",
        "volume_id",
        "server_id",
        "size_gb",
        "storage_type",
        "raw",
    ]

    def build_row(self, row: Dict[str, Any], run_id: str) -> Dict[str, Any]:
        return {
            "run_id": run_id,
            "volume_id": row.get("volume_id") or "",
            "server_id": row.get("server_id") or None,
            "size_gb": float(row.get("size_gb", 0) or 0),
            "storage_type": row.get("storage_type"),
            "raw": row,
        }
