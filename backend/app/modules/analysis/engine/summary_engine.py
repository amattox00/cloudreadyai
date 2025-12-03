from typing import Dict

from sqlalchemy.orm import Session
from sqlalchemy.exc import ProgrammingError

from app.models.server import Server
from app.models.database import Database
from app.models.analysis_run import AnalysisRun
from app.schemas.analysis import AnalysisRunSummary


def _safe_count(query) -> int:
    """
    Safely count rows, returning 0 if the underlying table/columns are broken.
    """
    try:
        return query.count()
    except ProgrammingError:
        return 0


def build_summary(run_id: str, db: Session) -> AnalysisRunSummary:
    """
    Build a foundational summary of the ingestion dataset for this run.

    For now, we ONLY look at servers and databases so that analysis
    works even if storage/network tables aren't fully wired yet.
    """

    # ---- Counts we are confident about -----------------
    server_count = _safe_count(db.query(Server).filter(Server.run_id == run_id))
    db_count = _safe_count(db.query(Database).filter(Database.run_id == run_id))

    # We will stub these for now until storage/network ingestion
    # schemas are confirmed.
    storage_count = 0
    network_count = 0

    counts: Dict[str, int] = {
        "servers": server_count,
        "databases": db_count,
        "storage_volumes": storage_count,
        "network_endpoints": network_count,
    }

    ingestion_complete = server_count > 0 and db_count > 0

    if ingestion_complete:
        status = "ok"
        dataset_health = "ok"
        notes = None
    else:
        status = "ingestion_incomplete"
        dataset_health = "warning"
        notes = (
            "Ingestion appears incomplete. Some core datasets (servers/databases) "
            "have zero rows."
        )

    summary = AnalysisRunSummary(
        run_id=run_id,
        status=status,
        dataset_health=dataset_health,
        counts=counts,
        notes=notes,
    )

    # ---- Try to persist to analysis_run table ----------
    try:
        analysis_row = (
            db.query(AnalysisRun).filter(AnalysisRun.run_id == run_id).one_or_none()
        )

        if analysis_row is None:
            analysis_row = AnalysisRun(
                run_id=run_id,
                summary_json=summary.model_dump(),
            )
            db.add(analysis_row)
        else:
            analysis_row.summary_json = summary.model_dump()

        db.commit()
        db.refresh(analysis_row)
    except ProgrammingError:
        # If the analysis_run table is somehow misaligned, we don't
        # want to break the endpoint — just return the in-memory summary.
        db.rollback()

    return summary
