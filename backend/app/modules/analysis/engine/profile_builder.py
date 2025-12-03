from typing import Optional, List, Dict

from sqlalchemy.orm import Session
from sqlalchemy import text

from app.modules.analysis.models.server_profile import ServerProfile


class ProfileBuilder:
    """
    Builds derived ServerProfile rows from existing ingestion tables.

    Priority:
      1. inventory_servers_v2 (new v2 ingestion path)
      2. inventory_servers
      3. servers

    This is designed to be defensive and flexible:
    - It will try a set of candidate source tables in order
    - It introspects column names to map server_id, os, environment, cpu, ram, role
    - If metrics like CPU/RAM utilization are missing, it will default to 0.
    """

    CANDIDATE_TABLES = [
        "inventory_servers_v2",
        "inventory_servers",
        "servers",
    ]

    def _detect_source_table(self, db: Session) -> Optional[str]:
        """
        Try to find which candidate table actually exists in the database.
        Uses Postgres to_regclass() to check existence.
        """
        for table in self.CANDIDATE_TABLES:
            result = db.execute(
                text("SELECT to_regclass(:tname)"), {"tname": table}
            ).scalar()
            if result is not None:
                return table
        return None

    def _get_columns(self, db: Session, table_name: str) -> List[str]:
        """
        Return list of column names for the given table, in lower-case.
        """
        rows = db.execute(
            text(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = :tname
                """
            ),
            {"tname": table_name},
        ).fetchall()
        return [row[0].lower() for row in rows]

    def _select_rows(self, db: Session, table_name: str, run_id: str) -> List[Dict]:
        """
        Select all rows from the source table for the given run_id.
        Assumes there is a column named 'run_id' on that table.
        """
        result = db.execute(
            text(f"SELECT * FROM {table_name} WHERE run_id = :run_id"),
            {"run_id": run_id},
        )
        return list(result.mappings())

    def _map_server_fields(self, row: Dict, columns: List[str]) -> Dict:
        """
        Map a raw ingestion row into the fields we need for ServerProfile.

        We do this by trying common column name patterns, so this function
        stays robust even if the ingestion schema is slightly different.
        """
        cols = {c.lower() for c in columns}

        def pick(*names: str) -> Optional[str]:
            for name in names:
                if name.lower() in cols:
                    return str(row.get(name))
            return None

        # server_id: hostname or server_name or name or server_id or id
        server_id = (
            pick("hostname", "server_name", "name", "server_id")
            or str(row.get("id"))
        )

        # OS
        os_value = pick("os", "os_name", "os_version", "operating_system")

        # environment
        environment = pick("environment", "env", "tier")

        # role (if exists)
        role = pick("role", "server_role", "function")

        # CPU/RAM utilization — try several possibilities, default to 0.0
        def pick_float(*names: str) -> float:
            for name in names:
                if name.lower() in cols:
                    raw = row.get(name)
                    if raw is None:
                        continue
                    try:
                        return float(raw)
                    except (TypeError, ValueError):
                        continue
            return 0.0

        cpu_usage = pick_float("cpu_usage", "avg_cpu", "cpu_percent", "cpu_utilization")
        ram_usage = pick_float("ram_usage", "avg_ram", "ram_percent", "memory_utilization")
        storage_usage = pick_float("storage_usage", "disk_usage", "disk_percent")

        return {
            "server_id": server_id,
            "os": os_value,
            "environment": environment,
            "role": role,
            "cpu_usage": cpu_usage,
            "ram_usage": ram_usage,
            "storage_usage": storage_usage,
        }

    def build_server_profiles(self, db: Session, run_id: str) -> int:
        """
        Main entrypoint:

        - Detects source table
        - Introspects its columns
        - Reads rows for that run_id
        - Deletes existing ServerProfile rows for that run_id
        - Inserts fresh ServerProfile rows
        - Returns count of inserted rows
        """
        source_table = self._detect_source_table(db)
        if not source_table:
            # No known ingestion table found; don't blow up, just return 0
            return 0

        columns = self._get_columns(db, source_table)
        rows = self._select_rows(db, source_table, run_id)

        # Clear existing profiles for this run
        db.query(ServerProfile).filter(ServerProfile.run_id == run_id).delete()

        count = 0

        for row in rows:
            mapped = self._map_server_fields(row, columns)

            if not mapped.get("server_id"):
                # Skip rows that we can't uniquely identify
                continue

            profile = ServerProfile(
                run_id=run_id,
                server_id=mapped["server_id"],
                role=mapped.get("role"),
                cpu_usage=mapped.get("cpu_usage") or 0.0,
                ram_usage=mapped.get("ram_usage") or 0.0,
                storage_usage=mapped.get("storage_usage") or 0.0,
                os=mapped.get("os"),
                environment=mapped.get("environment"),
            )
            db.add(profile)
            count += 1

        db.commit()
        return count
