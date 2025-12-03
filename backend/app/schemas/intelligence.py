from typing import List, Optional
from pydantic import BaseModel


class OverallReadiness(BaseModel):
    score: int
    label: str
    confidence: float


class MigrationRecommendation(BaseModel):
    primary_strategy: str
    summary: str
    detail: Optional[str] = None
    alternatives: List[str] = []


class KeyInsights(BaseModel):
    top_blockers: List[str] = []
    top_opportunities: List[str] = []
    risk_flags: List[str] = []
    complexity_score: float = 0.0


class ApplicationInsight(BaseModel):
    name: str
    business_tier: Optional[str] = None
    recommended_path: str
    risk_level: Optional[str] = None
    notes: Optional[str] = None


class IntelligenceSummary(BaseModel):
    run_id: str
    org_name: Optional[str] = None
    environment: Optional[str] = None

    overall_readiness: OverallReadiness
    migration_recommendation: MigrationRecommendation
    key_insights: KeyInsights
    applications: List[ApplicationInsight] = []

    engine_version: str = "phase-c-1.0"
