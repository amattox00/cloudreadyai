# backend/app/modules/analysis_v2/profile_integration.py

from typing import Dict, List, Tuple

from app.models.analysis_run import AnalysisRun  # adjust if your model path is different
from app.modules.analysis.profile_selector import (
    load_analysis_profile,
    enforce_required_slices,
    get_weights,
)


def get_profile_for_run(run: AnalysisRun) -> Tuple[str, Dict]:
    """
    Resolve the analysis profile for a given run.
    Falls back to 'migration_readiness' if not set.
    """
    profile_name = getattr(run, "profile", None) or "migration_readiness"
    profile_config = load_analysis_profile(profile_name)
    return profile_name, profile_config


def evaluate_profile_requirements(profile_config: Dict, available_slices: List[str]) -> Dict:
    """
    Given a profile and available slices, compute:
      - missing_slices
      - weights (for scoring engines)
    """
    missing_slices = enforce_required_slices(profile_config, available_slices)
    weights = get_weights(profile_config)

    return {
        "missing_slices": missing_slices,
        "weights": weights,
    }
