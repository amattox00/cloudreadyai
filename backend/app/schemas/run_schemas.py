from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class RunSchema(BaseModel):
    """
    Lightweight representation of an ingestion run used by:
    - /runs
    - /v1/run_registry
    """

    run_id: str
    name: Optional[str] = None
    status: Optional[str] = None

    # Customer is optional and may not exist on the DB model.
    customer: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Pydantic v2: replaces orm_mode = True
    model_config = ConfigDict(from_attributes=True)


class RunListResponse(BaseModel):
    """
    Wrapper used by list endpoints so the JSON payload is:
    {
      "runs": [ ...RunSchema... ]
    }
    """

    runs: List[RunSchema]
