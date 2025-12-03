"""
Phase 4 Cost calculation engine.
- Multi-cloud (AWS/Azure/GCP)
- Right-sizing, commitments, HA/DR multipliers, burst
- Per-workload breakdown and scenario totals
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional
from .pricing import PricingCatalog

@dataclass
class WorkloadInput:
    name: str
    cloud: str  # aws|azure|gcp
    region: str
    vcpu: int
    memory_gib: float
    storage_gib: float
    storage_class: str  # standard|gp2|gp3|premium (toy)
    hours_per_month: int = 730
    egress_gib: float = 0.0
    ha_multiplier: float = 1.0   # 1.0=single-AZ; 2.0=active/standby; tune per policy
    dr_multiplier: float = 1.0   # >1.0 adds DR cost proportion

@dataclass
class Scenario:
    name: str  # baseline | right-sized | reserved | bursty | ha | dr
    commitment: Optional[str] = None  # "1yrRI"|"3yrRI"|"savings_plan"|None
    rightsize_factor: float = 1.0     # <1.0 to right-size compute/memory
    burst_percent: float = 0.0        # e.g., 0.1 = +10% hours
    notes: Optional[str] = None

class CostCalculator:
    def __init__(self, pricing: PricingCatalog):
        self.pricing = pricing

    def estimate_workload_monthly(self, w: WorkloadInput, scenario: Scenario) -> Dict:
        # Right-sizing
        vcpu = max(1, int(round(w.vcpu * scenario.rightsize_factor)))
        mem  = max(0.5, w.memory_gib * scenario.rightsize_factor)
        hours = w.hours_per_month * (1.0 + scenario.burst_percent)

        # Unit prices
        compute = self.pricing.lookup_compute(w.cloud, w.region, vcpu, mem, commitment=scenario.commitment)
        storage = self.pricing.lookup_storage(w.cloud, w.region, w.storage_class)
        egress  = self.pricing.lookup_egress(w.cloud, w.region)

        # Cost math
        compute_cost = compute.price_per_vcpu_hour * vcpu * hours + compute.price_per_gib_hour * mem * hours
        storage_cost = storage.price_per_gib_month * w.storage_gib
        egress_cost  = egress.price_per_gib * w.egress_gib

        # HA/DR multipliers
        compute_cost *= w.ha_multiplier * w.dr_multiplier
        storage_cost *= w.ha_multiplier * w.dr_multiplier

        total = compute_cost + storage_cost + egress_cost

        return {
            "workload": w.name,
            "cloud": w.cloud,
            "region": w.region,
            "scenario": scenario.name,
            "breakdown": {
                "compute": round(compute_cost, 4),
                "storage": round(storage_cost, 4),
                "egress": round(egress_cost, 4),
            },
            "total_monthly": round(total, 4),
            "assumptions": {
                "vcpu": vcpu, "memory_gib": round(mem,2), "hours": round(hours,2),
                "ha_multiplier": w.ha_multiplier, "dr_multiplier": w.dr_multiplier,
                "commitment": scenario.commitment, "rightsize_factor": scenario.rightsize_factor,
                "burst_percent": scenario.burst_percent
            }
        }

    def estimate_scenario(self, workloads: List[WorkloadInput], scenario: Scenario) -> Dict:
        items = [self.estimate_workload_monthly(w, scenario) for w in workloads]
        total = round(sum(i["total_monthly"] for i in items), 4)
        return {
            "scenario": scenario.name,
            "items": items,
            "total_monthly": total
        }
