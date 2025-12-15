// src/api/analysisRunV1.ts
// Client for Analysis v1 endpoints that read from the in-memory run registry.
// These endpoints are intentionally lightweight and demo-safe.

export interface AnalysisRunV1Overview {
  run: {
    id: string;
    created_at: string;
    name: string;
    source: string;
    state: string;
  };
  counts: {
    servers: number;
    storage: number;
    databases: number;
    applications: number;
    dependencies: number;
    network: number;
  };
  readiness: {
    has_servers: boolean;
    has_other_slice: boolean;
    ready_for_analysis: boolean;
  };
  findings: string[];
  version: string;
}

export interface AnalysisRunV1Segmentation {
  run_id: string;
  totals: {
    servers: number;
  };
  segments: {
    os_family: any[];
    environment: any[];
    cpu_cores_bucket: any[];
    ram_gb_bucket: any[];
  };
  note?: string;
  version: string;
}

// nginx proxies /api/... -> http://127.0.0.1:8000/...
const API_BASE = "/api/v1/analysis";

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail: string | undefined;
    try {
      const data = await res.json();
      detail = data?.detail;
    } catch {
      // ignore JSON parse errors
    }
    throw new Error(
      detail || `Request failed with status ${res.status} ${res.statusText}`
    );
  }
  return (await res.json()) as T;
}

/**
 * GET /v1/analysis/run/{run_id}/overview
 */
export async function fetchAnalysisRunV1Overview(
  runId: string
): Promise<AnalysisRunV1Overview> {
  const res = await fetch(
    `${API_BASE}/run/${encodeURIComponent(runId)}/overview`
  );
  return handleResponse<AnalysisRunV1Overview>(res);
}

/**
 * GET /v1/analysis/run/{run_id}/servers/segmentation
 */
export async function fetchAnalysisRunV1Segmentation(
  runId: string
): Promise<AnalysisRunV1Segmentation> {
  const res = await fetch(
    `${API_BASE}/run/${encodeURIComponent(runId)}/servers/segmentation`
  );
  return handleResponse<AnalysisRunV1Segmentation>(res);
}
