// src/api/analysis.ts

export interface EnvironmentBreakdown {
  name: string;
  count: number;
}

export interface OSSummary {
  family: string;
  count: number;
  legacy_count: number;
}

export interface ReadinessSummary {
  ready_for_rehost: number;
  needs_modernization: number;
  needs_investigation: number;
}

export interface AnalysisSummary {
  run_id: string;
  total_servers: number;
  environments: EnvironmentBreakdown[];
  os_summary: OSSummary[];
  legacy_server_count: number;
  modern_server_count: number;
  readiness: ReadinessSummary;
  notes: string[];
}

export interface RecommendationItem {
  server_id: string;
  hostname: string | null;
  ip: string | null;
  environment: string | null;
  os: string | null;
  strategy: string;
  risk_level: string;
  wave: number;
  summary: string;
  estimated_monthly_savings: number | null;
  target_platform: string | null;
}

export interface AnalysisRecommendations {
  run_id: string;
  total_recommendations: number;
  items: RecommendationItem[];
}

// IMPORTANT: match how nginx is already proxying the backend.
// Existing working calls (run registry, etc.) go to /v1/..., not /api/v1/...
const API_BASE = "/v1/analysis";

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail: string | undefined;
    try {
      const data = await res.json();
      detail = (data as any)?.detail;
    } catch {
      // ignore JSON parse errors; fall back to status text
    }
    throw new Error(
      detail || `Request failed with status ${res.status} ${res.statusText}`
    );
  }
  return (await res.json()) as T;
}

export async function fetchAnalysisSummary(
  runId: string
): Promise<AnalysisSummary> {
  const res = await fetch(
    `${API_BASE}/${encodeURIComponent(runId)}/summary`
  );
  return handleResponse<AnalysisSummary>(res);
}

export async function fetchAnalysisRecommendations(
  runId: string
): Promise<AnalysisRecommendations> {
  const res = await fetch(
    `${API_BASE}/${encodeURIComponent(runId)}/recommendations`
  );
  return handleResponse<AnalysisRecommendations>(res);
}
