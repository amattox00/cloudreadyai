# app/routers/run_insights_v2.py

from fastapi import APIRouter, HTTPException

from app.modules.analysis_v2.run_views_v2 import (
    get_servers_slice_summary,
    get_server_rscores,
    get_workloads_summary,
)

router = APIRouter(
    prefix="/api/runs",
    tags=["run_insights_v2"],
)


@router.get("/{run_id}/servers/summary")
def get_servers_summary_endpoint(run_id: str):
    """
    High-level servers slice summary for a run, including R-Score overview.

    Returns:
    {
      "row_count": 2,
      "environment_counts": {...},
      "role_counts": {...},
      "os_counts": {...},
      "rscore_summary": {
          "num_scored": 2,
          "distribution": {...},
          "average_scores": {...}
      }
    }

    404 if no servers slice metrics exist for this run.
    """
    summary = get_servers_slice_summary(run_id)
    if summary is None:
        raise HTTPException(
            status_code=404,
            detail=f"No servers slice metrics found for run_id={run_id}",
        )
    return summary


@router.get("/{run_id}/servers/rscores")
def get_server_rscores_endpoint(run_id: str):
    """
    Per-server 6R scores and final recommendation for a run.

    Returns a list like:
    [
      {
        "hostname": "...",
        "role": "...",
        "os": "...",
        "environment": "...",
        "cpu_usage": 0.0,
        "ram_usage": 0.0,
        "rehost": 45.0,
        "replatform": 55.0,
        "refactor": 30.0,
        "repurchase": 10.0,
        "retire": 16.0,
        "retain": 12.5,
        "final_recommendation": "REPLATFORM",
      },
      ...
    ]

    Empty list is allowed if no scores exist for this run.
    """
    return get_server_rscores(run_id)


@router.get("/{run_id}/workloads")
def get_workloads_summary_endpoint(run_id: str):
    """
    Workload-level summary for a run from the workloads table.

    Returns a list like:
    [
      {
        "id": 1,
        "name": "web (prod)",
        "environment": "prod",
        "tier": "app",
        "utilization_cpu": 35.0,
        "utilization_memory": 40.0,
        "migration_pattern": "REPLATFORM",
      },
      ...
    ]

    Empty list is allowed if no workloads exist for this run.
    """
    return get_workloads_summary(run_id)
