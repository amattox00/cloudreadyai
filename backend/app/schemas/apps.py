from typing import Optional
from pydantic import BaseModel


class AppInventory(BaseModel):
    application_name: str
    criticality: Optional[str] = None
    environment: Optional[str] = None
    business_unit: Optional[str] = None
    owner: Optional[str] = None
    hostname: Optional[str] = None
    notes: Optional[str] = None
