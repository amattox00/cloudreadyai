from typing import Optional

from pydantic import BaseModel


class VCenterRow(BaseModel):
    """
    Represents a single row from a vCenter export CSV.

    Example headers:
    vm_name,cluster,datacenter,hostname,os,environment,cpu_count,memory_gb,storage_gb,ip
    """

    vm_name: str
    cluster: Optional[str] = None
    datacenter: Optional[str] = None
    hostname: Optional[str] = None
    os: Optional[str] = None
    environment: Optional[str] = None
    cpu_count: Optional[int] = None
    memory_gb: Optional[float] = None
    storage_gb: Optional[float] = None
    ip: Optional[str] = None
