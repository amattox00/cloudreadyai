#!/usr/bin/env bash
set -euo pipefail

ROOT="$HOME/cloudreadyai"
echo "Using ROOT: $ROOT"

mkdir -p "$ROOT/backend/app/modules/phase7e"
mkdir -p "$ROOT/backend/app/worker"
mkdir -p "$ROOT/backend/app/routers"
mkdir -p "$ROOT/frontend/lib/api"
mkdir -p "$ROOT/frontend/components/diagram"
mkdir -p "$ROOT/frontend/app/diagrams/enrich"

echo "Writing backend Phase 7E files..."

cat <<'PY1' > "$ROOT/backend/app/modules/phase7e/__init__.py"
from .models import (
    DiagramAutoLayoutRequest,
    DiagramZeroTrustRequest,
    DiagramEnrichRequest,
    DiagramEnrichResponse,
)
from .service import (
    apply_auto_layout,
    apply_zero_trust_overlays,
    enrich_diagram,
)
PY1

cat <<'PY2' > "$ROOT/backend/app/modules/phase7e/models.py"
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class DiagramMetadata(BaseModel):
    cloud: str = Field(..., description="aws | azure | gcp | hybrid")
    use_case: str = Field(
        "landing_zone",
        description="Workload type such as landing_zone, app_migration, data_lake, etc.",
    )
    compliance: Optional[str] = Field(
        None, description="fedramp, dod, nist80053, hipaa, etc."
    )
    environment: Optional[str] = Field(None, description="Dev, Test, Stage, Prod")
    org_name: Optional[str] = None
    workload_name: Optional[str] = None
    opportunity_id: Optional[str] = None
    version_tag: Optional[str] = None


class DiagramAutoLayoutRequest(BaseModel):
    xml: str = Field(..., description="Original draw.io/mxgraph XML")
    metadata: DiagramMetadata


class DiagramZeroTrustRequest(BaseModel):
    xml: str = Field(..., description="Input XML (already auto-laid out or raw)")
    metadata: DiagramMetadata


class DiagramEnrichRequest(BaseModel):
    xml: str = Field(..., description="Input XML (may already include layout/overlays)")
    metadata: DiagramMetadata
    enable_auto_layout: bool = True
    enable_zero_trust: bool = True
    include_recommendations: bool = True


class DiagramRecommendation(BaseModel):
    category: str
    title: str
    description: str
    severity: str = "info"
    tags: List[str] = []


class DiagramEnrichResponse(BaseModel):
    xml: str
    metadata: DiagramMetadata
    recommendations: List[DiagramRecommendation] = []
    extras: Dict[str, Any] = {}
PY2

cat <<'PY3' > "$ROOT/backend/app/modules/phase7e/auto_layout.py"
from xml.etree import ElementTree as ET
from typing import Tuple


def _iter_vertices(root: ET.Element):
    for cell in root.findall(".//mxCell"):
        if cell.get("vertex") == "1":
            yield cell


def _ensure_geometry(cell: ET.Element) -> ET.Element:
    geom = cell.find("mxGeometry")
    if geom is None:
        geom = ET.SubElement(cell, "mxGeometry")
        geom.set("width", "120")
        geom.set("height", "60")
        geom.set("as", "geometry")
    return geom


def _grid_position(index: int, cols: int = 4, x_step: int = 220, y_step: int = 140) -> Tuple[int, int]:
    row = index // cols
    col = index % cols
    x = 40 + col * x_step
    y = 40 + row * y_step
    return x, y


def apply_grid_layout(xml_str: str) -> str:
    tree = ET.fromstring(xml_str)
    graph_model = tree.find(".//mxGraphModel")
    if graph_model is None:
        return xml_str

    root = graph_model.find("root")
    if root is None:
        return xml_str

    for i, cell in enumerate(_iter_vertices(root)):
        geom = _ensure_geometry(cell)
        x, y = _grid_position(i)
        geom.set("x", str(x))
        geom.set("y", str(y))

    return ET.tostring(tree, encoding="unicode")
PY3

cat <<'PY4' > "$ROOT/backend/app/modules/phase7e/zero_trust.py"
from xml.etree import ElementTree as ET
from .models import DiagramMetadata

ZERO_TRUST_ZONE_STYLES = {
    "default": "shape=swimlane;horizontal=0;rounded=1;opacity=20;fillColor=#dae8fc;",
    "identity": "shape=swimlane;horizontal=0;rounded=1;opacity=15;fillColor=#e1d5e7;",
    "data": "shape=swimlane;horizontal=0;rounded=1;opacity=15;fillColor=#d5e8d4;",
}


def _add_zone(
    root: ET.Element,
    zone_id: str,
    label: str,
    style_key: str,
    x: int,
    y: int,
    width: int,
    height: int,
):
    cell = ET.SubElement(root, "mxCell")
    cell.set("id", zone_id)
    cell.set("value", label)
    cell.set("style", ZERO_TRUST_ZONE_STYLES.get(style_key, ZERO_TRUST_ZONE_STYLES["default"]))
    cell.set("vertex", "1")
    cell.set("parent", "1")

    geom = ET.SubElement(cell, "mxGeometry")
    geom.set("x", str(x))
    geom.set("y", str(y))
    geom.set("width", str(width))
    geom.set("height", str(height))
    geom.set("as", "geometry")


def apply_zero_trust(xml_str: str, metadata: DiagramMetadata) -> str:
    tree = ET.fromstring(xml_str)
    graph_model = tree.find(".//mxGraphModel")
    if graph_model is None:
        return xml_str

    root = graph_model.find("root")
    if root is None:
        return xml_str

    base_x, base_y, width, height = 20, 20, 1200, 800

    cloud = (metadata.cloud or "aws").lower()
    compliance = (metadata.compliance or "").lower()

    zone_label = {
        "aws": "AWS Application & Data Plane",
        "azure": "Azure Application & Data Plane",
        "gcp": "GCP Application & Data Plane",
    }.get(cloud, "Application & Data Plane")

    identity_label = "Identity & Policy Plane"
    if "dod" in compliance or "il" in compliance:
        identity_label = "DoD Identity / Policy Plane"

    data_label = "Data & Logging Plane"

    _add_zone(root, "zt_app_plane", zone_label, "default", base_x, base_y, width, int(height * 0.6))
    _add_zone(
        root,
        "zt_identity_plane",
        identity_label,
        "identity",
        base_x + 10,
        base_y - 80,
        int(width * 0.6),
        70,
    )
    _add_zone(
        root,
        "zt_data_plane",
        data_label,
        "data",
        base_x + int(width * 0.65),
        base_y - 80,
        int(width * 0.3),
        70,
    )

    return ET.tostring(tree, encoding="unicode")
PY4

cat <<'PY5' > "$ROOT/backend/app/modules/phase7e/enrichment.py"
from typing import List
from .models import DiagramMetadata, DiagramRecommendation


def _aws_base_recommendations(meta: DiagramMetadata) -> List[DiagramRecommendation]:
    recs: List[DiagramRecommendation] = []

    recs.append(
        DiagramRecommendation(
            category="network",
            title="Add AWS Transit Gateway for multi-account connectivity",
            description=(
                "For multi-account landing zones, use AWS Transit Gateway to centralize "
                "VPC connectivity and simplify routing between security, shared services, "
                "and workload accounts."
            ),
            severity="info",
            tags=["aws", "networking", "transit-gateway"],
        )
    )

    recs.append(
        DiagramRecommendation(
            category="security",
            title="Front-end public applications with AWS WAF + CloudFront",
            description=(
                "Place internet-facing workloads behind CloudFront and AWS WAF to improve "
                "security posture, performance, and DDoS mitigation."
            ),
            severity="warning",
            tags=["aws", "waf", "cloudfront", "zero-trust"],
        )
    )

    if (meta.compliance or "").lower() in {"dod", "fedramp"}:
        recs.append(
            DiagramRecommendation(
                category="compliance",
                title="Use AWS Config and Security Hub for FedRAMP / DoD control visibility",
                description=(
                    "Enable AWS Config and AWS Security Hub across accounts to continuously "
                    "monitor configuration drifts and map findings to frameworks like "
                    "FedRAMP and NIST 800-53."
                ),
                severity="info",
                tags=["aws", "fedramp", "config", "security-hub"],
            )
        )

    return recs


def _azure_base_recommendations(meta: DiagramMetadata) -> List[DiagramRecommendation]:
    recs: List[DiagramRecommendation] = []

    recs.append(
        DiagramRecommendation(
            category="network",
            title="Use hub-and-spoke with Azure Firewall or NVA",
            description=(
                "Adopt a hub-and-spoke network topology with Azure Firewall or a "
                "network virtual appliance in the hub VNet for centralized security and routing."
            ),
            severity="info",
            tags=["azure", "networking", "hub-spoke"],
        )
    )

    recs.append(
        DiagramRecommendation(
            category="identity",
            title="Enable Conditional Access and PIM via Entra ID",
            description=(
                "Apply Conditional Access and Privileged Identity Management in Entra ID "
                "for strong Zero Trust enforcement, particularly for admin roles."
            ),
            severity="warning",
            tags=["azure", "identity", "zero-trust"],
        )
    )

    return recs


def _gcp_base_recommendations(meta: DiagramMetadata) -> List[DiagramRecommendation]:
    recs: List[DiagramRecommendation] = []

    recs.append(
        DiagramRecommendation(
            category="network",
            title="Use Shared VPC for centralized control",
            description=(
                "Use Shared VPC to centralize network management and delegate service "
                "projects for workloads while keeping security enforcement in the host project."
            ),
            severity="info",
            tags=["gcp", "networking", "shared-vpc"],
        )
    )

    recs.append(
        DiagramRecommendation(
            category="security",
            title="Leverage Cloud Armor and Security Command Center",
            description=(
                "Use Cloud Armor for WAF and DDoS protection in front of external "
                "applications, and Security Command Center for centralized security posture management."
            ),
            severity="warning",
            tags=["gcp", "cloud-armor", "scc"],
        )
    )

    return recs


def build_recommendations(metadata: DiagramMetadata) -> List[DiagramRecommendation]:
    cloud = (metadata.cloud or "").lower()
    recs: List[DiagramRecommendation] = []

    if cloud == "aws":
        recs.extend(_aws_base_recommendations(metadata))
    elif cloud == "azure":
        recs.extend(_azure_base_recommendations(metadata))
    elif cloud == "gcp":
        recs.extend(_gcp_base_recommendations(metadata))
    else:
        recs.append(
            DiagramRecommendation(
                category="security",
                title="Ensure centralized logging and monitoring",
                description=(
                    "Enable centralized logging, metrics, and alerting across all workloads "
                    "to detect anomalies and enforce Zero Trust policies."
                ),
                severity="info",
                tags=["observability", "logging"],
            )
        )

    recs.append(
        DiagramRecommendation(
            category="dr",
            title="Regularly test failover and recovery paths",
            description=(
                "Document and rehearse DR runbooks. Validate RPO/RTO using automated "
                "failover drills where possible."
            ),
            severity="info",
            tags=["dr", "testing"],
        )
    )

    return recs
PY5

cat <<'PY6' > "$ROOT/backend/app/modules/phase7e/service.py"
from .models import (
    DiagramAutoLayoutRequest,
    DiagramZeroTrustRequest,
    DiagramEnrichRequest,
    DiagramEnrichResponse,
)
from .auto_layout import apply_grid_layout
from .zero_trust import apply_zero_trust
from .enrichment import build_recommendations


def apply_auto_layout(req: DiagramAutoLayoutRequest) -> str:
    return apply_grid_layout(req.xml)


def apply_zero_trust_overlays(req: DiagramZeroTrustRequest) -> str:
    return apply_zero_trust(req.xml, req.metadata)


def enrich_diagram(req: DiagramEnrichRequest) -> DiagramEnrichResponse:
    xml = req.xml

    if req.enable_auto_layout:
        xml = apply_grid_layout(xml)

    if req.enable_zero_trust:
        xml = apply_zero_trust(xml, req.metadata)

    recommendations = build_recommendations(req.metadata) if req.include_recommendations else []

    return DiagramEnrichResponse(
        xml=xml,
        metadata=req.metadata,
        recommendations=recommendations,
        extras={
            "auto_layout_applied": req.enable_auto_layout,
            "zero_trust_applied": req.enable_zero_trust,
        },
    )
PY6

echo "Writing backend router and worker..."

cat <<'PY7' > "$ROOT/backend/app/routers/phase7e.py"
from fastapi import APIRouter
from ..modules.phase7e.models import (
    DiagramAutoLayoutRequest,
    DiagramZeroTrustRequest,
    DiagramEnrichRequest,
    DiagramEnrichResponse,
)
from ..modules.phase7e.service import (
    apply_auto_layout,
    apply_zero_trust_overlays,
    enrich_diagram,
)

router = APIRouter(prefix="/v1/diagram", tags=["phase7e"])


@router.post("/auto-layout", response_model=str, summary="Apply CSP auto-layout to diagram XML")
async def auto_layout_endpoint(payload: DiagramAutoLayoutRequest) -> str:
    return apply_auto_layout(payload)


@router.post("/zero-trust", response_model=str, summary="Apply Zero Trust overlays to diagram XML")
async def zero_trust_endpoint(payload: DiagramZeroTrustRequest) -> str:
    return apply_zero_trust_overlays(payload)


@router.post("/enrich", response_model=DiagramEnrichResponse, summary="AI-driven diagram enrichment")
async def enrich_endpoint(payload: DiagramEnrichRequest) -> DiagramEnrichResponse:
    return enrich_diagram(payload)
PY7

cat <<'PY8' > "$ROOT/backend/app/worker/phase7e_tasks.py"
from typing import Dict, Any
from app.modules.phase7e.models import DiagramEnrichRequest
from app.modules.phase7e.service import enrich_diagram


def enrich_diagram_task(payload: Dict[str, Any]) -> Dict[str, Any]:
    req = DiagramEnrichRequest(**payload)
    resp = enrich_diagram(req)
    return resp.dict()
PY8

echo "Writing frontend Phase 7E files..."

cat <<'TS1' > "$ROOT/frontend/lib/api/diagram.ts"
export interface DiagramMetadata {
  cloud: "aws" | "azure" | "gcp" | "hybrid" | string;
  use_case?: string;
  compliance?: string;
  environment?: string;
  org_name?: string;
  workload_name?: string;
  opportunity_id?: string;
  version_tag?: string;
}

export interface DiagramEnrichRequest {
  xml: string;
  metadata: DiagramMetadata;
  enable_auto_layout?: boolean;
  enable_zero_trust?: boolean;
  include_recommendations?: boolean;
}

export interface DiagramRecommendation {
  category: string;
  title: string;
  description: string;
  severity: "info" | "warning" | "critical";
  tags: string[];
}

export interface DiagramEnrichResponse {
  xml: string;
  metadata: DiagramMetadata;
  recommendations: DiagramRecommendation[];
  extras: Record<string, any>;
}

const API_BASE = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export async function enrichDiagram(req: DiagramEnrichRequest): Promise<DiagramEnrichResponse> {
  const res = await fetch(`${API_BASE}/v1/diagram/enrich`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });

  if (!res.ok) {
    throw new Error(`Failed to enrich diagram: ${res.status}`);
  }

  return (await res.json()) as DiagramEnrichResponse;
}
TS1

cat <<'TS2' > "$ROOT/frontend/components/diagram/DiagramPreview.tsx"
"use client";

import React, { useEffect, useRef } from "react";

interface DiagramPreviewProps {
  xml: string;
  height?: number;
}

/**
 * Simple draw.io iframe embed that loads XML into the editor in "embed" mode.
 */
export const DiagramPreview: React.FC<DiagramPreviewProps> = ({ xml, height = 600 }) => {
  const iframeRef = useRef<HTMLIFrameElement | null>(null);

  useEffect(() => {
    const iframe = iframeRef.current;
    if (!iframe) return;

    const listener = (event: MessageEvent) => {
      if (event.source !== iframe.contentWindow) return;
      if (!event.data || typeof event.data !== "string") return;

      if (event.data === "ready") {
        const msg = JSON.stringify({
          action: "load",
          xml,
        });
        iframe.contentWindow?.postMessage(msg, "*");
      }
    };

    window.addEventListener("message", listener);
    return () => window.removeEventListener("message", listener);
  }, [xml]);

  const drawIoUrl =
    "https://embed.diagrams.net/?embed=1&ui=min&spin=1&proto=json&noSaveBtn=1&noExitBtn=1";

  return (
    <iframe
      ref={iframeRef}
      src={drawIoUrl}
      style={{ width: "100%", border: "1px solid #ccc", height }}
      aria-label="Diagram preview"
    />
  );
};
TS2

cat <<'TS3' > "$ROOT/frontend/app/diagrams/enrich/page.tsx"
"use client";

import React, { useState } from "react";
import { DiagramPreview } from "@/components/diagram/DiagramPreview";
import { enrichDiagram, DiagramMetadata, DiagramEnrichResponse } from "@/lib/api/diagram";

const defaultXml = `<mxfile><diagram id="cloud-diagram" name="Cloud Diagram"><mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/></root></mxGraphModel></diagram></mxfile>`;

const defaultMetadata: DiagramMetadata = {
  cloud: "aws",
  use_case: "landing_zone",
  compliance: "dod",
  environment: "Prod",
  org_name: "5NINE Data Solutions",
  workload_name: "CloudReadyAI",
};

export default function DiagramEnrichPage() {
  const [xml, setXml] = useState<string>(defaultXml);
  const [response, setResponse] = useState<DiagramEnrichResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleEnrich = async () => {
    setLoading(true);
    setError(null);
    try {
      const resp = await enrichDiagram({
        xml,
        metadata: defaultMetadata,
        enable_auto_layout: true,
        enable_zero_trust: true,
        include_recommendations: true,
      });
      setResponse(resp);
      setXml(resp.xml);
    } catch (err: any) {
      setError(err.message || "Failed to enrich diagram");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-2xl font-semibold">Phase 7E – AI-driven Diagram Enrichment</h1>

      <div className="flex flex-col gap-4 md:flex-row">
        <div className="md:w-1/2 space-y-2">
          <label className="font-medium">Input / Enriched XML</label>
          <textarea
            className="w-full h-72 border rounded p-2 text-xs font-mono"
            value={xml}
            onChange={(e) => setXml(e.target.value)}
          />
          <button
            onClick={handleEnrich}
            disabled={loading}
            className="px-4 py-2 rounded border text-sm disabled:opacity-60"
          >
            {loading ? "Enriching..." : "Run Phase 7E Enrichment"}
          </button>
          {error && <p className="text-red-600 text-sm mt-1">{error}</p>}
        </div>

        <div className="md:w-1/2">
          <DiagramPreview xml={xml} />
        </div>
      </div>

      {response?.recommendations?.length ? (
        <div className="mt-4">
          <h2 className="text-xl font-semibold mb-2">Recommendations</h2>
          <ul className="space-y-2">
            {response.recommendations.map((r, idx) => (
              <li key={idx} className="border rounded p-2 text-sm">
                <div className="flex justify-between items-center">
                  <span className="font-semibold">{r.title}</span>
                  <span className="text-xs uppercase tracking-wide">{r.severity}</span>
                </div>
                <p className="text-xs mt-1">{r.description}</p>
                {r.tags?.length ? (
                  <div className="mt-1 flex flex-wrap gap-1">
                    {r.tags.map((tag) => (
                      <span
                        key={tag}
                        className="text-[10px] px-2 py-0.5 border rounded-full"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                ) : null}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </div>
  );
}
TS3

echo "Phase 7E files written."
echo "Reminder: ensure backend/app/main.py includes:  app.include_router(phase7e.router)"

