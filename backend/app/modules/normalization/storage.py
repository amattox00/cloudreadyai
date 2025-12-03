from sqlalchemy.orm import Session
from app.models.storage import Storage

def normalize_storage(db: Session, run_id: str):
    rows = db.query(Storage).filter(Storage.run_id == run_id).all()

    rows_updated = 0
    for r in rows:
        # Normalize environment (lowercase, expanded)
        if r.environment:
            env = r.environment.lower()
            r.environment = {
                "prod": "production",
                "production": "production",
                "dev": "development",
                "development": "development",
                "test": "test",
            }.get(env, env)

        # Normalize RAID field
        if r.raid:
            r.raid = r.raid.upper().replace("RAID", "RAID ")

        rows_updated += 1

    db.commit()

    return {
        "run_id": run_id,
        "rows_seen": len(rows),
        "rows_updated": rows_updated,
    }
