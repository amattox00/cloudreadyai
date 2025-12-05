from __future__ import annotations

from typing import Iterable

from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models.inventory_network_v2 import InventoryNetworkV2
from app.modules.ingestion_core.networks_ingestion_v2 import NetworkRow


def persist_network_records_v2(
    run_id: str,
    records: Iterable[NetworkRow],
) -> int:
    """
    Persist validated NetworkRow records into inventory_networks_v2.
    """
    db: Session = SessionLocal()
    inserted = 0
    try:
        for rec in records:
            row = InventoryNetworkV2(
                run_id=run_id,
                subnet_id=rec.subnet_id,
                subnet_cidr=rec.subnet_cidr,
                vlan_id=rec.vlan_id,
                environment=rec.environment,
                datacenter=rec.datacenter,
                zone=rec.zone,
                network_name=rec.network_name,
                purpose=rec.purpose,
                is_public=rec.is_public,
                is_dmz=rec.is_dmz,
                connected_to=rec.connected_to,
                tags=rec.tags,
            )
            db.add(row)
            inserted += 1

        db.commit()
        return inserted
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
