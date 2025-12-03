from typing import Dict


class RScoreEngine:
    """
    Computes 6R recommendations and an overall R-Score profile for a server.

    This is a heuristic, rules-based engine designed to be:
    - easy to tweak later
    - deterministic (no randomness)
    """

    def compute(self, server_data: Dict) -> Dict:
        """
        Compute R-Score breakdown and final recommendation.

        Expected keys in server_data (all optional for now):
            - cpu_usage (float, percent)
            - ram_usage (float, percent)
            - os (str)
            - environment (str: prod/dev/test)
            - role (str: app/db/file/etc.)

        Returns a dict like:
        {
            "rehost": 35,
            "replatform": 60,
            "refactor": 20,
            "repurchase": 10,
            "retire": 5,
            "retain": 15,
            "final_recommendation": "REPLATFORM",
        }
        """
        cpu = float(server_data.get("cpu_usage") or 0.0)
        ram = float(server_data.get("ram_usage") or 0.0)
        os_name = (server_data.get("os") or "").lower()
        env = (server_data.get("environment") or "").lower()
        role = (server_data.get("role") or "").lower()

        # ------------------------------------------------------------------
        # Base scores (0-100). We'll adjust them using simple rules.
        # ------------------------------------------------------------------
        scores = {
            "rehost": 40.0,      # lift-and-shift default
            "replatform": 40.0,  # move + small improvements
            "refactor": 20.0,    # deep modernization
            "repurchase": 10.0,  # SaaS replacement
            "retire": 5.0,       # decommission
            "retain": 10.0,      # keep on-prem
        }

        # ------------------------------------------------------------------
        # Environment adjustments
        # ------------------------------------------------------------------
        if env == "prod":
            # Production workloads: bias against retire
            scores["retire"] -= 3
            scores["retain"] += 5
        elif env in ("dev", "test"):
            # Non-prod: easier to replatform/refactor or retire
            scores["replatform"] += 5
            scores["refactor"] += 10
            scores["retire"] += 5

        # ------------------------------------------------------------------
        # CPU / RAM utilization adjustments
        # ------------------------------------------------------------------
        # High utilization: refactor/replatform/rightsize
        if cpu > 80 or ram > 80:
            scores["replatform"] += 10
            scores["refactor"] += 5
            scores["rehost"] -= 5
        # Very low utilization: retire or consolidate (rehost/replatform with rightsizing)
        elif cpu < 10 and ram < 10:
            scores["retire"] += 10
            scores["rehost"] += 5
            scores["replatform"] += 5

        # Moderate utilization (typical lift-and-shift)
        elif 20 <= cpu <= 60 and 20 <= ram <= 60:
            scores["rehost"] += 5
            scores["replatform"] += 5

        # ------------------------------------------------------------------
        # OS-level modernization heuristic
        # ------------------------------------------------------------------
        legacy_os_keywords = ["2008", "2003", "xp", "rhel 5", "rhel 6", "centos 6"]
        modern_os_keywords = ["2019", "2022", "rhel 8", "rhel 9", "ubuntu 20", "ubuntu 22"]

        is_legacy_os = any(k in os_name for k in legacy_os_keywords)
        is_modern_os = any(k in os_name for k in modern_os_keywords)

        if is_legacy_os:
            # Legacy OS: refactor or repurchase more attractive
            scores["refactor"] += 15
            scores["repurchase"] += 10
            scores["rehost"] -= 10
            scores["retain"] -= 5
        elif is_modern_os:
            # Modern OS: rehost/replatform are safer
            scores["rehost"] += 5
            scores["replatform"] += 5

        # ------------------------------------------------------------------
        # Role-based hints
        # ------------------------------------------------------------------
        if "db" in role or "database" in role:
            # DB servers are great candidates for managed services replatforming
            scores["replatform"] += 10
            scores["refactor"] += 5
        elif "file" in role or "storage" in role:
            # File servers sometimes move to SaaS or object storage solutions
            scores["repurchase"] += 5
            scores["replatform"] += 5
        elif "app" in role or "web" in role:
            # App servers: refactor or replatform to containers, app services
            scores["refactor"] += 5
            scores["replatform"] += 5

        # ------------------------------------------------------------------
        # Normalization and final recommendation
        # ------------------------------------------------------------------
        # Clamp and normalize scores between 0 and 100
        for k in scores.keys():
            scores[k] = max(0.0, min(100.0, scores[k]))

        # Determine final recommendation based on highest score
        final_key = max(scores, key=scores.get)
        final_recommendation = final_key.upper()  # e.g., "REPLATFORM"

        scores["final_recommendation"] = final_recommendation
        return scores
