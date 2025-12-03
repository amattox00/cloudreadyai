from typing import Dict, List, Literal
from pydantic import BaseModel

ScenarioName = Literal["baseline","rehost_aws","refactor_azure","replatform_gcp"]

_SCENARIOS: Dict[ScenarioName, Dict[str, float]] = {
    "baseline":       {"capex": 100.00, "opex_monthly": 75.00,  "tco_12mo": 100.00 + 12*75.00},
    "rehost_aws":     {"capex":  80.00, "opex_monthly": 68.33,  "tco_12mo":  80.00 + 12*68.33},
    "refactor_azure": {"capex":  60.00, "opex_monthly": 66.67,  "tco_12mo":  60.00 + 12*66.67},
    "replatform_gcp": {"capex":  50.00, "opex_monthly": 62.50,  "tco_12mo":  50.00 + 12*62.50},
}

class ScenarioResult(BaseModel):
    name: ScenarioName
    capex: float
    opex_monthly: float
    tco_12mo: float

def _round_money(x: float) -> float:
    return float(f"{x:.2f}")

def list_scenarios() -> List[ScenarioResult]:
    out: List[ScenarioResult] = []
    for k, v in _SCENARIOS.items():
        out.append(ScenarioResult(
            name=k, capex=_round_money(v["capex"]),
            opex_monthly=_round_money(v["opex_monthly"]),
            tco_12mo=_round_money(v["tco_12mo"]),
        ))
    return out

def get_scenario(name: ScenarioName) -> ScenarioResult:
    if name not in _SCENARIOS:
        raise KeyError(f"Unknown scenario: {name}")
    v = _SCENARIOS[name]
    return ScenarioResult(
        name=name,
        capex=_round_money(v["capex"]),
        opex_monthly=_round_money(v["opex_monthly"]),
        tco_12mo=_round_money(v["tco_12mo"]),
    )
