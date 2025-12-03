#!/usr/bin/env bash
set -euo pipefail

REPO="${REPO:-/home/ec2-user/cloudreadyai}"
APP_DIR="$REPO/backend/app"
ROUTERS_DIR="$APP_DIR/routers"
MODULE_DIR="$APP_DIR/modules/phase8"
CONFIG_FILE="$APP_DIR/core/config.py"
MAIN_FILE="$APP_DIR/main.py"

echo "==> Phase 8 Installer: Modeling module (mock-ready)"

# --- 1) Ensure folders --------------------------------------------------------
mkdir -p "$MODULE_DIR"

# --- 2) Phase 8 module: __init__.py ------------------------------------------
cat > "$MODULE_DIR/__init__.py" << 'PY'
from .modeling import CostModeler
from .scenarios import list_scenarios, get_scenario, ScenarioResult
PY

# --- 3) Phase 8 module: modeling.py ------------------------------------------
cat > "$MODULE_DIR/modeling.py" << 'PY'
from pydantic import BaseModel
import os

PHASE8_MODE = os.getenv("PHASE8_MODE", "mock").lower()

class EstimateRequest(BaseModel):
    num_servers: int = 10
    storage_tb: float = 5.0
    monthly_bandwidth_tb: float = 1.0
    region: str = "us-east-1"

class EstimateResult(BaseModel):
    capex: float
    opex_monthly: float
    tco_12mo: float
    notes: str = "mock"

class CostModeler:
    def estimate(self, req: EstimateRequest) -> EstimateResult:
        if PHASE8_MODE == "mock":
            capex = round(100 * (req.num_servers / 10), 2)
            opex_monthly = round(200 + 10 * req.storage_tb + 5 * req.monthly_bandwidth_tb, 2)
            tco_12mo = round(capex + opex_monthly * 12, 2)
            return EstimateResult(capex=capex, opex_monthly=opex_monthly, tco_12mo=tco_12mo, notes="mock")
        else:
            capex = 0.0
            opex_monthly = 0.0
            tco_12mo = 0.0
            return EstimateResult(capex=capex, opex_monthly=opex_monthly, tco_12mo=tco_12mo, notes="live-placeholder")
PY

# --- 4) Phase 8 module: scenarios.py -----------------------------------------
cat > "$MODULE_DIR/scenarios.py" << 'PY'
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
PY

# --- 5) Router: phase8.py ----------------------------------------------------
mkdir -p "$ROUTERS_DIR"
cat > "$ROUTERS_DIR/phase8.py" << 'PY'
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os

from backend.app.modules.phase8 import CostModeler, list_scenarios, get_scenario, ScenarioResult
from backend.app.modules.phase8.modeling import EstimateRequest, EstimateResult

router = APIRouter(prefix="/v1/model", tags=["phase8-modeling"])

class WhatIfRequest(BaseModel):
    scenario: str

@router.get("/health")
def model_health():
    return {
        "phase": 8,
        "enabled": os.getenv("PHASE8_ENABLED", "true").lower() == "true",
        "mode": os.getenv("PHASE8_MODE", "mock"),
    }

@router.get("/scenarios", response_model=list[ScenarioResult])
def model_scenarios():
    return list_scenarios()

@router.post("/estimate", response_model=EstimateResult)
def model_estimate(req: EstimateRequest):
    modeler = CostModeler()
    return modeler.estimate(req)

@router.post("/whatif", response_model=ScenarioResult)
def model_whatif(req: WhatIfRequest):
    try:
        return get_scenario(req.scenario)  # type: ignore
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
PY

# --- 6) Env toggles in config -------------------------------------------------
if [ -f "$CONFIG_FILE" ]; then
  if ! grep -q "PHASE8_ENABLED" "$CONFIG_FILE"; then
    echo "Patching $CONFIG_FILE with Phase 8 settings..."
    cat >> "$CONFIG_FILE" << 'PY'

# ==== Phase 8 toggles ====
try:
    PHASE8_ENABLED = bool(os.getenv("PHASE8_ENABLED", "true").lower() == "true")
    PHASE8_MODE = os.getenv("PHASE8_MODE", "mock")
    PHASE8_DEFAULT_SCENARIO = os.getenv("PHASE8_DEFAULT_SCENARIO", "baseline")
except Exception:
    PHASE8_ENABLED = True
    PHASE8_MODE = "mock"
    PHASE8_DEFAULT_SCENARIO = "baseline"
PY
  fi
fi

# --- 7) Wire router into FastAPI main.py -------------------------------------
if ! grep -q "from backend.app.routers.phase8 import router as phase8_router" "$MAIN_FILE"; then
  sed -i '1,/^from /{x;}; $a from backend.app.routers.phase8 import router as phase8_router' "$MAIN_FILE"
fi
if ! grep -q "include_router(phase8_router" "$MAIN_FILE"; then
  sed -i 's/app = FastAPI([^)]*)/app = FastAPI()\napp.include_router(phase8_router)/' "$MAIN_FILE" || true
  if ! grep -q "include_router(phase8_router" "$MAIN_FILE"; then
    echo -e "\napp.include_router(phase8_router)" >> "$MAIN_FILE"
  fi
fi

# --- 8) .env hints (non-destructive) -----------------------------------------
if [ -f "$REPO/.env" ] && ! grep -q "PHASE8_ENABLED" "$REPO/.env"; then
  cat >> "$REPO/.env" << 'ENV'
# ===== Phase 8 (Modeling) =====
PHASE8_ENABLED=true
PHASE8_MODE=mock
PHASE8_DEFAULT_SCENARIO=baseline
ENV
fi

# --- 9) Git add/commit --------------------------------------------------------
cd "$REPO"
git add backend/app/modules/phase8 \
        backend/app/routers/phase8.py \
        backend/app/core/config.py 2>/dev/null || true
git add backend/app/modules 2>/dev/null || true
git add backend/app/main.py 2>/dev/null || true
git commit -m "Phase 8: Modeling module + router, env toggles (mock mode)" || true

# --- 10) Restart backend if managed by systemd -------------------------------
if systemctl list-units --full -all | grep -q "cloudready-backend.service"; then
  echo "Restarting cloudready-backend.service..."
  sudo systemctl restart cloudready-backend.service
  sudo systemctl --no-pager --full status cloudready-backend.service || true
else
  echo "NOTE: cloudready-backend.service not found. Start your backend manually if needed."
fi

echo "==> Phase 8 installer complete."
