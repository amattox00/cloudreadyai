"""
Quick CLI helper for Analysis v2.

Usage:

  cd ~/cloudreadyai/backend
  . .venv/bin/activate
  python -m tools.test_analysis_v2 <run_id>

Example:

  python -m tools.test_analysis_v2 run-servers-v2-scale-500
"""

import json
import sys
from typing import Any

from app.db import SessionLocal
from app.modules.analysis_v2.run_summary_v2 import summarize_run_v2


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python -m tools.test_analysis_v2 <run_id>")
        sys.exit(1)

    run_id = sys.argv[1]
    print(f"Analysis v2 summary for run_id={run_id}\n")

    db = SessionLocal()
    try:
        summary = summarize_run_v2(run_id=run_id, db=db)
    finally:
        db.close()

    # Pydantic model → dict → pretty JSON
    payload: dict[str, Any] = summary.model_dump()
    print(json.dumps(payload, indent=2, default=str))


if __name__ == "__main__":
    main()
