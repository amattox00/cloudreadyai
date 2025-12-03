from sqlalchemy.orm import Session
from sqlalchemy import text


def get_server_summary(db: Session, run_id: str):
    """
    Return aggregated metrics for the servers slice of a single run.
    """
    sql = text("""
        SELECT
            COUNT(*) AS server_count,
            COALESCE(SUM(cpu_cores), 0) AS total_cpu,
            COALESCE(SUM(ram_gb), 0) AS total_ram_gb
        FROM servers
        WHERE run_id = :run_id;
    """)
    row = db.execute(sql, {"run_id": run_id}).mappings().first()

    # Distribution: environments
    sql_env = text("""
        SELECT environment, COUNT(*) AS count
        FROM servers
        WHERE run_id = :run_id
        GROUP BY environment;
    """)

    env_rows = db.execute(sql_env, {"run_id": run_id}).mappings().all()
    environments = {r["environment"] or "unknown": r["count"] for r in env_rows}

    # Distribution: operating system
    sql_os = text("""
        SELECT os, COUNT(*) AS count
        FROM servers
        WHERE run_id = :run_id
        GROUP BY os;
    """)

    os_rows = db.execute(sql_os, {"run_id": run_id}).mappings().all()
    os_dist = {r["os"] or "unknown": r["count"] for r in os_rows}

    return {
        "server_count": row["server_count"],
        "total_cpu": float(row["total_cpu"]),
        "total_ram_gb": float(row["total_ram_gb"]),
        "environment_distribution": environments,
        "os_distribution": os_dist,
    }


def get_run_summary(db: Session, run_id: str):
    """
    Master summary that merges all slices (servers, storage, networks, apps later).
    For now, servers are implemented. Other slices return placeholders.
    """

    server_summary = get_server_summary(db, run_id)

    return {
        "run_id": run_id,
        "slices": {
            "servers": {
                "ingested": server_summary["server_count"] > 0,
                "summary": server_summary,
            },
            "storage": {"ingested": False, "summary": {}},
            "networks": {"ingested": False, "summary": {}},
            "apps": {"ingested": False, "summary": {}},
        }
    }
