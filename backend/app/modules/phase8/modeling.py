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
