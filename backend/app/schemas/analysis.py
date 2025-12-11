from typing import List, Optional
from pydantic import BaseModel


class EnvironmentBreakdown(BaseModel):
    """
    Simple count of servers per environment (e.g., Prod, Dev, Test).
    """
    name: str
    count: int


class OSSummary(BaseModel):
    """
    Aggregated view of OS families and how many are legacy/EOL.
    """
    family: str
    count: int
    legacy_count: int


class ReadinessSummary(BaseModel):
    """
    High-level readiness banding for the run.
    """
    ready_for_rehost: int
    needs_modernization: int
    needs_investigation: int


class RecommendationItem(BaseModel):
    """
    Per-server recommendation row.
    """
    server_id: str
    hostname: Optional[str]
    ip: Optional[str]
    environment: Optional[str]
    os: Optional[str]

    strategy: str              # e.g., "Rehost", "Refactor / Modernize"
    risk_level: str            # e.g., "Low", "Medium", "High"
    wave: int                  # migration wave number

    summary: str               # short explanation

    estimated_monthly_savings: Optional[float] = None
    target_platform: Optional[str] = None


class AnalysisSummary(BaseModel):
    """
    Top-level summary returned by /v1/analysis/{run_id}/summary
    """
    run_id: str

    total_servers: int
    environments: List[EnvironmentBreakdown]
    os_summary: List[OSSummary]

    legacy_server_count: int
    modern_server_count: int

    readiness: ReadinessSummary

    notes: List[str]


class AnalysisRecommendations(BaseModel):
    """
    Canonical response model for /v1/analysis/{run_id}/recommendations
    """
    run_id: str
    total_recommendations: int
    items: List[RecommendationItem]


# --- Backward-compatible aliases -------------------------------------------

class RecommendationResponse(AnalysisRecommendations):
    """
    Alias used by older code paths (run_views_v2 / run_views_servers_v2).
    """
    pass


class RecommendationsResponse(AnalysisRecommendations):
    """
    Alias used by routers expecting RecommendationsResponse.
    """
    pass
