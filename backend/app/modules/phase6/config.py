from __future__ import annotations

import os
from typing import List

# Default to "hybrid": try live where implemented, fall back to mock
PHASE6_MODE: str = os.getenv("PHASE6_MODE", "hybrid").lower()

SUPPORTED_PROVIDERS: List[str] = ["aws", "azure", "gcp"]


def get_mode() -> str:
    """Return the current Phase 6 mode."""
    return PHASE6_MODE


def get_supported_providers() -> list[str]:
    """Return supported cloud providers."""
    return SUPPORTED_PROVIDERS
