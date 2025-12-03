from typing import Dict, Optional
from pydantic import BaseModel


class AnalysisRunSummary(BaseModel):
    """
    Lightweight summary of an analysis run, returned by the /analysis endpoints.
    """

    run_id: str
    status: str  # e.g. "ok", "ingestion_incomplete", "error"
    dataset_health: str  # e.g. "ok", "warning", "critical"
    counts: Dict[str, int]  # servers, databases, storage, network, etc.
    notes: Optional[str] = None
