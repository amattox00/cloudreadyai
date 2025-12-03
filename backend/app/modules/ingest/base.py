import csv
import os
import tempfile
from typing import Any, Dict, List

from fastapi import UploadFile


class IngestError(Exception):
    """Domain-specific error for ingestion failures."""
    pass


class BaseIngestor:
    """
    Very lightweight base ingestor class.

    Child ingestors (servers, storage, etc.) can inherit this so they all have
    a common shape: run_id, file_path, and db handle.
    """

    def __init__(self, run_id: str, file_path: str, db: Any) -> None:
        self.run_id = run_id
        self.file_path = file_path
        self.db = db

    def ingest(self) -> int:
        """
        Perform ingestion.

        Child classes should implement this and return an integer (e.g. number
        of rows ingested).
        """
        raise NotImplementedError("Child ingestors must implement ingest()")


def save_temp_upload(upload: UploadFile) -> str:
    """
    Save a FastAPI UploadFile to a temporary file on disk and return the path.

    This is used by the ingest router: it receives an UploadFile, we persist it
    to a temp location, and then the ingestor classes read from that path.
    """
    # Determine a safe suffix based on the original file name (e.g. ".csv")
    _, ext = os.path.splitext(upload.filename or "")
    fd, tmp_path = tempfile.mkstemp(prefix="ingest_", suffix=ext or ".csv")

    try:
        # Close the OS-level file descriptor — we'll reopen by path
        os.close(fd)

        with open(tmp_path, "wb") as out_f:
            out_f.write(upload.file.read())

        # Reset file pointer so the UploadFile can be reused if needed
        try:
            upload.file.seek(0)
        except Exception:
            # Not fatal; just means we can't reuse the stream
            pass

        return tmp_path
    except Exception as exc:
        raise IngestError(f"Failed to persist uploaded file: {exc}") from exc


def read_csv(file_path: str) -> List[Dict[str, Any]]:
    """
    Read a CSV file from disk and return a list of normalized dict rows.

    This matches what the ingestion modules expect:
    - Uses csv.DictReader
    - Strips whitespace from headers and string values
    - Raises IngestError on common failure modes
    """
    try:
        with open(file_path, mode="r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            rows: List[Dict[str, Any]] = []

            for row in reader:
                # Normalize: strip whitespace around keys and string values
                cleaned: Dict[str, Any] = {}
                for k, v in row.items():
                    key = k.strip() if isinstance(k, str) else k
                    if isinstance(v, str):
                        cleaned[key] = v.strip()
                    else:
                        cleaned[key] = v
                rows.append(cleaned)

        if not rows:
            raise IngestError("CSV file is empty or has no data rows.")

        return rows

    except FileNotFoundError:
        raise IngestError(f"CSV file not found: {file_path}")
    except IngestError:
        # Let IngestError bubble up unchanged
        raise
    except Exception as exc:
        raise IngestError(f"Failed to read CSV: {exc}") from exc
