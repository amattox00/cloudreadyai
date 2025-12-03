from typing import Optional
from pydantic import BaseModel


class NetworkInventory(BaseModel):
    cidr: str
    environment: Optional[str] = None
    vlan: Optional[str] = None
    gateway: Optional[str] = None
