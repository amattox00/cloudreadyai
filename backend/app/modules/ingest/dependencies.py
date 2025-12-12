import csv
from typing import Any, Dict, List, Optional, Set, Tuple

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.models.app_dependency import AppDependency


EXPECTED_HEADERS = [
    "app_id",
    "depends_on_app_id",
    "dependency_type",
    "notes",
]


def _norm(s: Optional[str]) -> str:
    return (s or "").strip()


def _detect_cycles(edges: List[Tuple[str, str]]) -> int:
    """
    Lightweight cycle detection for directed graph edges (u -> v).
    Returns number of nodes involved in at least one cycle (approx).
    Safe for a few thousand edges.
    """
    adj: Dict[str, List[str]] = {}
    nodes: Set[str] = set()
    for u, v in edges:
        nodes.add(u)
        nodes.add(v)
        adj.setdefault(u, []).append(v)

    # 0=unvisited, 1=visiting, 2=done
    state: Dict[str, int] = {n: 0 for n in nodes}
    cycle_nodes: Set[str] = set()

    def dfs(n: str, stack: List[str]) -> None:
        state[n] = 1
        stack.append(n)

        for nxt in adj.get(n, []):
            st = state.get(nxt, 0)
            if st == 0:
                dfs(nxt, stack)
            elif st == 1:
                # back-edge -> cycle
                if nxt in stack:
                    idx = stack.index(nxt)
                    for k in stack[idx:]:
                        cycle_nodes.add(k)

        stack.pop()
        state[n] = 2

    for n in list(nodes):
        if state.get(n, 0) == 0:
            dfs(n, [])

    return len(cycle_nodes)


def ingest_dependencies_csv(
    db: Session,
    run_id: str,
    csv_path: str,
    *,
    replace_existing: bool = True,
    detect_cycles: bool = True,
    max_errors: int = 25,
) -> Dict[str, Any]:
    """
    Ingest an Application Dependencies CSV from a local file path.

    Expected columns:
      app_id, depends_on_app_id, dependency_type, notes

    Behavior:
      - replace_existing=True: delete existing dependencies for run_id before insert
      - validates required fields (app_id, depends_on_app_id)
      - de-duplicates edges within this upload (app_id, depends_on_app_id, dependency_type)
      - optionally detects cycles and returns cycle info as warnings (non-fatal)

    Returns:
      A dict with stable keys used by ingestion_engine/UI.
    """
    if not run_id:
        raise ValueError("run_id is required")

    # Replace-existing to make re-upload idempotent
    deleted_existing = 0
    replaced_existing = False
    if replace_existing:
        res = db.execute(delete(AppDependency).where(AppDependency.run_id == run_id))
        deleted_existing = int(getattr(res, "rowcount", 0) or 0)
        db.commit()
        replaced_existing = True

    rows_processed = 0
    rows_inserted = 0
    rows_failed = 0
    duplicates_skipped = 0

    errors: List[str] = []
    seen: Set[Tuple[str, str, str]] = set()
    edges_for_cycle: List[Tuple[str, str]] = []

    with open(csv_path, newline="", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)

        if reader.fieldnames is None:
            raise ValueError("Dependencies CSV appears to have no header row.")

        missing = [h for h in EXPECTED_HEADERS if h not in reader.fieldnames]
        if missing:
            raise ValueError(
                f"Missing expected columns in dependencies CSV: {', '.join(missing)}"
            )

        for idx, row in enumerate(reader, start=2):  # header is line 1
            if not row:
                continue

            rows_processed += 1

            app_id = _norm(row.get("app_id"))
            depends_on_app_id = _norm(row.get("depends_on_app_id"))
            dependency_type = _norm(row.get("dependency_type"))
            notes = _norm(row.get("notes"))

            # Required fields
            if not app_id or not depends_on_app_id:
                rows_failed += 1
                if len(errors) < max_errors:
                    errors.append(f"Line {idx}: missing required app_id/depends_on_app_id")
                continue

            # Self-dependency is almost always a data bug -> fail
            if app_id == depends_on_app_id:
                rows_failed += 1
                if len(errors) < max_errors:
                    errors.append(f"Line {idx}: app_id equals depends_on_app_id ({app_id})")
                continue

            key = (app_id, depends_on_app_id, dependency_type.lower())
            if key in seen:
                duplicates_skipped += 1
                continue
            seen.add(key)

            db.add(
                AppDependency(
                    run_id=run_id,
                    app_id=app_id,
                    depends_on_app_id=depends_on_app_id,
                    dependency_type=dependency_type,
                    notes=notes,
                )
            )
            rows_inserted += 1

            if detect_cycles:
                edges_for_cycle.append((app_id, depends_on_app_id))

    db.commit()

    cycles_detected = 0
    if detect_cycles and edges_for_cycle:
        cycles_detected = _detect_cycles(edges_for_cycle)

    message = (
        f"Dependencies CSV ingested successfully "
        f"({rows_inserted}/{rows_processed} rows inserted"
        f"{', ' + str(rows_failed) + ' failed' if rows_failed else ''}"
        f"{', ' + str(duplicates_skipped) + ' duplicates skipped' if duplicates_skipped else ''}"
        f"{', ' + str(cycles_detected) + ' cycle-nodes detected' if cycles_detected else ''})"
    )

    # Provide stable aliases expected by other code paths
    return {
        "rows_processed": rows_processed,
        "rows_inserted": rows_inserted,
        "rows_successful": rows_inserted,  # alias
        "rows_failed": rows_failed,
        "duplicates_skipped": duplicates_skipped,
        "deleted_existing": deleted_existing,
        "replaced_existing": replaced_existing,
        "cycles_detected": cycles_detected,
        "message": message,
        "errors": errors,
    }
