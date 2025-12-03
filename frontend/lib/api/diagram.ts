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

const API_BASE =
  (import.meta as any).env.VITE_BACKEND_URL || "http://localhost:8000";

export async function enrichDiagram(
  req: DiagramEnrichRequest,
): Promise<DiagramEnrichResponse> {
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
