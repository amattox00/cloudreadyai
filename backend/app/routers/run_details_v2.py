from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.inventory_server_v2 import InventoryServerV2

router = APIRouter(
    prefix="/v2",
    tags=["run_details_v2"],
)


class ServerV2(BaseModel):
    hostname: str
    os: Optional[str] = None
    environment: Optional[str] = None
    vcpus: Optional[int] = None
    memory_gb: Optional[float] = None
    storage_gb: Optional[float] = None

    class Config:
        orm_mode = True


class RunServersV2Response(BaseModel):
    run_id: str
    total_servers: int
    servers: List[ServerV2]


@router.get("/run_details/{run_id}/servers", response_model=RunServersV2Response)
def get_run_servers_v2(run_id: str, db: Session = Depends(get_db)) -> RunServersV2Response:
    """
    Read-only view of servers for a given run_id from inventory_servers_v2.
    """
    # Adjust InventoryServerV2 class name / module if different
    servers = (
        db.query(InventoryServerV2)
        .filter(InventoryServerV2.run_id == run_id)
        .order_by(InventoryServerV2.hostname)
        .all()
    )

    if not servers:
        raise HTTPException(status_code=404, detail="No v2 servers found for this run_id")

    # Map ORM objects to Pydantic models explicitly
    servers_pydantic = []
    for s in servers:
        servers_pydantic.append(
            ServerV2(
                hostname=s.hostname,
                # Using getattr with defaults in case some columns don't exist yet
                os=getattr(s, "os", None),
                environment=getattr(s, "environment", None),
                vcpus=getattr(s, "vcpus", None),
                memory_gb=getattr(s, "memory_gb", None),
                storage_gb=getattr(s, "storage_gb", None),
            )
        )

    return RunServersV2Response(
        run_id=run_id,
        total_servers=len(servers_pydantic),
        servers=servers_pydantic,
    )

