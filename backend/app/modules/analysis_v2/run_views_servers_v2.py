# app/modules/analysis_v2/run_views_servers_v2.py

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.inventory_server_v2 import InventoryServerV2
from app.models.server import Server
from app.schemas.analysis import (
    AnalysisSummary,
    EnvironmentBreakdown,
    OSSummary,
    ReadinessSummary,
    RecommendationItem,
    RecommendationResponse,   # <- alias defined in schemas/analysis.py
)

@dataclass
class ServerRow:
    """
    Normalized view of a server record, regardless of which table it came from.
    """

    id: str
    hostname: str
    os: Optional[str]
    environment: Optional[str]


def _classify_os(os_name: Optional[str]) -> Tuple[str, bool]:
    """
    Return (family, is_legacy) for a given OS string.
    We keep this deliberately simple – good enough for early MVP.
    """
    if not os_name:
        return "Unknown", True

    name = os_name.lower()

    # Basic family detection
    if "windows" in name or name.startswith("win"):
        family = "Windows"
    elif any(x in name for x in ["linux", "ubuntu", "centos", "red hat", "rhel", "suse"]):
        family = "Linux"
    elif any(x in name for x in ["aix", "hp-ux", "solaris"]):
        family = "Unix"
    else:
        family = "Other"

    # Very rough legacy markers – this will evolve over time
    legacy_markers = [
        "2000",
        "2003",
        "2008",
        "2012",
        "xp",
        "vista",
        "2003 r2",
        "2008 r2",
        "nt 4",
        "rhel 5",
        "rhel 6",
        "esx 4",
    ]
    is_legacy = any(m in name for m in legacy_markers)

    return family, is_legacy


def _normalize_env(env: Optional[str]) -> str:
    """
    Map raw env values (dev, prod, qa, test, etc.) into friendly labels.
    """
    if not env:
        return "Unknown"

    e = env.strip()
    if not e:
        return "Unknown"

    lower = e.lower()
    if lower.startswith("dev"):
        return "Development"
    if lower.startswith("prod"):
        return "Production"
    if lower.startswith("qa") or "test" in lower:
        return "Test / QA"
    return e


def _load_servers(db: Session, run_id: str) -> List[ServerRow]:
    """
    Load servers for a run_id.

    1. Prefer the v2 table (inventory_servers_v2)
    2. Fall back to the legacy servers table if nothing is found
    """
    servers: List[ServerRow] = []

    # --- Try v2 table first ---
    v2_rows: List[InventoryServerV2] = (
        db.query(InventoryServerV2)
        .filter(InventoryServerV2.run_id == run_id)
        .all()
    )

    if v2_rows:
        for row in v2_rows:
            servers.append(
                ServerRow(
                    id=str(getattr(row, "id", "")),
                    hostname=row.hostname,
                    os=row.os,
                    environment=row.environment,
                )
            )
    else:
        # --- Fall back to legacy 'servers' table ---
        legacy_rows: List[Server] = (
            db.query(Server)
            .filter(Server.run_id == run_id)
            .all()
        )
        for row in legacy_rows:
            servers.append(
                ServerRow(
                    id=str(getattr(row, "server_id", "")),
                    hostname=row.hostname or "",
                    os=row.os,
                    environment=row.environment,
                )
            )

    if not servers:
        raise HTTPException(
            status_code=404,
            detail=f"No servers found for run_id={run_id}",
        )

    return servers


def build_server_summary(db: Session, run_id: str) -> AnalysisSummary:
    """
    Build the high-level summary used by the Analysis page.
    """
    servers = _load_servers(db, run_id)
    total = len(servers)

    env_counts: Dict[str, int] = {}
    os_buckets: Dict[str, Dict[str, int]] = {}
    legacy_total = 0
    modern_total = 0
    missing_os = 0

    for s in servers:
        # Environment buckets
        env_key = _normalize_env(s.environment)
        env_counts[env_key] = env_counts.get(env_key, 0) + 1

        # OS & legacy detection
        family, is_legacy = _classify_os(s.os)
        bucket = os_buckets.setdefault(family, {"count": 0, "legacy": 0})
        bucket["count"] += 1
        if is_legacy:
            bucket["legacy"] += 1
            legacy_total += 1
        else:
            modern_total += 1

        if not s.os:
            missing_os += 1

    environments = [
        EnvironmentBreakdown(name=name, count=count)
        for name, count in sorted(env_counts.items(), key=lambda x: x[0])
    ]

    os_summary = [
        OSSummary(family=family, count=data["count"], legacy_count=data["legacy"])
        for family, data in os_buckets.items()
    ]

    # Simple readiness model for now
    readiness = ReadinessSummary(
        ready_for_rehost=modern_total,
        needs_modernization=legacy_total,
        needs_investigation=total,
    )

    notes: List[str] = []
    if missing_os:
        notes.append(f"{missing_os} servers are missing OS details.")
    if legacy_total:
        notes.append(
            f"{legacy_total} servers appear to be running legacy / EOL operating systems."
        )

    return AnalysisSummary(
        run_id=run_id,
        total_servers=total,
        environments=environments,
        os_summary=os_summary,
        legacy_server_count=legacy_total,
        modern_server_count=modern_total,
        readiness=readiness,
        notes=notes,
    )


def build_server_recommendations(db: Session, run_id: str) -> RecommendationResponse:
    """
    Build per-server recommendations used by the Analysis / Insights views.
    """
    servers = _load_servers(db, run_id)
    items: List[RecommendationItem] = []

    for idx, s in enumerate(servers, start=1):
        env_raw = s.environment or ""
        env_lower = env_raw.lower()

        _, is_legacy = _classify_os(s.os)

        if is_legacy:
            strategy = "Refactor / Modernize"
            risk_level = "High" if env_lower.startswith("prod") else "Medium"
        else:
            strategy = "Rehost"
            risk_level = "Low" if env_lower.startswith("dev") else "Medium"

        if env_lower.startswith("prod"):
            wave = 3
        elif env_lower.startswith("dev"):
            wave = 2
        else:
            wave = 1

        summary_parts: List[str] = []
        if is_legacy:
            summary_parts.append("Legacy/EOL OS detected.")
        if env_lower.startswith("prod"):
            summary_parts.append("Production workload.")
        summary = " ".join(summary_parts) or "Baseline server recommendation."

        items.append(
            RecommendationItem(
                server_id=s.id or str(idx),
                hostname=s.hostname,
                ip=None,
                environment=s.environment,
                os=s.os,
                strategy=strategy,
                risk_level=risk_level,
                wave=wave,
                summary=summary,
                estimated_monthly_savings=None,
                target_platform=None,
            )
        )

    return RecommendationResponse(
        run_id=run_id,
        total_recommendations=len(items),
        items=items,
    )
# ---------------------------------------------------------------------------
# Public API used by routers (thin wrappers around the server-focused helpers)
# ---------------------------------------------------------------------------

def build_analysis_summary(db: Session, run_id: str) -> AnalysisSummary:
    """
    Wrapper used by the /v1/analysis router.
    """
    return build_server_summary(db, run_id)


def build_recommendations(db: Session, run_id: str) -> RecommendationResponse:
    """
    Wrapper used by the /v1/analysis router.
    """
    return build_server_recommendations(db, run_id)
