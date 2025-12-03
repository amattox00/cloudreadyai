from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List
from pathlib import Path
import csv

@dataclass
class PriceRow:
    cloud: str
    service: str
    region: str
    metric: str
    unit: str
    price: float
    meta: str = ""

class PricingCatalog:
    """
    Loads simple CSV pricing tables from pricing_tables/.
    Replace with real SKU catalogs or cloud price APIs as needed.
    """
    def __init__(self):
        self.rows: List[PriceRow] = []
        self._load_csvs()

    def _load_csvs(self):
        base = Path(__file__).parent / "pricing_tables"
        for name in ["aws.csv", "azure.csv", "gcp.csv"]:
            p = base / name
            if not p.exists():
                continue
            with p.open("r", newline="") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    self.rows.append(PriceRow(
                        cloud=r["cloud"], service=r["service"], region=r["region"],
                        metric=r["metric"], unit=r["unit"], price=float(r["price"]), meta=r.get("meta","")
                    ))

    def _find(self, cloud: str, region: str, service: str, metric: str) -> PriceRow:
        candidates = [r for r in self.rows if r.cloud==cloud and r.region==region and r.service==service and r.metric==metric]
        if not candidates:
            candidates = [r for r in self.rows if r.cloud==cloud and r.region=="any" and r.service==service and r.metric==metric]
        if not candidates:
            raise ValueError(f"No price for {cloud}/{region}/{service}/{metric}")
        return candidates[0]

    def lookup_compute(self, cloud: str, region: str, vcpu: int, mem_gib: float, commitment: Optional[str]=None):
        # Toy commitment discounts. Tune or replace with real schedules.
        discount = {"1yrRI": 0.75, "3yrRI": 0.6, "savings_plan": 0.7}.get(commitment, 1.0)
        vcpu_row = self._find(cloud, region, "compute", "vcpu_hour")
        mem_row  = self._find(cloud, region, "compute", "gib_hour")
        class Obj:
            price_per_vcpu_hour = vcpu_row.price * discount
            price_per_gib_hour  = mem_row.price  * discount
        return Obj

    def lookup_storage(self, cloud: str, region: str, storage_class: str):
        metric = {
            "gp2": "gp2_gib_month",
            "gp3": "gp3_gib_month",
            "standard": "standard_gib_month",
            "premium": "premium_gib_month",
        }.get(storage_class, "standard_gib_month")
        row = self._find(cloud, region, "storage", metric)
        class Obj:
            price_per_gib_month = row.price
        return Obj

    def lookup_egress(self, cloud: str, region: str):
        row = self._find(cloud, region, "network", "egress_gib")
        class Obj:
            price_per_gib = row.price
        return Obj
