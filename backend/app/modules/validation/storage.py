from sqlalchemy.orm import Session
from app.models.storage import Storage

def storage_problems(db: Session, run_id: str):
    rows = db.query(Storage).filter(Storage.run_id == run_id).all()

    problems = []

    # Missing size
    missing_size = [r.name for r in rows if not r.size_gb]
    if missing_size:
        problems.append({
            "code": "missing_size",
            "severity": "warning",
            "message": "Storage volumes missing size_gb.",
            "count": len(missing_size),
            "examples": missing_size[:5],
        })

    # Negative sizes
    negative = [r.name for r in rows if r.size_gb and r.size_gb < 0]
    if negative:
        problems.append({
            "code": "negative_size",
            "severity": "error",
            "message": "Storage volumes with negative size_gb.",
            "count": len(negative),
            "examples": negative[:5],
        })

    return {
        "run_id": run_id,
        "rows_seen": len(rows),
        "problems": problems,
        "summary": {
            "error_count": len([p for p in problems if p["severity"] == "error"]),
            "warning_count": len([p for p in problems if p["severity"] == "warning"]),
        }
    }
