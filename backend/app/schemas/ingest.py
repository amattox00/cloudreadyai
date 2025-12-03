from typing import Optional

from pydantic import BaseModel


class IngestResponse(BaseModel):
    """
    Standard response for an ingestion endpoint.
    This is intentionally simple so FastAPI/Pydantic never complains.
    """

    run_id: str
    slice: str
    rows_ingested: int
    rows_failed: int
    s3_key: Optional[str] = None
