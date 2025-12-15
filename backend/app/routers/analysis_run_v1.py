from fastapi import APIRouter, HTTPException

# IMPORTANT:
# The UI run registry is currently the in-memory router at /v1/run_registry (app/routers/runs.py).
# Until we unify run ids across DB + UI, Analysis v1 will read from the same in-memory store
# so we don't regress demos.
from app.routers import runs as runs_router

router = APIRouter(prefix="/v1/analysis", tags=["analysis_run_v1"])


def _get_run_or_404(run_id: str) -> runs_router.RunRecord:
    record = runs_router._RUN_REGISTRY.get(run_id)  # pylint: disable=protected-access
    if not record:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")
    return record


@router.get("/run/{run_id}/overview")
def run_overview(run_id: str):
    run = _get_run_or_404(run_id)

    counts = {
        "servers": int(run.servers_ingested or 0),
        "storage": int(run.storage_ingested or 0),
        "databases": int(run.databases_ingested or 0),
        "applications": int(run.applications_ingested or 0),
        "dependencies": int(run.dependencies_ingested or 0),
        "network": int(run.network_ingested or 0),
    }

    has_servers = counts["servers"] > 0
    has_other = (
        counts["storage"]
        + counts["databases"]
        + counts["applications"]
        + counts["dependencies"]
        + counts["network"]
    ) > 0

    ready_for_analysis = has_servers and has_other

    findings = []
    if not has_servers:
        findings.append("No servers ingested yet. Upload Servers CSV to unlock meaningful analysis.")
    if has_servers and not has_other:
        findings.append("Servers are present, but no other slices are populated yet. Add at least one more slice.")
    if ready_for_analysis:
        findings.append("Readiness gate passed. Proceed to Analysis, Diagrams, and Cost Modeling.")

    return {
        "run": {
            "id": run.id,
            "created_at": run.created_at,
            "name": run.name,
            "source": run.source,
            "state": run.state,
        },
        "counts": counts,
        "readiness": {
            "has_servers": has_servers,
            "has_other_slice": has_other,
            "ready_for_analysis": ready_for_analysis,
        },
        "findings": findings,
        "version": "analysis_run_v1",
    }


@router.get("/run/{run_id}/servers/segmentation")
def servers_segmentation(run_id: str):
    run = _get_run_or_404(run_id)
    servers_count = int(run.servers_ingested or 0)

    # MVP placeholder response shape (stable for UI wiring)
    return {
        "run_id": run_id,
        "totals": {"servers": servers_count},
        "segments": {
            "os_family": [],
            "environment": [],
            "cpu_cores_bucket": [],
            "ram_gb_bucket": [],
        },
        "note": "MVP placeholder. Next: compute segmentation from V2 inventory rows (/v1/ingest/results).",
        "version": "analysis_run_v1",
    }
