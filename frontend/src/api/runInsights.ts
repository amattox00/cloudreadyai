// src/api/runInsights.ts

export interface ServersSummary {
  row_count: number;
  environment_counts: Record<string, number>;
  role_counts: Record<string, number>;
  os_counts: Record<string, number>;
  rscore_summary?: {
    num_scored: number;
    distribution: Record<string, number>;
    average_scores: {
      rehost: number;
      replatform: number;
      refactor: number;
      repurchase: number;
      retire: number;
      retain: number;
    };
  };
}

export interface ServerRScoreRow {
  hostname: string;
  role: string | null;
  os: string | null;
  environment: string | null;
  cpu_usage: number | null;
  ram_usage: number | null;
  rehost: number;
  replatform: number;
  refactor: number;
  repurchase: number;
  retire: number;
  retain: number;
  final_recommendation: string;
}

export interface WorkloadSummaryRow {
  id: number;
  name: string;
  environment: string | null;
  tier: string | null;
  utilization_cpu: number | null;
  utilization_memory: number | null;
  migration_pattern: string | null;
}

const API_BASE = "/api/runs";

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

export async function fetchServersSummary(
  runId: string
): Promise<ServersSummary> {
  const res = await fetch(
    `${API_BASE}/${encodeURIComponent(runId)}/servers/summary`
  );
  return handleResponse<ServersSummary>(res);
}

export async function fetchServerRscores(
  runId: string
): Promise<ServerRScoreRow[]> {
  const res = await fetch(
    `${API_BASE}/${encodeURIComponent(runId)}/servers/rscores`
  );
  return handleResponse<ServerRScoreRow[]>(res);
}

export async function fetchWorkloadsSummary(
  runId: string
): Promise<WorkloadSummaryRow[]> {
  const res = await fetch(
    `${API_BASE}/${encodeURIComponent(runId)}/workloads`
  );
  return handleResponse<WorkloadSummaryRow[]>(res);
}
