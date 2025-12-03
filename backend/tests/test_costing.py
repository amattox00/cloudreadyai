from app.cost.pricing import PricingCatalog
from app.cost.calculator import CostCalculator, WorkloadInput, Scenario

def test_baseline_estimate_smoke():
    pricing = PricingCatalog()
    calc = CostCalculator(pricing)
    w = WorkloadInput(
        name="app1", cloud="aws", region="any",
        vcpu=4, memory_gib=16.0, storage_gib=200, storage_class="standard",
        hours_per_month=100, egress_gib=50.0, ha_multiplier=1.0, dr_multiplier=1.0
    )
    s = Scenario(name="baseline")
    out = calc.estimate_scenario([w], s)
    assert out["total_monthly"] > 0
    assert out["items"][0]["breakdown"]["compute"] > 0
