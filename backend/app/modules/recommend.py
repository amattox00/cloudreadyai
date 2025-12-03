from typing import Dict, Any

# Minimal decision engine: uses cost (if provided) + simple tie-breakers.
# Inputs:
#   - matches: output from matching.match_services
#   - costs: { provider: { 'monthly_total': float } }
#   - constraints: { region, compliance, windows_bias, analytics_bias }

def recommend(matches: Dict[str, Any], costs: Dict[str, Any], constraints: Dict[str, Any] | None = None) -> Dict[str, Any]:
    constraints = constraints or {}
    # 1) Prefer lowest cost
    best = None
    best_p = None
    for p, v in costs.items():
        mt = float(v.get('monthly_total', 9e18))
        if best is None or mt < best:
            best = mt
            best_p = p

    # 2) Biasing rules (very simplified)
    if constraints.get('windows_bias'):
        best_p = 'Azure'
    if constraints.get('analytics_bias'):
        best_p = 'GCP'

    return {
        'recommended_provider': best_p or 'AWS',
        'explanation': 'Selected by lowest monthly_total with simple bias rules.',
        'match': matches.get(best_p or 'AWS'),
        'cost': costs.get(best_p or 'AWS'),
    }
