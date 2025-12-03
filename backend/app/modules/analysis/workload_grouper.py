from typing import Dict, List

from sqlalchemy.orm import Session

from app.models.server import Server
from app.models.database import Database
from app.models.workload import Workload


def delete_existing_workloads_for_run(db: Session, run_id: str) -> None:
    """
    Idempotency helper: remove any previously generated workloads
    for this run before rebuilding.
    """
    db.query(Workload).filter(Workload.run_id == run_id).delete(
        synchronize_session=False
    )


def _group_servers(servers: List[Server]) -> Dict[str, List[Server]]:
    """
    Very simple first-pass grouping strategy.

    We try a few reasonable fields that might exist on the Server model:
    - application_name
    - app_name
    - role
    - environment

    If none are present / populated, we fall back to a single
    catch-all workload.

    This is intentionally conservative so we don't depend on
    specific columns that may not exist in your schema.
    """
    groups: Dict[str, List[Server]] = {}

    for server in servers:
        app_name = getattr(server, "application_name", None) or getattr(
            server, "app_name", None
        )
        role = getattr(server, "role", None)
        env = getattr(server, "environment", None)

        if app_name:
            key = f"{app_name}"
        elif role and env:
            key = f"{role} ({env})"
        elif role:
            key = role
        elif env:
            key = f"default ({env})"
        else:
            key = "default-workload"

        groups.setdefault(key, []).append(server)

    return groups


def build_workloads_for_run(db: Session, run_id: str) -> List[Workload]:
    """
    Main entrypoint: group servers into workloads and persist simple
    Workload records.

    For now we only create Workload rows with:
    - run_id
    - name

    Any additional fields on Workload are assumed to have defaults /
    be nullable.
    """
    # Clear previous workloads for this run so the operation is idempotent.
    delete_existing_workloads_for_run(db, run_id)

    # Load servers for this run.
    servers: List[Server] = (
        db.query(Server).filter(Server.run_id == run_id).order_by(Server.name).all()
    )

    if not servers:
        # Nothing to do – return empty list so the API responds cleanly.
        db.commit()
        return []

    grouped = _group_servers(servers)

    workloads: List[Workload] = []

    # Create one Workload per group.
    for workload_name, group_servers in grouped.items():
        # Only use fields we are confident exist: run_id and name.
        workload = Workload(run_id=run_id, name=workload_name)  # type: ignore[arg-type]
        db.add(workload)
        workloads.append(workload)

    db.commit()

    # Refresh so we have ids populated, etc.
    for w in workloads:
        db.refresh(w)

    return workloads
