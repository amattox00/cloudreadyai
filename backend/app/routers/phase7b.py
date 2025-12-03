import base64
import io
import re
import zipfile

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


# -------------------------------
# Request Models
# -------------------------------
class DiagramRequest(BaseModel):
    cloud: str
    diagram_type: str
    org_name: str | None = None
    environment: str | None = None
    workload_name: str | None = None
    overlay_profile: str | None = None  # "dod" | "fedramp" | "zero_trust"


class DiagramPackageRequest(BaseModel):
    """
    Request for a multi-diagram ZIP package.

    By default, generates AWS/Azure/GCP × (landing_zone, network, application).
    """
    clouds: list[str] | None = None
    include_types: list[str] | None = None
    org_name: str | None = None
    environment: str | None = None
    workload_name: str | None = None
    overlay_profile: str | None = None
    opportunity_id: str | None = None
    version_tag: str | None = "v1"


# ------------------------------------------------------
# Utility wrappers / helpers
# ------------------------------------------------------
def _mxfile_wrapper(diagram_name: str, inner_xml: str) -> str:
    return f"""<mxfile host="cloudreadyai" modified="2025-11-15T00:00:00Z" agent="CloudReadyAI-Phase7D" version="1.0">
  <diagram id="cloud-diagram" name="{diagram_name}">
    <mxGraphModel dx="1024" dy="768" grid="1" gridSize="10" guides="1" tooltips="1"
                  connect="1" arrows="1" fold="1" page="1" pageScale="1"
                  pageWidth="1169" pageHeight="827" math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
{inner_xml}
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>"""


def _overlay_cells(profile: str | None) -> str:
    """
    Optional compliance overlay banner at the bottom of the diagram.
    """
    if not profile:
        return ""

    p = profile.lower()

    if p == "dod":
        label = "DoD Overlay: IL4–IL6 Enclaves, Mission Owner Boundaries, Cross-Domain Guardrails"
    elif p == "fedramp":
        label = "FedRAMP Overlay: High Baseline, ATO Boundary, Shared Responsibility Assignments"
    elif p == "zero_trust":
        label = "Zero Trust Overlay: Identity, Device, Network, Application, Data, Visibility Planes"
    else:
        # Unknown overlay profile – skip rather than error
        return ""

    return f"""        <mxCell id="overlay_{p}" value="{label}" style="rounded=1;whiteSpace=wrap;html=1;fontStyle=1;strokeColor=#B03A2E;fillColor=#FDEDEC;" vertex="1" parent="1">
          <mxGeometry x="80" y="580" width="960" height="70" as="geometry"/>
        </mxCell>
"""


def _safe_slug(value: str | None, fallback: str) -> str:
    v = (value or "").strip() or fallback
    return re.sub(r"[^A-Za-z0-9]+", "_", v)


def _type_short(diagram_type: str) -> str:
    if diagram_type == "landing_zone":
        return "LZ"
    if diagram_type == "network":
        return "NET"
    return "APP"


def _build_diagram_filename(cloud: str, diagram_type: str, pkg: DiagramPackageRequest) -> str:
    cloud_part = cloud.upper()
    type_part = _type_short(diagram_type)

    # If no proposal context, use generic naming
    if not pkg.opportunity_id:
        return f"cloudready-{cloud_part}-{type_part}.drawio"

    client_part = _safe_slug(pkg.org_name, "Client")
    opp_part = _safe_slug(pkg.opportunity_id, "OPP")
    version_part = _safe_slug(pkg.version_tag or "v1", "v1")

    return f"{client_part}_{opp_part}_{cloud_part}_{type_part}_{version_part}.drawio"


def _build_zip_name(pkg: DiagramPackageRequest) -> str:
    if not pkg.opportunity_id:
        return "cloudready-diagrams.zip"
    return f"{_safe_slug(pkg.opportunity_id, 'OPP')}_diagrams.zip"


# ------------------------------------------------------
# AWS Landing Zone
# ------------------------------------------------------
def generate_aws_lz(req: DiagramRequest) -> str:
    org = req.org_name or "Organization"
    env = req.environment or "Environment"
    workload = req.workload_name or "Workload"

    header = f"""        <mxCell id="aws_h1" value="AWS Landing Zone - {org} ({env})" style="rounded=1;fontStyle=1;strokeColor=#232F3E;fillColor=#F4F6F6;" vertex="1" parent="1">
          <mxGeometry x="80" y="40" width="960" height="120" as="geometry"/>
        </mxCell>"""

    body = f"""
        <mxCell id="aws_h2" value="AWS Organizations / Security Root" style="rounded=1;whiteSpace=wrap;strokeColor=#95A5A6;fillColor=#ECF0F1;" vertex="1" parent="1">
          <mxGeometry x="100" y="70" width="260" height="70" as="geometry"/>
        </mxCell>

        <mxCell id="aws_h3" value="Shared Services Account" style="rounded=1;whiteSpace=wrap;strokeColor=#95A5A6;fillColor=#ECF0F1;" vertex="1" parent="1">
          <mxGeometry x="380" y="70" width="260" height="70" as="geometry"/>
        </mxCell>

        <mxCell id="aws_h4" value="Security / Logging Account" style="rounded=1;whiteSpace=wrap;strokeColor=#95A5A6;fillColor=#ECF0F1;" vertex="1" parent="1">
          <mxGeometry x="660" y="70" width="260" height="70" as="geometry"/>
        </mxCell>

        <mxCell id="aws_h5" value="{workload} Account" style="rounded=1;whiteSpace=wrap;strokeColor=#95A5A6;fillColor=#ECF0F1;" vertex="1" parent="1">
          <mxGeometry x="940" y="70" width="140" height="70" as="geometry"/>
        </mxCell>
"""

    inner = header + body + _overlay_cells(req.overlay_profile)
    return _mxfile_wrapper(f"AWS Landing Zone - {org} ({env})", inner)


# ------------------------------------------------------
# Azure Landing Zone
# ------------------------------------------------------
def generate_azure_lz(req: DiagramRequest) -> str:
    org = req.org_name or "Organization"
    env = req.environment or "Environment"
    workload = req.workload_name or "Workload"

    header = f"""        <mxCell id="az_lz1" value="Azure Landing Zone - {org} ({env})" style="rounded=1;fontStyle=1;strokeColor=#0072C6;fillColor=#E8F4FF;" vertex="1" parent="1">
          <mxGeometry x="80" y="40" width="960" height="120" as="geometry"/>
        </mxCell>"""

    body = f"""
        <mxCell id="az_lz2" value="Management Group Root" style="rounded=1;strokeColor=#7F8C8D;fillColor=#ECECEC;" vertex="1" parent="1">
          <mxGeometry x="100" y="70" width="240" height="70" as="geometry"/>
        </mxCell>

        <mxCell id="az_lz3" value="Platform / Connectivity" style="rounded=1;strokeColor=#7F8C8D;fillColor=#ECECEC;" vertex="1" parent="1">
          <mxGeometry x="360" y="70" width="240" height="70" as="geometry"/>
        </mxCell>

        <mxCell id="az_lz4" value="Security / Logging" style="rounded=1;strokeColor=#7F8C8D;fillColor=#ECECEC;" vertex="1" parent="1">
          <mxGeometry x="620" y="70" width="240" height="70" as="geometry"/>
        </mxCell>

        <mxCell id="az_lz5" value="{workload}" style="rounded=1;strokeColor=#7F8C8D;fillColor=#ECECEC;" vertex="1" parent="1">
          <mxGeometry x="880" y="70" width="140" height="70" as="geometry"/>
        </mxCell>
"""

    inner = header + body + _overlay_cells(req.overlay_profile)
    return _mxfile_wrapper(f"Azure Landing Zone - {org} ({env})", inner)


# ------------------------------------------------------
# GCP Landing Zone
# ------------------------------------------------------
def generate_gcp_lz(req: DiagramRequest) -> str:
    org = req.org_name or "Organization"
    env = req.environment or "Environment"
    workload = req.workload_name or "Workload"

    header = f"""        <mxCell id="gcp_h1" value="GCP Landing Zone - {org} ({env})" style="rounded=1;fontStyle=1;strokeColor=#4285F4;fillColor=#E8F0FE;" vertex="1" parent="1">
          <mxGeometry x="80" y="40" width="960" height="120" as="geometry"/>
        </mxCell>"""

    body = f"""
        <mxCell id="gcp_h2" value="Organization Node" style="rounded=1;strokeColor=#95A5A6;fillColor=#ECF0F1;" vertex="1" parent="1">
          <mxGeometry x="100" y="70" width="220" height="70" as="geometry"/>
        </mxCell>

        <mxCell id="gcp_h3" value="Folder: Platform / Networking" style="rounded=1;strokeColor=#95A5A6;fillColor=#ECF0F1;" vertex="1" parent="1">
          <mxGeometry x="340" y="70" width="260" height="70" as="geometry"/>
        </mxCell>

        <mxCell id="gcp_h4" value="Folder: Security / Logging" style="rounded=1;strokeColor=#95A5A6;fillColor=#ECF0F1;" vertex="1" parent="1">
          <mxGeometry x="620" y="70" width="260" height="70" as="geometry"/>
        </mxCell>

        <mxCell id="gcp_h5" value="{workload}" style="rounded=1;strokeColor=#95A5A6;fillColor=#ECF0F1;" vertex="1" parent="1">
          <mxGeometry x="900" y="70" width="140" height="70" as="geometry"/>
        </mxCell>
"""

    inner = header + body + _overlay_cells(req.overlay_profile)
    return _mxfile_wrapper(f"GCP Landing Zone - {org} ({env})", inner)


# ------------------------------------------------------
# Simplified Network & Application diagrams (per cloud)
# ------------------------------------------------------
def generate_aws_network(req: DiagramRequest) -> str:
    org = req.org_name or "Organization"
    env = req.environment or "Environment"
    title = f"AWS Network Topology - {org} ({env})"

    cells = """        <mxCell id="aws_n1" value="AWS Network Topology" style="rounded=1;strokeColor=#232F3E;fillColor=#F4F6F6;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="80" y="40" width="960" height="80" as="geometry"/>
        </mxCell>"""

    return _mxfile_wrapper(title, cells + _overlay_cells(req.overlay_profile))


def generate_aws_app(req: DiagramRequest) -> str:
    org = req.org_name or "Organization"
    env = req.environment or "Environment"
    title = f"AWS Application Stack - {org} ({env})"

    cells = """        <mxCell id="aws_a1" value="AWS Application Stack" style="rounded=1;strokeColor=#232F3E;fillColor=#F4F6F6;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="80" y="40" width="960" height="80" as="geometry"/>
        </mxCell>"""

    return _mxfile_wrapper(title, cells + _overlay_cells(req.overlay_profile))


def generate_azure_network(req: DiagramRequest) -> str:
    org = req.org_name or "Organization"
    env = req.environment or "Environment"
    title = f"Azure Network Topology - {org} ({env})"

    cells = """        <mxCell id="az_n1" value="Azure Network Topology" style="rounded=1;strokeColor=#0072C6;fillColor=#E8F4FF;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="80" y="40" width="960" height="80" as="geometry"/>
        </mxCell>"""

    return _mxfile_wrapper(title, cells + _overlay_cells(req.overlay_profile))


def generate_azure_app(req: DiagramRequest) -> str:
    org = req.org_name or "Organization"
    env = req.environment or "Environment"
    title = f"Azure Application Stack - {org} ({env})"

    cells = """        <mxCell id="az_a1" value="Azure Application Stack" style="rounded=1;strokeColor=#0072C6;fillColor=#E8F4FF;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="80" y="40" width="960" height="80" as="geometry"/>
        </mxCell>"""

    return _mxfile_wrapper(title, cells + _overlay_cells(req.overlay_profile))


def generate_gcp_network(req: DiagramRequest) -> str:
    org = req.org_name or "Organization"
    env = req.environment or "Environment"
    title = f"GCP Network Topology - {org} ({env})"

    cells = """        <mxCell id="gcp_n1" value="GCP Network Topology" style="rounded=1;strokeColor=#4285F4;fillColor=#E8F0FE;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="80" y="40" width="960" height="80" as="geometry"/>
        </mxCell>"""

    return _mxfile_wrapper(title, cells + _overlay_cells(req.overlay_profile))


def generate_gcp_app(req: DiagramRequest) -> str:
    org = req.org_name or "Organization"
    env = req.environment or "Environment"
    title = f"GCP Application Stack - {org} ({env})"

    cells = """        <mxCell id="gcp_a1" value="GCP Application Stack" style="rounded=1;strokeColor=#4285F4;fillColor=#E8F0FE;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="80" y="40" width="960" height="80" as="geometry"/>
        </mxCell>"""

    return _mxfile_wrapper(title, cells + _overlay_cells(req.overlay_profile))


# ------------------------------------------------------
# MAIN ROUTE – single diagram
# ------------------------------------------------------
@router.post(
    "/v1/diagram/generate",
    summary="Generate cloud architecture diagram",
)
def generate(req: DiagramRequest):
    cloud = req.cloud.lower()
    dtype = req.diagram_type.lower()

    # --- AWS ---
    if cloud == "aws":
        if dtype == "landing_zone":
            return {"xml": generate_aws_lz(req)}
        if dtype == "network":
            return {"xml": generate_aws_network(req)}
        if dtype == "application":
            return {"xml": generate_aws_app(req)}

    # --- Azure ---
    if cloud == "azure":
        if dtype == "landing_zone":
            return {"xml": generate_azure_lz(req)}
        if dtype == "network":
            return {"xml": generate_azure_network(req)}
        if dtype == "application":
            return {"xml": generate_azure_app(req)}

    # --- GCP ---
    if cloud == "gcp":
        if dtype == "landing_zone":
            return {"xml": generate_gcp_lz(req)}
        if dtype == "network":
            return {"xml": generate_gcp_network(req)}
        if dtype == "application":
            return {"xml": generate_gcp_app(req)}

    raise HTTPException(status_code=400, detail="Unsupported cloud or diagram type")


# ------------------------------------------------------
# PACKAGE ROUTE – multi-diagram ZIP bundle
# ------------------------------------------------------
@router.post(
    "/v1/diagram/package",
    summary="Generate multi-diagram ZIP bundle",
)
def generate_package(pkg: DiagramPackageRequest):
    """
    Generate a ZIP containing multiple .drawio diagrams.

    By default this will create AWS/Azure/GCP × (landing_zone, network, application),
    skipping any unsupported combinations.
    """
    clouds = [c.lower() for c in (pkg.clouds or ["aws", "azure", "gcp"])]
    types = [t.lower() for t in (pkg.include_types or ["landing_zone", "network", "application"])]

    buf = io.BytesIO()
    file_count = 0

    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for cloud in clouds:
            for dtype in types:
                try:
                    req = DiagramRequest(
                        cloud=cloud,
                        diagram_type=dtype,
                        org_name=pkg.org_name,
                        environment=pkg.environment,
                        workload_name=pkg.workload_name,
                        overlay_profile=pkg.overlay_profile,
                    )
                    result = generate(req)  # reuse single-diagram logic
                    xml = result["xml"]
                except HTTPException:
                    # Skip unsupported combos instead of failing the whole package
                    continue

                fname = _build_diagram_filename(cloud, dtype, pkg)
                zf.writestr(fname, xml)
                file_count += 1

    buf.seek(0)
    zip_b64 = base64.b64encode(buf.read()).decode("ascii")
    zip_name = _build_zip_name(pkg)

    return {
        "zip_filename": zip_name,
        "zip_base64": zip_b64,
        "file_count": file_count,
    }
