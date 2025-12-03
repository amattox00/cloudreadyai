from typing import Optional
from pydantic import BaseModel


class ServerInventory(BaseModel):
    hostname: str
    os: Optional[str] = None
    environment: Optional[str] = None
    cpu_count: Optional[int] = None
    memory_gb: Optional[float] = None
    storage_gb: Optional[float] = None
    ip: Optional[str] = None
