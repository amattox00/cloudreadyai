from typing import List, Optional, Any, Dict

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.modules.analysis_v2.run_summary_v2 import RunSummaryV2, summarize_run_v2
from app.models.analysis_run import AnalysisRun


class RecommendationItem(BaseModel):
    """
    A single recommendation item, grouped into categories like:
      - right_size
      - migration_strategy
      - migration_waves
      - risk_mitigation
      - architecture
      - data_quality
    """

    category: str
    title: str
    rationale: str
    impact: Optional[str] = None
    priority: Optional[str] = None


class RecommendationsBundleV2(BaseModel):
    """
    Top-level recommendations payload for a run.
    """

    run_id: str
    profile: Optional[str] = None
    overall_notes: List[str] = []

    right_size: List[RecommendationItem] = []
    migration_strategy: List[RecommendationItem] = []
    migration_waves: List[RecommendationItem] = []
    risk_mitigation: List[RecommendationItem] = []
    architecture: List[RecommendationItem] = []
    data_quality: List[RecommendationItem] = []


def _get_profile_for_run(db: Session, run_id: str) -> Optional[str]:
    row = db.query(AnalysisRun).filter(AnalysisRun.run_id == run_id).one_or_none()
    return row.profile if row else None


def _as_dict(obj: Any) -> Dict[str, Any]:
    """
    Safely treat RunSummaryV2 nested structures as dict-like, whether they are
    Pydantic models or plain dicts.
    """
    if obj is None:
        return {}
    if isinstance(obj, dict):
        return obj
    if hasattr(obj, "model_dump"):
        return obj.model_dump()  # pydantic v2
    if hasattr(obj, "dict"):
        return obj.dict()  # pydantic v1
    return {}


def _get_overall_score(r_score_obj: Any) -> float:
    d = _as_dict(r_score_obj)
    try:
        return float(d.get("overall_score") or 0.0)
    except (TypeError, ValueError):
        return 0.0


def _get_overall_grade(r_score_obj: Any) -> str:
    d = _as_dict(r_score_obj)
    grade = d.get("overall_grade") or "F"
    return str(grade)


def generate_recommendations_for_run(
    run_id: str,
    db: Session,
) -> Optional[RecommendationsBundleV2]:
    """
    Generate a structured recommendations bundle for a run, based on:
      - RunSummaryV2 (totals, slices, R-Score, flags)
      - AnalysisRun.profile (selected analysis profile)

    This is intentionally rules-based and easy to tweak.
    """
    summary: Optional[RunSummaryV2] = summarize_run_v2(run_id=run_id, db=db)
    if summary is None:
        return None

    profile = _get_profile_for_run(db, run_id)
    slices = _as_dict(summary.slices)
    flags = list(summary.flags or [])
    r_score_obj = summary.r_score

    overall_score = _get_overall_score(r_score_obj)
    overall_grade = _get_overall_grade(r_score_obj)

    bundle = RecommendationsBundleV2(
        run_id=run_id,
        profile=profile,
        overall_notes=[],
        right_size=[],
        migration_strategy=[],
        migration_waves=[],
        risk_mitigation=[],
        architecture=[],
        data_quality=[],
    )

    # ------------------------------------------------------------------
    # Overall notes based on R-Score
    # ------------------------------------------------------------------
    if overall_score == 0:
        bundle.overall_notes.append(
            "R-Score is 0: this likely indicates limited or no data coverage for this run. "
            "Prioritize data ingestion and slice completeness before making firm recommendations."
        )
    elif overall_score < 40:
        bundle.overall_notes.append(
            f"Overall R-Score is {overall_score:.1f} (grade {overall_grade}): "
            "this environment has significant uncertainty. Focus first on data quality and "
            "stabilization before aggressive modernization."
        )
    elif overall_score < 70:
        bundle.overall_notes.append(
            f"Overall R-Score is {overall_score:.1f} (grade {overall_grade}): "
            "the environment is moderately well-understood. A phased migration with careful "
            "dependency analysis is recommended."
        )
    else:
        bundle.overall_notes.append(
            f"Overall R-Score is {overall_score:.1f} (grade {overall_grade}): "
            "data coverage and dependency clarity are strong. You can confidently pursue "
            "modernization and optimization patterns."
        )

    # ------------------------------------------------------------------
    # Data Quality / Slice Completeness Recommendations
    # ------------------------------------------------------------------
    servers = int(slices.get("servers", 0) or 0)
    utilization = int(slices.get("utilization", 0) or 0)
    dependencies = int(slices.get("dependencies", 0) or 0)
    applications = int(slices.get("applications", 0) or 0)
    databases = int(slices.get("databases", 0) or 0)
    networks = int(slices.get("networks", 0) or 0)

    if "LIMITED_DATA_COVERAGE" in flags or servers == 0:
        bundle.data_quality.append(
            RecommendationItem(
                category="data_quality",
                title="Ingest core server inventory before detailed planning",
                rationale=(
                    "R-Score flags limited data coverage and no servers are present in the v2 slices. "
                    "Without server inventory, CloudReadyAI cannot provide accurate migration sizing, "
                    "waves, or risk insights."
                ),
                impact="High impact on all downstream recommendations (TCO, right-sizing, waves).",
                priority="P0",
            )
        )

    if servers > 0 and utilization == 0:
        bundle.data_quality.append(
            RecommendationItem(
                category="data_quality",
                title="Enable utilization collection for right-sizing accuracy",
                rationale=(
                    f"{servers} servers are present but no utilization datapoints were found. "
                    "CPU/RAM/storage utilization is required for precise right-sizing and cost optimization."
                ),
                impact="Directly impacts cost optimization and rightsizing quality.",
                priority="P1",
            )
        )

    if applications > 0 and dependencies == 0:
        bundle.data_quality.append(
            RecommendationItem(
                category="data_quality",
                title="Ingest application dependency mappings",
                rationale=(
                    f"{applications} applications were discovered but no dependency links are present. "
                    "Without dependencies, migration waves and blast-radius analysis are less reliable."
                ),
                impact="Impacts migration wave grouping and cutover risk.",
                priority="P1",
            )
        )

    if databases > 0 and dependencies == 0:
        bundle.data_quality.append(
            RecommendationItem(
                category="data_quality",
                title="Link applications and databases via dependency data",
                rationale=(
                    f"{databases} databases exist, but no app-to-DB dependencies were found. "
                    "This obscures database migration patterns (rehost vs managed DB vs refactor)."
                ),
                impact="Impacts DB migration strategy and downtime planning.",
                priority="P1",
            )
        )

    if networks == 0:
        bundle.data_quality.append(
            RecommendationItem(
                category="data_quality",
                title="Add network topology and segmentation data",
                rationale=(
                    "No network slice records found. Network segments, subnets, and sites are useful for "
                    "defining landing zones, security boundaries, and interconnect patterns."
                ),
                impact="Impacts architecture and security design recommendations.",
                priority="P2",
            )
        )

    # ------------------------------------------------------------------
    # Right-size Recommendations (high-level, slice-driven)
    # ------------------------------------------------------------------
    if servers > 0 and utilization > 0:
        bundle.right_size.append(
            RecommendationItem(
                category="right_size",
                title="Run detailed rightsizing against utilization data",
                rationale=(
                    f"{servers} servers and {utilization} utilization datapoints detected. "
                    "This is sufficient to generate concrete instance-family and size recommendations."
                ),
                impact="Can reduce cloud run-rate by optimizing vCPU/RAM/storage footprints.",
                priority="P1",
            )
        )
    elif servers > 0 and utilization == 0:
        bundle.right_size.append(
            RecommendationItem(
                category="right_size",
                title="Use conservative lift-and-shift sizing until utilization is available",
                rationale=(
                    f"{servers} servers are present but utilization is missing. "
                    "Recommend starting with like-for-like sizing with modest downsize assumptions "
                    "(e.g., 10–20% where safe) instead of aggressive rightsizing."
                ),
                impact="Reduces risk of under-sizing critical workloads.",
                priority="P2",
            )
        )

    # ------------------------------------------------------------------
    # Migration Strategy Suggestions (5R / 6R level)
    # ------------------------------------------------------------------
    if overall_score < 40:
        bundle.migration_strategy.append(
            RecommendationItem(
                category="migration_strategy",
                title="Favor conservative Rehost/Replatform in early waves",
                rationale=(
                    f"Overall R-Score {overall_score:.1f} (grade {overall_grade}) indicates incomplete "
                    "visibility. Recommend prioritizing Rehost/Replatform patterns until data quality "
                    "improves for deeper refactoring decisions."
                ),
                impact="Reduces early-phase risk while still moving workloads to cloud.",
                priority="P0",
            )
        )
    elif overall_score < 70:
        bundle.migration_strategy.append(
            RecommendationItem(
                category="migration_strategy",
                title="Blend Rehost/Replatform with targeted Refactor opportunities",
                rationale=(
                    f"Overall R-Score {overall_score:.1f} (grade {overall_grade}) indicates moderate "
                    "clarity. It is safe to pursue focused refactoring (e.g., app services/containers) "
                    "for low-risk workloads while rehosting complex or high-risk systems."
                ),
                impact="Balances modernization benefits with delivery risk.",
                priority="P1",
            )
        )
    else:
        bundle.migration_strategy.append(
            RecommendationItem(
                category="migration_strategy",
                title="Pursue aggressive modernization for suitable workloads",
                rationale=(
                    f"Overall R-Score {overall_score:.1f} (grade {overall_grade}) suggests strong "
                    "understanding of the environment. You can confidently evaluate managed services, "
                    "serverless, and container refactor patterns for many workloads."
                ),
                impact="Maximizes long-term agility and cost optimization.",
                priority="P1",
            )
        )

    # ------------------------------------------------------------------
    # Migration Waves (more granular when deps exist)
    # ------------------------------------------------------------------
    if servers > 0:
        # Generic guidance when we at least know server counts
        bundle.migration_waves.append(
            RecommendationItem(
                category="migration_waves",
                title="Define migration waves by business criticality and environment",
                rationale=(
                    "Group workloads into waves based on business impact (non-prod vs prod, "
                    "low vs high criticality) and environment (dev/test vs prod). "
                    "Even before full dependency data, this lowers cutover risk."
                ),
                impact="Reduces blast radius of each cutover and improves rollback options.",
                priority="P2",
            )
        )

    if servers > 0 and dependencies > 0:
        # More advanced guidance when we have dependency data
        bundle.migration_waves.append(
            RecommendationItem(
                category="migration_waves",
                title="Use dependency clusters to drive migration waves",
                rationale=(
                    "Server and dependency slices are populated. CloudReadyAI can now cluster "
                    "tightly-coupled workloads into affinity groups (e.g., app tiers + their databases) "
                    "and build migration waves that minimize cross-wave dependencies."
                ),
                impact="Enables safer, dependency-aware migrations with fewer surprises at cutover.",
                priority="P1",
            )
        )

    # ------------------------------------------------------------------
    # Risk Mitigation Actions
    # ------------------------------------------------------------------
    if "LIMITED_DATA_COVERAGE" in flags:
        bundle.risk_mitigation.append(
            RecommendationItem(
                category="risk_mitigation",
                title="Treat all recommendations as preliminary until data coverage improves",
                rationale=(
                    "The LIMITED_DATA_COVERAGE flag indicates incomplete slices for this run. "
                    "Document recommendations as preliminary and schedule a follow-up assessment "
                    "after improving ingestion coverage."
                ),
                impact="Prevents over-committing to plans based on partial information.",
                priority="P0",
            )
        )

    if dependencies == 0 and applications > 0:
        bundle.risk_mitigation.append(
            RecommendationItem(
                category="risk_mitigation",
                title="Avoid splitting multi-tier apps across waves without dependency data",
                rationale=(
                    "Without dependency links, it is easy to accidentally place app tiers or "
                    "app/DB pairs into different waves. This can increase downtime risk and complexity."
                ),
                impact="Reduces unexpected outages caused by partial migrations.",
                priority="P1",
            )
        )

    # ------------------------------------------------------------------
    # Architecture Guidance (profile-aware where possible)
    # ------------------------------------------------------------------
    if profile == "migration_readiness":
        bundle.architecture.append(
            RecommendationItem(
                category="architecture",
                title="Start with a standardized landing zone before large-scale cutovers",
                rationale=(
                    "For migration readiness assessments, a consistent landing zone (network, identity, "
                    "security baselines) is critical. Ensure core cloud foundations are in place before "
                    "moving production workloads."
                ),
                impact="Reduces rework and improves security posture during migration.",
                priority="P0",
            )
        )
    elif profile == "cost_optimization":
        bundle.architecture.append(
            RecommendationItem(
                category="architecture",
                title="Prioritize architectures that enable autoscaling and rightsizing",
                rationale=(
                    "Under a cost optimization lens, focus on architectures (e.g., autoscaling groups, "
                    "managed databases, storage tiering) that align resource consumption with demand."
                ),
                impact="Directly supports ongoing FinOps and cloud cost management.",
                priority="P1",
            )
        )
    elif profile == "modernization":
        bundle.architecture.append(
            RecommendationItem(
                category="architecture",
                title="Target managed and serverless services where feasible",
                rationale=(
                    "For modernization-focused assessments, look for workloads that can move to "
                    "managed databases, container platforms, and serverless runtimes instead of "
                    "straight VM rehosts."
                ),
                impact="Improves agility, maintainability, and long-term O&M costs.",
                priority="P1",
            )
        )
    elif profile == "operational_risk":
        bundle.architecture.append(
            RecommendationItem(
                category="architecture",
                title="Standardize HA/DR patterns and backup coverage",
                rationale=(
                    "Under an operational risk lens, the focus should be on consistent patterns for "
                    "high availability, disaster recovery, and validated backup/restore paths."
                ),
                impact="Reduces outage risk and improves recoverability.",
                priority="P0",
            )
        )

    return bundle
