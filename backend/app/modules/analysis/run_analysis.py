import json
import logging
from typing import Dict, Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import (
    Server,
    Application,
    StorageVolume,
    NetworkDevice,
    RunSliceMetric,
)

logger = logging.getLogger(__name__)


def _analyze_servers(db: Session, run_id: str) -> Dict[str, Any]:
    q = db.query(Server).filter_by(run_id=run_id)
    row_count = q.count()
    return {
        "row_count": row_count,
    }


def _analyze_apps(db: Session, run_id: str) -> Dict[str, Any]:
    q = db.query(Application).filter_by(run_id=run_id)
    row_count = q.count()

    env_counts = dict(
        db.query(Application.environment, func.count("*"))
        .filter_by(run_id=run_id)
        .group_by(Application.environment)
        .all()
    )

    return {
        "row_count": row_count,
        "env_counts": env_counts,
    }


def _analyze_networks(db: Session, run_id: str) -> Dict[str, Any]:
    q = db.query(NetworkDevice).filter_by(run_id=run_id)
    row_count = q.count()
    return {
        "row_count": row_count,
    }


def _analyze_storage(db: Session, run_id: str) -> Dict[str, Any]:
    q = db.query(StorageVolume).filter_by(run_id=run_id)
    row_count = q.count()

    total_size = (
        db.query(func.coalesce(func.sum(StorageVolume.size_gb), 0.0))
        .filter_by(run_id=run_id)
        .scalar()
    )

    return {
        "row_count": row_count,
        "total_size_gb": float(total_size or 0.0),
    }


def analyze_ingest_slice(run_id: str, slice_name: str) -> None:
    """
    Background job that computes metrics per slice and stores them
    in run_slice_metrics as a single JSON document per (run_id, slice_name).
    """
    db = SessionLocal()
    try:
        if slice_name == "servers":
            metrics = _analyze_servers(db, run_id)
        elif slice_name == "apps":
            metrics = _analyze_apps(db, run_id)
        elif slice_name == "networks":
            metrics = _analyze_networks(db, run_id)
        elif slice_name == "storage":
            metrics = _analyze_storage(db, run_id)
        else:
            logger.warning("[analysis] Unknown slice '%s' for run=%s", slice_name, run_id)
            return

        row_count = int(metrics.get("row_count", 0))

        # Upsert per (run_id, slice_name)
        existing = (
            db.query(RunSliceMetric)
            .filter(
                RunSliceMetric.run_id == run_id,
                RunSliceMetric.slice_name == slice_name,
            )
            .order_by(RunSliceMetric.id.asc())
            .first()
        )

        if existing:
            existing.row_count = row_count
            existing.metrics_json = json.dumps(metrics)
        else:
            db.add(
                RunSliceMetric(
                    run_id=run_id,
                    slice_name=slice_name,
                    row_count=row_count,
                    metrics_json=json.dumps(metrics),
                )
            )

        db.commit()
        logger.info(
            "[analysis] run=%s slice=%s metrics=%s",
            run_id,
            slice_name,
            metrics,
        )
    finally:
        db.close()
