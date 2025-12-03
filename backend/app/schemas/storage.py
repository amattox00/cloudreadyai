from typing import Optional
from pydantic import BaseModel


class StorageInventory(BaseModel):
    volume_name: str
    size_gb: Optional[float] = None
    storage_type: Optional[str] = None
    mount_point: Optional[str] = None
