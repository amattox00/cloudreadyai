// src/api/runRegistry.ts
// Unified client for the run registry APIs used by Dashboard, Runs, and Analysis.

export interface RunRecord {
  run_id: string;
  name: string | null;
  status?: string | null;
  customer?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
}

// AnalysisPage expects RunRegistryItem; alias it to RunRecord
export type RunRegistryItem = RunRecord;

export interface RunListResponse {
  runs: RunRecord[];
}

// nginx proxies /api/... -> http://127.0.0.1:8000/...
const API_BASE = "/api/v1/run_registry";

async function handleJson<T>(res: Response): Promise<T> {
  const text = await res.text();

  if (!res.ok) {
    let detail = text || res.statusText;
    try {
      const parsed = text ? JSON.parse(text) : null;
      if (parsed && typeof parsed === "object") {
        detail = JSON.stringify(parsed);
      }
    } catch {
      // ignore JSON parse errors, keep raw text
    }
    throw new Error(`Request failed (${res.status}): ${detail}`);
  }

  if (!text) {
    // @ts-expect-error allow void/empty bodies
    return {};
  }

  return JSON.parse(text) as T;
}

/**
 * GET /api/v1/run_registry
 * Returns the list of runs. We support both:
 *   { "runs": [...] }   (new-style API)
 *   [ ... ]             (older/simple API)
 */
export async function listRuns(): Promise<RunRecord[]> {
  const res = await fetch(API_BASE, {
    method: "GET",
    headers: { Accept: "application/json" },
  });

  const data = await handleJson<RunListResponse | RunRecord[]>(res);

  if (Array.isArray(data)) {
    return data;
  }

  if (data && Array.isArray((data as RunListResponse).runs)) {
    return (data as RunListResponse).runs;
  }

  return [];
}

/**
 * Alias used by AnalysisPage.
 * fetchRunRegistry -> just returns the list of runs.
 */
export async function fetchRunRegistry(): Promise<RunRegistryItem[]> {
  return listRuns();
}

/**
 * POST /api/v1/run_registry
 *
 * The backend currently expects a JSON body with:
 *   - name   (string, required)
 *   - source (string, required)
 *
 * For now we send an auto-generated name and a fixed source of "dashboard".
 * Later we can wire this to a text input so the user can type a friendly name.
 */
export async function createRun(): Promise<RunRecord> {
  const name = `Assessment ${new Date()
    .toISOString()
    .slice(0, 19)
    .replace("T", " ")}`;

  const res = await fetch(API_BASE, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify({
      name,
      source: "dashboard",
    }),
  });

  return handleJson<RunRecord>(res);
}

/**
 * DELETE /api/v1/run_registry/{run_id}
 * If the backend doesn't implement DELETE yet, a 404 is treated as "already gone".
 */
export async function deleteRun(runId: string): Promise<void> {
  const url = `${API_BASE}/${encodeURIComponent(runId)}`;
  const res = await fetch(url, {
    method: "DELETE",
    headers: { Accept: "application/json" },
  });

  if (!res.ok && res.status !== 404) {
    const text = await res.text();
    throw new Error(
      `Delete failed (${res.status}): ${text || res.statusText}`,
    );
  }
}
