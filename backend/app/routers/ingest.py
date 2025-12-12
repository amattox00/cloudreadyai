from __future__ import annotations

import csv
import io
from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.db import get_db
from app.modules.ingestion_engine import (
    ingest_applications,
    ingest_business,
    ingest_databases,
    ingest_dependencies,
    ingest_licensing,
    ingest_networks,
    ingest_os_metadata,
    ingest_servers,
    ingest_storage,
    ingest_utilization,
    list_ingest_routes,
)

# Template access helpers (for UI + clients to download the "official" templates)
from app.modules.ingestion_templates.template_validator import TEMPLATE_DIR, load_template

router = APIRouter(prefix="/v1/ingest", tags=["Ingestion"])


async def _run_slice_ingest(
    *,
    slice_name: str,
    fn,
    db: Session,
    run_id: str,
    file: UploadFile,
) -> Dict[str, Any]:
    """
    Tiny wrapper so all slices behave the same. It lets the underlying
    ingestion_engine handle CSV parsing + DB writes.
    """
    if not run_id:
        raise HTTPException(status_code=400, detail="run_id query parameter is required")

    try:
        result = await fn(db=db, run_id=run_id, file=file)
    except HTTPException:
        # Let explicit HTTP errors bubble through
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=500,
            detail=f"{slice_name} ingestion failed: {exc}",
        ) from exc

    # Normalise response shape a bit
    if not isinstance(result, dict):
        result = {"raw_result": str(result)}

    return {
        "ok": True,
        "slice": slice_name,
        "run_id": run_id,
        "details": result,
    }


# ------------------------------
# Servers
# ------------------------------


@router.post("/servers")
async def ingest_servers_endpoint(
    run_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    UI servers CSV upload endpoint.

    Frontend calls:
      POST /v1/ingest/servers?run_id=<run-id>
      Content-Type: multipart/form-data with field "file"
    """
    return await _run_slice_ingest(
        slice_name="servers",
        fn=ingest_servers,
        db=db,
        run_id=run_id,
        file=file,
    )


# ------------------------------
# Storage volumes
# ------------------------------


@router.post("/storage")
async def ingest_storage_endpoint(
    run_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Storage volumes CSV upload.

    Frontend will call:
      POST /v1/ingest/storage?run_id=<run-id>
    """
    return await _run_slice_ingest(
        slice_name="storage",
        fn=ingest_storage,
        db=db,
        run_id=run_id,
        file=file,
    )


# ------------------------------
# Databases
# ------------------------------


@router.post("/databases")
async def ingest_databases_endpoint(
    run_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Databases CSV upload.

    Frontend will call:
      POST /v1/ingest/databases?run_id=<run-id>
    """
    return await _run_slice_ingest(
        slice_name="databases",
        fn=ingest_databases,
        db=db,
        run_id=run_id,
        file=file,
    )


# ------------------------------
# Applications
# ------------------------------


@router.post("/applications")
async def ingest_applications_endpoint(
    run_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    return await _run_slice_ingest(
        slice_name="applications",
        fn=ingest_applications,
        db=db,
        run_id=run_id,
        file=file,
    )


@router.post("/business")
async def ingest_business_endpoint(
    run_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    return await _run_slice_ingest(
        slice_name="business",
        fn=ingest_business,
        db=db,
        run_id=run_id,
        file=file,
    )


@router.post("/dependencies")
async def ingest_dependencies_endpoint(
    run_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    return await _run_slice_ingest(
        slice_name="dependencies",
        fn=ingest_dependencies,
        db=db,
        run_id=run_id,
        file=file,
    )


@router.post("/licensing")
async def ingest_licensing_endpoint(
    run_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    return await _run_slice_ingest(
        slice_name="licensing",
        fn=ingest_licensing,
        db=db,
        run_id=run_id,
        file=file,
    )


@router.post("/os-metadata")
async def ingest_os_metadata_endpoint(
    run_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    return await _run_slice_ingest(
        slice_name="os_metadata",
        fn=ingest_os_metadata,
        db=db,
        run_id=run_id,
        file=file,
    )


@router.post("/networks")
async def ingest_networks_endpoint(
    run_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    return await _run_slice_ingest(
        slice_name="networks",
        fn=ingest_networks,
        db=db,
        run_id=run_id,
        file=file,
    )


@router.post("/utilization")
async def ingest_utilization_endpoint(
    run_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    return await _run_slice_ingest(
        slice_name="utilization",
        fn=ingest_utilization,
        db=db,
        run_id=run_id,
        file=file,
    )


# ------------------------------
# Utility: list available ingest routes
# ------------------------------


@router.get("/routes")
async def get_ingest_routes() -> List[Dict[str, str]]:
    """
    Simple debug helper – shows which ingestion routes are wired.
    """
    return list_ingest_routes()


# ------------------------------
# Template endpoints
# ------------------------------


def _list_template_slices() -> List[str]:
    """
    Return a sorted list of slice names based on *.template.json files.
    """
    if not TEMPLATE_DIR.exists():
        return []
    slices: List[str] = []
    for p in TEMPLATE_DIR.glob("*.template.json"):
        name = p.name.replace(".template.json", "").strip()
        if name:
            slices.append(name)
    return sorted(set(slices))


@router.get("/templates")
async def list_templates() -> Dict[str, Any]:
    """
    Lists available ingestion templates.

    Useful for UI: show “Download template” buttons per slice.
    """
    slices = _list_template_slices()
    templates: List[Dict[str, Any]] = []
    for s in slices:
        try:
            tpl = load_template(s)
            templates.append(
                {
                    "slice": tpl.get("slice", s),
                    "required_headers": tpl.get("required_headers", []),
                    "optional_headers": tpl.get("optional_headers", []),
                    "header_aliases": tpl.get("header_aliases", {}),
                    "policy": tpl.get("policy", {}),
                }
            )
        except Exception:
            # If a template is malformed, skip it rather than failing the whole endpoint
            continue

    return {"ok": True, "templates": templates}


@router.get("/templates/{slice_name}")
async def get_template(slice_name: str) -> Dict[str, Any]:
    """
    Returns the full JSON template for a given slice.

    Example:
      GET /v1/ingest/templates/servers
      GET /v1/ingest/templates/storage
    """
    # allow either "servers" or "servers.template.json" style input
    clean = slice_name.replace(".template.json", "").strip()
    if not clean:
        raise HTTPException(status_code=400, detail="slice_name is required")

    path = Path(TEMPLATE_DIR) / f"{clean}.template.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Template not found for slice: {clean}")

    try:
        tpl = load_template(clean)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to load template {clean}: {exc}") from exc

    return {"ok": True, "template": tpl}


@router.get("/templates/{slice_name}/csv")
async def download_template_csv(
    slice_name: str,
    include_optional: bool = Query(True, description="If true, include optional headers too"),
    include_example_row: bool = Query(False, description="If true, add a blank example row"),
) -> Response:
    """
    Download a CSV template for a given slice.

    - Row 1: headers
    - Optional: add a blank example row (same columns, empty values)
    """
    clean = slice_name.replace(".template.json", "").strip()
    if not clean:
        raise HTTPException(status_code=400, detail="slice_name is required")

    path = Path(TEMPLATE_DIR) / f"{clean}.template.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Template not found for slice: {clean}")

    try:
        tpl = load_template(clean)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to load template {clean}: {exc}") from exc

    required = [str(x) for x in (tpl.get("required_headers", []) or [])]
    optional = [str(x) for x in (tpl.get("optional_headers", []) or [])]

    headers = required + (optional if include_optional else [])
    headers = [h for h in headers if h]

    if not headers:
        raise HTTPException(status_code=500, detail=f"Template for {clean} has no headers")

    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(headers)

    if include_example_row:
        writer.writerow(["" for _ in headers])

    content = buf.getvalue().encode("utf-8")
    filename = f"{clean}.template.csv"

    return Response(
        content=content,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
