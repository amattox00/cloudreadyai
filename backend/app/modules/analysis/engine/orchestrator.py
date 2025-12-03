from sqlalchemy.orm import Session

from app.modules.analysis.engine.summary_engine import build_summary
from app.schemas.analysis import AnalysisRunSummary


def run_full_analysis(run_id: str, db: Session) -> AnalysisRunSummary:
    """
    Orchestrate the full analysis pipeline.

    For now, this just builds a dataset summary, but later we can add:
      - consolidation logic
      - R-Score
      - optimization recommendations, etc.
    """
    return build_summary(run_id, db)
