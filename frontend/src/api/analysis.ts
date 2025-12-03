export type WorkloadComponent = {
  id: number;
  component_type: string;
  component_ref_id: string;
};

export type Workload = {
  id: number;
  run_id: string;
  name: string;
  type: string;
  environment?: string | null;
  criticality?: string | null;
  complexity_score?: number | null;
  risk_score?: number | null;
  created_at: string;
  updated_at: string;
  components: WorkloadComponent[];
};

export type WorkloadListResponse = {
  run_id: string;
  workloads: Workload[];
};

const API_BASE =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/v1";

export async function fetchWorkloads(
  runId: string
): Promise<WorkloadListResponse> {
  const res = await fetch(`${API_BASE}/runs/${runId}/analysis/workloads`);
  if (!res.ok) {
    throw new Error(`Failed to load workloads for run ${runId}`);
  }
  return res.json();
}

export async function rebuildWorkloads(
  runId: string
): Promise<WorkloadListResponse> {
  const res = await fetch(
    `${API_BASE}/runs/${runId}/analysis/workloads/rebuild`,
    {
      method: "POST",
    }
  );
  if (!res.ok) {
    throw new Error(`Failed to rebuild workloads for run ${runId}`);
  }
  return res.json();
}
