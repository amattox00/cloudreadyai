from __future__ import annotations

from dataclasses import dataclass
from typing import List

from app.models.workload import Workload, Node


@dataclass
class PatternResult:
    """
    Result of classifying a workload into a high-level architecture pattern.
    Example pattern_ids:
      - "three_tier_web_app"
      - "data_platform"
      - "iot_edge"
      - "generic"
    """
    pattern_id: str
    confidence: float
    reasons: List[str]


def _count_roles(nodes: List[Node]) -> dict:
    counts: dict[str, int] = {}
    for n in nodes:
        counts[n.role] = counts.get(n.role, 0) + 1
    return counts


def infer_pattern(workload: Workload) -> PatternResult:
    """
    First version of the pattern engine.

    Later this can grow into:
      - multiple pattern matches
      - priority rules
      - data-driven pattern definitions
    """
    counts = _count_roles(workload.nodes)
    reasons: List[str] = []

    has_clients = counts.get("client", 0) > 0
    has_edge = counts.get("edge", 0) > 0
    has_app = counts.get("app", 0) > 0
    has_data = counts.get("data", 0) > 0

    if has_clients:
        reasons.append("Found at least one 'client' node")
    if has_edge:
        reasons.append("Found at least one 'edge' node")
    if has_app:
        reasons.append("Found at least one 'app' node")
    if has_data:
        reasons.append("Found at least one 'data' node")

    # Simple heuristic: typical 3-tier web app pattern
    if has_clients and has_edge and has_app and has_data:
        return PatternResult(
            pattern_id="three_tier_web_app",
            confidence=0.9,
            reasons=reasons,
        )

    # Fallback: generic pattern for now
    reasons.append("Did not match any specific pattern, using 'generic'")
    return PatternResult(
        pattern_id="generic",
        confidence=0.3,
        reasons=reasons,
    )
