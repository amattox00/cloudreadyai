from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class DiagramMetadata(BaseModel):
    cloud: str = Field(..., description="aws | azure | gcp | hybrid")
    use_case: str = Field(
        "landing_zone",
        description="Workload type such as landing_zone, app_migration, data_lake, etc.",
    )
    compliance: Optional[str] = Field(
        None, description="fedramp, dod, nist80053, hipaa, etc."
    )
    environment: Optional[str] = Field(None, description="Dev, Test, Stage, Prod")
    org_name: Optional[str] = None
    workload_name: Optional[str] = None
    opportunity_id: Optional[str] = None
    version_tag: Optional[str] = None


class DiagramAutoLayoutRequest(BaseModel):
    xml: str = Field(..., description="Original draw.io/mxgraph XML")
    metadata: DiagramMetadata


class DiagramZeroTrustRequest(BaseModel):
    xml: str = Field(..., description="Input XML (already auto-laid out or raw)")
    metadata: DiagramMetadata


class DiagramEnrichRequest(BaseModel):
    xml: str = Field(..., description="Input XML (may already include layout/overlays)")
    metadata: DiagramMetadata
    enable_auto_layout: bool = True
    enable_zero_trust: bool = True
    include_recommendations: bool = True


class DiagramRecommendation(BaseModel):
    category: str
    title: str
    description: str
    severity: str = "info"
    tags: List[str] = []


class DiagramEnrichResponse(BaseModel):
    xml: str
    metadata: DiagramMetadata
    recommendations: List[DiagramRecommendation] = []
    extras: Dict[str, Any] = {}
