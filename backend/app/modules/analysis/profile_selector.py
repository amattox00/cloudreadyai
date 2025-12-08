# backend/app/modules/analysis/profile_selector.py

from typing import Dict, List
from .profiles.registry import get_profile_config


def load_analysis_profile(profile_name: str) -> Dict:
    """
    Loads the selected analysis profile.
    Falls back to migration_readiness if not found.
    """
    return get_profile_config(profile_name)


def enforce_required_slices(profile_config: Dict, available_slices: List[str]) -> List[str]:
    """
    Check for missing slices based on the selected profile.
    Returns a list of missing slice names.
    """
    required = profile_config.get("required_slices", [])
    missing = [s for s in required if s not in available_slices]
    return missing


def get_weights(profile_config: Dict) -> Dict:
    """Return scoring weights to feed into R-Score or other scoring engines."""
    return profile_config.get("weights", {})
