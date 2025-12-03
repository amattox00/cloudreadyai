from __future__ import annotations

from typing import Dict, Any
from collections import Counter

from sqlalchemy.orm import Session
from sqlalchemy import text


def _normalize_environment(env: str | None) -> str | None:
    if not env:
        return None
    s = env.strip().lower()

    if s in {"prod", "prd", "production", "live"}:
        return "production"
    if s in {"dev", "development", "sandbox"}:
        return "development"
    if s in {"qa", "test", "testing", "staging", "stage", "uat", "preprod"}:
        return "non-production"

    # Default: just return the lowercased original
    return s


def _normalize_os(os_name: str | None) -> str | None:
    if not os_name:
        return None

    s = os_name.strip().lower()

    # Basic examples; we can expand this over time
    if "windows" in s and "2019" in s:
        return "Windows Server 2019"
    if "windows" in s and "2016" in s:
        return "Windows Server 2016"
    if "windows" in s and "2022" in s:
        return "Windows Server 2022"
    if "ubuntu" in s and "22.04" in s:
        return "Ubuntu 22.04 LTS"
    if "ubuntu" in s and "20.04" in s:
        return "Ubuntu 20.04 LTS"
    if "rhel" in s or "red hat" in s:
        return "Red Hat Enterprise Linux"
    if "centos" in s:
        return "CentOS"
    if "suse" in s:
        return "SUSE Linux"

    # Default: title-case the original
    return os_name.strip().title()


def normalize_servers_for_run(db: Session, run_id: str) -> Dict[str, Any]:
    """
    Normalize server metadata for a given run_id.

    - Normalizes environment strings (prod/dev/qa/etc).
    - Normalizes OS names (basic patterns).
    - Optionally ensures RAM fields are consistent.
    - Returns a summary of changes.
    """

    # Pull all servers for this run_id
    rows = db.execute(
        text(
            """
            SELECT
              server_id,
              hostname,
              environment,
              os,
              memory_gb,
              ram_gb
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
            "rows_updated": 0,
            "env_counts": {},
            "os_counts": {},
        }

    env_before = Counter()
    os_before = Counter()
    env_after = Counter()
    os_after = Counter()

    updates: list[Dict[str, Any]] = []

    for row in rows:
        server_id = row["server_id"]
        hostname = row["hostname"]
        env = row["environment"]
        os_name = row["os"]
        memory_gb = row["memory_gb"]
        ram_gb = row["ram_gb"]

        env_before[env or ""] += 1
        os_before[os_name or ""] += 1

        new_env = _normalize_environment(env)
        new_os = _normalize_os(os_name) if os_name else None

        # If ram_gb is null but memory_gb has a value, fill it
        new_ram_gb = ram_gb
        if new_ram_gb is None and memory_gb is not None:
            new_ram_gb = float(memory_gb)

        # Determine if anything actually changed
        changed = False
        if new_env != env:
            changed = True
        if new_os != os_name and new_os is not None:
            changed = True
        if new_ram_gb != ram_gb:
            changed = True

        if changed:
            updates.append(
                {
                    "server_id": server_id,
                    "environment": new_env,
                    "os": new_os,
                    "ram_gb": new_ram_gb,
                }
            )

        env_after[new_env or ""] += 1
        os_after[new_os or os_name or ""] += 1

    rows_updated = 0

    # Apply updates in a transaction
    if updates:
        for u in updates:
            db.execute(
                text(
                    """
                    UPDATE servers
                    SET
                      environment = :environment,
                      os = COALESCE(:os, os),
                      ram_gb = :ram_gb
                    WHERE server_id = :server_id
                    """
                ),
                u,
            )
        db.commit()
        rows_updated = len(updates)

    return {
        "run_id": run_id,
        "rows_seen": len(rows),
        "rows_updated": rows_updated,
        "env_counts_before": dict(env_before),
        "env_counts_after": dict(env_after),
        "os_counts_before": dict(os_before),
        "os_counts_after": dict(os_after),
    }
