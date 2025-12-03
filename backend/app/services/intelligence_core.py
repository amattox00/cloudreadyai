from typing import List, Dict, Tuple

from sqlalchemy.orm import Session

from app.models.intelligence import (
    WorkloadFingerprint,
    ReadinessScore,
    MigrationRecommendation,
)


# ----------------- FINGERPRINTING ----------------- #


def build_fingerprints_for_run(db: Session, run_id: str) -> List[WorkloadFingerprint]:
    """
    Minimal, safe implementation:

    - Does NOT depend on any other models (servers, workloads, etc.).
    - Creates a single "summary workload" for the run, using the run_id as workload_id.
    - All metrics are left as NULL and profiles are set to 'unknown'.

    This guarantees the intelligence endpoints work even before
    we wire in real per-server metrics.
    """

    # Clear any previous fingerprints for idempotency
    db.query(WorkloadFingerprint).filter(WorkloadFingerprint.run_id == run_id).delete(
        synchronize_session=False
    )

    fp = WorkloadFingerprint(
        workload_id=run_id,
        run_id=run_id,
        avg_cpu_pct=None,
        peak_cpu_pct=None,
        avg_mem_pct=None,
        peak_mem_pct=None,
        avg_disk_read_iops=None,
        avg_disk_write_iops=None,
        avg_disk_latency_ms=None,
        avg_net_in_kbps=None,
        avg_net_out_kbps=None,
        cpu_profile="unknown",
        mem_profile="unknown",
        storage_profile="unknown",
        role=None,
        risk_flags=[],
        optimization_flags=[],
    )

    db.add(fp)
    db.commit()
    db.refresh(fp)

    return [fp]


# ----------------- SCORING ----------------- #


def _default_subscores_for_run(run_id: str) -> Tuple[int, int, int, int, int]:
    """
    Cheap heuristic just to return something stable and non-zero.
    You can tune this later or base it on real metrics.
    """
    compute = 80
    storage = 80
    network = 85
    app_cx = 75
    security = 90
    return compute, storage, network, app_cx, security


def build_scores_for_run(db: Session, run_id: str) -> List[ReadinessScore]:
    """
    Builds readiness scores based on the fingerprints we have.

    With the current minimal implementation, this simply assigns
    a single score bundle to the synthetic fingerprint we create per run.
    """

    # Clear previous scores for idempotency
    db.query(ReadinessScore).filter(ReadinessScore.run_id == run_id).delete(
        synchronize_session=False
    )

    fps: List[WorkloadFingerprint] = (
        db.query(WorkloadFingerprint)
        .filter(WorkloadFingerprint.run_id == run_id)
        .all()
    )

    # If there are no fingerprints yet, create them first
    if not fps:
        fps = build_fingerprints_for_run(db, run_id)

    results: List[ReadinessScore] = []

    for fp in fps:
        compute, storage, network, app_cx, security = _default_subscores_for_run(
            fp.run_id
        )

        total = round(
            compute * 0.25
            + storage * 0.20
            + network * 0.20
            + app_cx * 0.20
            + security * 0.15
        )

        score = ReadinessScore(
            workload_id=fp.workload_id,
            run_id=fp.run_id,
            total_score=total,
            compute_score=compute,
            storage_score=storage,
            network_score=network,
            app_complexity_score=app_cx,
            security_risk_score=security,
            notes=None,
        )

        db.add(score)
        results.append(score)

    db.commit()
    return results


# ----------------- RECOMMENDATIONS ----------------- #


def _strategy_from_score(total_score: int) -> Tuple[str, float, List[str]]:
    """
    Very simple strategy mapping based on total score.
    """
    notes: List[str] = []

    if total_score >= 80:
        notes.append("High readiness; straightforward lift-and-shift is viable.")
        return "rehost", 0.9, notes

    if 60 <= total_score < 80:
        notes.append("Moderate readiness; consider managed services to optimize.")
        return "replatform", 0.8, notes

    if 40 <= total_score < 60:
        notes.append("Lower readiness; application changes may be required.")
        return "refactor", 0.7, notes

    notes.append("Not a good candidate for migration as-is; consider retain/retire.")
    return "retain", 0.6, notes


def build_recommendations_for_run(
    db: Session, run_id: str
) -> List[MigrationRecommendation]:
    """
    Builds migration recommendations from readiness scores.
    """

    # Clear previous recs for idempotency
    db.query(MigrationRecommendation).filter(
        MigrationRecommendation.run_id == run_id
    ).delete(synchronize_session=False)

    scores: List[ReadinessScore] = (
        db.query(ReadinessScore).filter(ReadinessScore.run_id == run_id).all()
    )

    # If there are no scores yet, create them first
    if not scores:
        scores = build_scores_for_run(db, run_id)

    results: List[MigrationRecommendation] = []

    for s in scores:
        strategy, confidence, rationale = _strategy_from_score(s.total_score)

        rec = MigrationRecommendation(
            workload_id=s.workload_id,
            run_id=s.run_id,
            recommended_strategy=strategy,
            confidence=confidence,
            rationale=rationale,
            alternative_strategies=[],
        )

        db.add(rec)
        results.append(rec)

    db.commit()
    return results


# ----------------- SUMMARY ----------------- #


def get_intelligence_summary_for_run(db: Session, run_id: str) -> Dict:
    """
    Returns a summary dict for a run, suitable for both:
    - GET /v1/intelligence/{run_id}/summary
    - GET /v1/runs/{run_id}/analysis (as the intelligence block)
    """

    scores: List[ReadinessScore] = (
        db.query(ReadinessScore).filter(ReadinessScore.run_id == run_id).all()
    )

    if not scores:
        # Caller (router) can decide whether to 404
        return {}

    total = sum(s.total_score for s in scores)
    avg_readiness = total / max(len(scores), 1)

    recs: List[MigrationRecommendation] = (
        db.query(MigrationRecommendation)
        .filter(MigrationRecommendation.run_id == run_id)
        .all()
    )

    strategy_counts: Dict[str, int] = {}
    for r in recs:
        strategy_counts[r.recommended_strategy] = (
            strategy_counts.get(r.recommended_strategy, 0) + 1
        )

    summary: Dict = {
        "run_id": run_id,
        "avg_readiness": float(avg_readiness),
        "workload_count": len(scores),
        "strategy_counts": strategy_counts,
        "top_risks": [],
        "top_optimizations": [],
    }

    return summary
