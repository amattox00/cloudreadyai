from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class WorkloadComponentBase(BaseModel):
    id: int
    component_type: str
    component_ref_id: str

    class Config:
        orm_mode = True


class WorkloadBase(BaseModel):
    id: int
    run_id: str
    name: str
    type: str
    environment: Optional[str] = None
    criticality: Optional[str] = None
    complexity_score: Optional[int] = None
    risk_score: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    components: List[WorkloadComponentBase] = []

    class Config:
        orm_mode = True


class WorkloadListResponse(BaseModel):
    run_id: str
    workloads: List[WorkloadBase]
