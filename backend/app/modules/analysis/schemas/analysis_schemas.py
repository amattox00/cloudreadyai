from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


# ----------------------------
# R-Score (6R) schemas
# ----------------------------

class RScoreDetail(BaseModel):
    rehost: float
    replatform: float
    refactor: float
    repurchase: float
    retire: float
    retain: float
    final_recommendation: str


class ServerRScore(BaseModel):
    server_id: str
    score: RScoreDetail


class RScoreResponse(BaseModel):
    run_id: str
    servers: List[ServerRScore]


# ----------------------------
# Rightsizing schemas
# ----------------------------

class RightsizingDetail(BaseModel):
    current_cpu: float
    current_ram: float
    current_storage: float
    action: str  # DOWNSIZE / KEEP / UPSCALE
    target_size: Optional[str] = None  # small / medium / large, etc.
    rationale: Optional[str] = None


class RightsizingServer(BaseModel):
    server_id: str
    rightsizing: RightsizingDetail


class RightsizingResponse(BaseModel):
    run_id: str
    servers: List[RightsizingServer]


# ----------------------------
# Analysis run summary schema
# ----------------------------

class AnalysisRunSummary(BaseModel):
    run_id: str
    status: str
    # Arbitrary nested summary dict:
    # {
    #   "profiles": { "server_profile_count": 3 },
    #   "rscore_overview": { ... },
    #   "rightsizing_overview": { ... }
    # }
    summary: Optional[Dict[str, Any]] = None
