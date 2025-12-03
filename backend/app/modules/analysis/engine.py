from typing import List, Optional
from sqlalchemy.orm import Session

from app import models
from app.schemas.intelligence import (
    OverallReadiness,
    MigrationRecommendation,
    KeyInsights,
    ApplicationInsight,
    IntelligenceSummary,
)


def _compute_readiness_score(servers: List["models.Server"], apps: List["models.App"]) -> OverallReadiness:
    legacy_os_penalties = 0
    unknown_size_penalties = 0
    app_complexity_penalties = 0

    for s in servers:
        os_name = (getattr(s, "os_name", "") or "").lower()
        if any(x in os_name for x in ["2003", "2008", "xp"]):
            legacy_os_penalties += 5

        if getattr(s, "cpu_cores", None) is None or getattr(s, "memory_gb", None) is None:
            unknown_size_penalties += 2

    for a in apps:
        arch = (getattr(a, "architecture", "") or "").lower()
        if "monolith" in arch:
            app_complexity_penalties += 5

    base_score = 85
    score = base_score - legacy_os_penalties - unknown_size_penalties - app_complexity_penalties
    score = max(0, min(100, score))

    if score >= 80:
        label = "Ready now"
    elif score >= 60:
        label = "Ready with minor changes"
    else:
        label = "Needs preparation"

    confidence = 0.7
    if unknown_size_penalties > 5:
        confidence -= 0.1
    if legacy_os_penalties > 10:
        confidence -= 0.1

    confidence = max(0.0, min(1.0, confidence))

    return OverallReadiness(score=score, label=label, confidence=confidence)


def _build_migration_recommendation(readiness: OverallReadiness) -> MigrationRecommendation:
    if readiness.label == "Ready now":
        primary = "Rehost with targeted replatforming"
        summary = "Most workloads can move to the cloud with limited changes."
        detail = (
            "The environment scores high on readiness. A practical path is to start with lift-and-shift "
            "for the majority of workloads, while replatforming a few high-impact data and analytics workloads."
        )
        alternatives = [
            "Full replatform for all workloads.",
            "Minimal-change rehost only.",
        ]
    elif readiness.label == "Ready with minor changes":
        primary = "Rehost first, then replatform over time"
        summary = "Begin with lift-and-shift and plan phased modernization."
        detail = (
            "The environment is broadly suitable for migration. A phased replatforming approach balances "
            "risk while enabling managed services adoption."
        )
        alternatives = [
            "Replatform key applications during migration.",
            "Prep additional workloads before migrating.",
        ]
    else:
        primary = "Prepare and modernize before migration"
        summary = "Address key blockers before broad migration."
        detail = (
            "The environment contains migration blockers. Addressing modernization needs ahead of "
            "large-scale movement will reduce risk."
        )
        alternatives = [
            "Pilot low-risk workloads first.",
            "Delay migration waves until blockers are fixed.",
        ]

    return MigrationRecommendation(
        primary_strategy=primary,
        summary=summary,
        detail=detail,
        alternatives=alternatives,
    )


def _build_key_insights(
    readiness: OverallReadiness,
    servers: List["models.Server"],
    apps: List["models.App"],
) -> KeyInsights:
    blockers = []
    opportunities = []
    risk_flags = []

    for s in servers:
        os_name = (getattr(s, "os_name", "") or "").lower()
        if any(x in os_name for x in ["2003", "2008", "xp"]):
            hostname = getattr(s, "hostname", f"server-{s.id}")
            blockers.append(f"Legacy OS detected on {hostname}")
            risk_flags.append("Legacy OS")

    for a in apps:
        criticality = (getattr(a, "criticality", "") or "").lower()
        if "tier 1" in criticality:
            risk_flags.append(
                f"Tier-1 application {getattr(a, 'name', f'app-{a.id}')}"
            )

        arch = (getattr(a, "architecture", "") or "").lower()
        if "monolith" in arch:
            blockers.append(
                f"Monolithic architecture: {getattr(a, 'name', f'app-{a.id}')}"
            )

    db_like = [
        a
        for a in apps
        if "db" in (getattr(a, "role", "") or "").lower()
        or "warehouse" in (getattr(a, "name", "") or "").lower()
    ]
    if db_like:
        opportunities.append("Move analytics and DB workloads to managed services.")

    complexity = 0.5
    complexity += min(len(blockers) * 0.05, 0.3)
    complexity += min(len(db_like) * 0.03, 0.2)

    complexity = max(0.0, min(1.0, complexity))

    return KeyInsights(
        top_blockers=blockers[:5],
        top_opportunities=opportunities[:5],
        risk_flags=list(set(risk_flags)),
        complexity_score=complexity,
    )


def _build_application_insights(apps: List["models.App"]) -> List[ApplicationInsight]:
    results = []

    for a in apps:
        name = getattr(a, "name", f"app-{a.id}")
        criticality = getattr(a, "criticality", "") or "Unclassified"
        architecture = (getattr(a, "architecture", "") or "").lower()

        risk_level = "Medium"
        if "monolith" in architecture:
            risk_level = "High"
        elif "micro" in architecture:
            risk_level = "Low"

        recommended_path = "Rehost"
        if "db" in name.lower() or "sql" in name.lower():
            recommended_path = "Replatform to managed database"

        notes = []
        notes.append(f"Criticality: {criticality}")
        if architecture:
            notes.append(f"Architecture: {architecture}")

        results.append(
            ApplicationInsight(
                name=name,
                business_tier=criticality,
                recommended_path=recommended_path,
                risk_level=risk_level,
                notes=" | ".join(notes),
            )
        )

    return results


def generate_intelligence_summary(db: Session, run_id: str) -> IntelligenceSummary:
    run = db.query(models.Run).filter(models.Run.id == run_id).first()
    if not run:
        raise ValueError(f"Run {run_id} not found")

    servers = db.query(models.Server).filter(models.Server.run_id == run_id).all()
    apps = db.query(models.App).filter(models.App.run_id == run_id).all()

    readiness = _compute_readiness_score(servers, apps)
    migration_rec = _build_migration_recommendation(readiness)
    key_insights = _build_key_insights(readiness, servers, apps)
    app_insights = _build_application_insights(apps)

    return IntelligenceSummary(
        run_id=str(run.id),
        org_name=getattr(run, "org_name", None),
        environment=getattr(run, "environment", None),
        overall_readiness=readiness,
        migration_recommendation=migration_rec,
        key_insights=key_insights,
        applications=app_insights,
    )
