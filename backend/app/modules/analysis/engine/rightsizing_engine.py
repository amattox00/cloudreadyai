from __future__ import annotations

from typing import Dict, Any


class RightsizingEngine:
    """
    Simple heuristic-based rightsizing engine.

    Uses CPU and RAM utilization to suggest:
      - DOWNSIZE: underutilized
      - KEEP: reasonably utilized
      - UPSCALE: heavily utilized

    This does NOT consider actual instance types yet; it's a
    utilization-based recommendation that we can later tie into
    cloud SKU catalogs.
    """

    def recommend(self, *, cpu_usage: float, ram_usage: float, storage_usage: float | None = None) -> Dict[str, Any]:
        cpu = float(cpu_usage or 0.0)
        ram = float(ram_usage or 0.0)
        storage = float(storage_usage or 0.0) if storage_usage is not None else 0.0

        # Use the higher of CPU/RAM as our primary signal
        primary_util = max(cpu, ram)

        if primary_util < 30.0:
            action = "DOWNSIZE"
            target_size = "small"
            rationale = "Low CPU/RAM utilization; candidate for downsizing."
        elif primary_util <= 75.0:
            action = "KEEP"
            target_size = "medium"
            rationale = "Moderate utilization; current sizing appears appropriate."
        else:
            action = "UPSCALE"
            target_size = "large"
            rationale = "High CPU/RAM utilization; consider upsizing."

        return {
            "current_cpu": cpu,
            "current_ram": ram,
            "current_storage": storage,
            "action": action,
            "target_size": target_size,
            "rationale": rationale,
        }
