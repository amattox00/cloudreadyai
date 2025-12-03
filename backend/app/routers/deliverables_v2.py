from __future__ import annotations

from typing import Optional

from fastapi import APIRouter

from pydantic import BaseModel

from app.modules.deliverables.packaging_v2 import (
    load_workload_from_disk,
    build_deliverables_zip,
    encode_zip_base64,
)


router = APIRouter(tags=["deliverables_v2"])


class DeliverablesPackageV2Request(BaseModel):
    workload_id: str
    opportunity_id: Optional[str] = None
    org_name: Optional[str] = None
    environment: Optional[str] = None
    version_tag: Optional[str] = None


class DeliverablesPackageV2Response(BaseModel):
    zip_filename: str
    zip_base64: str


@router.post("/deliverables/package_v2", response_model=DeliverablesPackageV2Response)
def package_deliverables_v2(payload: DeliverablesPackageV2Request) -> DeliverablesPackageV2Response:
    """
    Package deliverables for a given workload_id (and optional opportunity metadata)
    into a ZIP containing:

      - diagrams/architecture.drawio.xml
      - metadata/workload.json
      - metadata/summary.txt
    """
    workload = load_workload_from_disk(payload.workload_id)

    filename, zip_bytes = build_deliverables_zip(
        workload,
        opportunity_id=payload.opportunity_id,
        org_name=payload.org_name,
        environment=payload.environment,
        version_tag=payload.version_tag,
    )

    zip_b64 = encode_zip_base64(zip_bytes)
    return DeliverablesPackageV2Response(zip_filename=filename, zip_base64=zip_b64)
