# app/routers/preview.py

import csv
import io
import json
from typing import Any, Dict, List

from fastapi import APIRouter, UploadFile, File, HTTPException, status

router = APIRouter(
    prefix="/preview",
    tags=["preview"],
)


def _make_preview(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "count": len(rows),
        "columns": list(rows[0].keys()) if rows else [],
        "rows": rows[:50],
    }


@router.post("/servers")
async def preview_servers(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Servers preview requires CSV",
        )
    contents = (await file.read()).decode("utf-8", errors="ignore")
    rows = list(csv.DictReader(io.StringIO(contents)))
    return _make_preview(rows)


@router.post("/apps")
async def preview_apps(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apps preview requires CSV",
        )
    contents = (await file.read()).decode("utf-8", errors="ignore")
    rows = list(csv.DictReader(io.StringIO(contents)))
    return _make_preview(rows)


@router.post("/storage")
async def preview_storage(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Storage preview requires CSV",
        )
    contents = (await file.read()).decode("utf-8", errors="ignore")
    rows = list(csv.DictReader(io.StringIO(contents)))
    return _make_preview(rows)


@router.post("/networks")
async def preview_networks(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Network preview requires CSV",
        )
    contents = (await file.read()).decode("utf-8", errors="ignore")
    rows = list(csv.DictReader(io.StringIO(contents)))
    return _make_preview(rows)


@router.post("/vcenter")
async def preview_vcenter(file: UploadFile = File(...)):
    """
    Preview vCenter export (JSON only for now).

    Expected: JSON document with either:
      - a top-level array of VMs, or
      - an object with a list under keys like "vms", "virtual_machines", or "value".
    """
    contents = (await file.read()).decode("utf-8", errors="ignore")

    try:
        data = json.loads(contents)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="vCenter preview currently supports JSON exports only.",
        )

    # Try to locate a VM list in common patterns
    vms: List[Any] = []
    if isinstance(data, list):
        vms = data
    elif isinstance(data, dict):
        for key in ["vms", "virtual_machines", "virtualMachines", "value"]:
            if isinstance(data.get(key), list):
                vms = data[key]
                break
        if not vms:
            # Fallback: treat the whole dict as a single VM record
            vms = [data]

    return {
        "vm_count": len(vms),
        "sample": vms[:10],
    }
