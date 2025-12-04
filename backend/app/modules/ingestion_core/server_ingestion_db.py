import uuid
from sqlalchemy.orm import Session

from app.modules.ingestion_core.server_ingestion_core import ServerRow
from app.models.server import Server  # assuming this import already works


def persist_row_to_db(
    row: ServerRow,
    db: Session,
    run_id: str,
) -> None:
    """
    Map a validated ServerRow into your Server DB model and upsert by (run_id, hostname).
    """

    # Try to find an existing row for this run_id + hostname
    server = (
        db.query(Server)
        .filter(
            Server.run_id == run_id,
            Server.hostname == row.hostname,
        )
        .one_or_none()
    )

    if server is None:
        # 👇 Generate a primary key since the DB doesn't auto-generate server_id
        server = Server(
            server_id=str(uuid.uuid4()),
            run_id=run_id,
            hostname=row.hostname,
        )
        db.add(server)

    # Map fields (adjust to match your actual column names)
    server.environment = row.environment
    server.os = row.os
    server.platform = row.platform
    server.vm_id = row.vm_id

    # 👇 Map CSV ip_address to the DB's ip column
    try:
        server.ip = row.ip_address
    except AttributeError:
        # If your model uses a different field name (e.g. ip_address), adjust here
        pass

    server.subnet = row.subnet
    server.datacenter = row.datacenter
    server.cluster_name = row.cluster_name
    server.role = row.role
    server.app_name = row.app_name
    server.owner = row.owner
    server.criticality = row.criticality
    server.cpu_cores = row.cpu_cores
    server.memory_gb = row.memory_gb
    server.storage_gb = row.storage_gb
    server.is_virtual = row.is_virtual
    server.is_cloud = row.is_cloud
    server.tags = row.tags
