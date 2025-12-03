from __future__ import annotations

from typing import Dict, Any, List
from collections import Counter

from sqlalchemy.orm import Session
from sqlalchemy import text


def _make_problem(
    code: str,
    severity: str,
    message: str,
    affected_rows: List[Dict[str, Any]],
    max_examples: int = 5,
) -> Dict[str, Any]:
    """
    Build a standardized problem record.
    """
    example_hosts = [
        r.get("hostname") or r.get("server_id")
        for r in affected_rows[:max_examples]
    ]

    return {
        "code": code,
        "severity": severity,  # "warning" or "error"
        "message": message,
        "count": len(affected_rows),
        "example_hosts": example_hosts,
    }


def analyze_servers_for_run(db: Session, run_id: str) -> Dict[str, Any]:
    """
    Analyze the servers slice for a given run_id and return a list of problems.

    Checks include:
      - Missing hostname
      - Missing / zero CPU
      - Missing / zero RAM
      - Missing environment
      - Missing OS
      - Duplicate hostnames within the run
    """

    rows = db.execute(
        text(
            """
            SELECT
              server_id,
              hostname,
              cpu_cores,
              ram_gb,
              os,
              environment,
              ip
            FROM servers
            WHERE run_id = :run_id
            """
        ),
        {"run_id": run_id},
    ).mappings().all()

    if not rows:
        return {
            "run_id": run_id,
            "rows_seen": 0,
            "problems": [],
            "summary": {"error_count": 0, "warning_count": 0},
        }

    problems: List[Dict[str, Any]] = []

    # --- Rule: missing hostname (critical) ---
    missing_hostname = [r for r in rows if not (r.get("hostname") or "").strip()]
    if missing_hostname:
        problems.append(
            _make_problem(
                code="missing_hostname",
                severity="error",
                message="Servers with no hostname recorded.",
                affected_rows=missing_hostname,
            )
        )

    # --- Rule: missing or zero CPU cores ---
    missing_cpu = [r for r in rows if r.get("cpu_cores") is None]
    if missing_cpu:
        problems.append(
            _make_problem(
                code="missing_cpu",
                severity="error",
                message="Servers with no CPU core count.",
                affected_rows=missing_cpu,
            )
        )

    zero_cpu = [r for r in rows if r.get("cpu_cores") == 0]
    if zero_cpu:
        problems.append(
            _make_problem(
                code="zero_cpu",
                severity="error",
                message="Servers with 0 CPU cores.",
                affected_rows=zero_cpu,
            )
        )

    # --- Rule: missing or zero RAM ---
    missing_ram = [r for r in rows if r.get("ram_gb") is None]
    if missing_ram:
        problems.append(
            _make_problem(
                code="missing_ram",
                severity="error",
                message="Servers with no RAM value (GB).",
                affected_rows=missing_ram,
            )
        )

    zero_ram = [r for r in rows if r.get("ram_gb") == 0]
    if zero_ram:
        problems.append(
            _make_problem(
                code="zero_ram",
                severity="error",
                message="Servers with 0 GB RAM.",
                affected_rows=zero_ram,
            )
        )

    # --- Rule: missing environment (warning) ---
    missing_env = [
        r for r in rows if not (r.get("environment") or "").strip()
    ]
    if missing_env:
        problems.append(
            _make_problem(
                code="missing_environment",
                severity="warning",
                message="Servers with no environment set (dev/prod/etc).",
                affected_rows=missing_env,
            )
        )

    # --- Rule: missing OS (warning) ---
    missing_os = [
        r for r in rows if not (r.get("os") or "").strip()
    ]
    if missing_os:
        problems.append(
            _make_problem(
                code="missing_os",
                severity="warning",
                message="Servers with no operating system recorded.",
                affected_rows=missing_os,
            )
        )

    # --- Rule: duplicate hostnames within the run (error) ---
    host_counter = Counter(
        (r.get("hostname") or "").strip().lower()
        for r in rows
        if (r.get("hostname") or "").strip()
    )
    dup_hosts = {h: c for h, c in host_counter.items() if c > 1}
    if dup_hosts:
        # Collect all rows with duplicated hostnames
        affected = [
            r
            for r in rows
            if (r.get("hostname") or "").strip().lower() in dup_hosts
        ]
        problems.append(
            _make_problem(
                code="duplicate_hostname",
                severity="error",
                message="Duplicate hostnames detected within this run.",
                affected_rows=affected,
            )
        )

    # Compute counts by severity
    error_count = sum(1 for p in problems if p["severity"] == "error")
    warning_count = sum(1 for p in problems if p["severity"] == "warning")

    return {
        "run_id": run_id,
        "rows_seen": len(rows),
        "problems": problems,
        "summary": {
            "error_count": error_count,
            "warning_count": warning_count,
        },
    }
