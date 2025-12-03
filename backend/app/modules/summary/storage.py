from sqlalchemy.orm import Session
from app.models.storage import Storage

def summarize_storage(db: Session, run_id: str):
    rows = db.query(Storage).filter(Storage.run_id == run_id).all()

    total_gb = sum([float(r.size_gb or 0) for r in rows])
    raid_counts = {}
    env_counts = {}

    for r in rows:
        raid = r.raid or "unknown"
        raid_counts[raid] = raid_counts.get(raid, 0) + 1

        env = r.environment or "unknown"
        env_counts[env] = env_counts.get(env, 0) + 1

    return {
        "storage_count": len(rows),
        "total_size_gb": total_gb,
        "raid_distribution": raid_counts,
        "environment_distribution": env_counts,
    }
