// src/api/runRegistry.ts
// Unified client for the run registry APIs used by Dashboard, Runs, and Analysis.
// IMPORTANT: We currently have two run registries behind the same endpoint:
//
// 1) In-memory UI registry (app/routers/runs.py) -> returns an ARRAY of items like:
//    { id, created_at, name, source, state, servers_ingested, ... }
//
// 2) DB registry (app/routers/run_registry.py) -> returns { runs: [ { run_id, ... } ] }
//
// This client normalizes both into a single shape with a stable `id`.

export type RawInMemoryRun = {
  id: string;
  created_at?: string | null;
  name?: string | null;
  source?: string | null;
  state?: string | null;

  servers_ingested?: number;
  storage_ingested?: number;
  network_ingested?: number;
  databases_ingested?: number;
  applications_ingested?: number;
  dependencies_ingested?: number;
};

export type RawDbRun = {
  run_id: string;
  name?: string | null;
  status?: string | null;
  customer?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
};

export interface RunRegistryItem {
  // Normalized ID used everywhere in the UI
  id: string;

  // Optional raw DB run_id (for reference)
  run_id?: string;

  name?: string | null;
  created_at?: string | null;

  // Optional helpful fields (present in in-memory registry)
  source?: string | null;
  state?: string | null;

  servers_ingested?: number;
  storage_ingested?: number;
  network_ingested?: number;
  databases_ingested?: number;
  applications_ingested?: number;
  dependencies_ingested?: number;

  // Optional DB fields
  status?: string | null;
  customer?: string | null;
  updated_at?: string | null;
}

export interface RunListResponse {
  runs: RawDbRun[];
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

function normalizeRun(r: RawInMemoryRun | RawDbRun): RunRegistryItem {
  // In-memory
  if ((r as any).id) {
    const x = r as RawInMemoryRun;
    return {
      id: x.id,
      name: x.name ?? null,
      created_at: x.created_at ?? null,
      source: x.source ?? null,
      state: x.state ?? null,
      servers_ingested: x.servers_ingested ?? 0,
      storage_ingested: x.storage_ingested ?? 0,
      network_ingested: x.network_ingested ?? 0,
      databases_ingested: x.databases_ingested ?? 0,
      applications_ingested: x.applications_ingested ?? 0,
      dependencies_ingested: x.dependencies_ingested ?? 0,
    };
  }

  // DB
  const y = r as RawDbRun;
  return {
    id: y.run_id,
    run_id: y.run_id,
    name: y.name ?? null,
    created_at: y.created_at ?? null,
    status: y.status ?? null,
    customer: y.customer ?? null,
    updated_at: y.updated_at ?? null,
  };
}

/**
 * GET /api/v1/run_registry
 * Supports:
 *   { "runs": [...] }   (DB registry)
 *   [ ... ]             (in-memory registry)
 */
export async function fetchRunRegistry(): Promise<RunRegistryItem[]> {
  const res = await fetch(API_BASE, {
    method: "GET",
    headers: { Accept: "application/json" },
  });

  const data = await handleJson<RunListResponse | RawInMemoryRun[] | RawDbRun[]>(
    res
  );

  if (Array.isArray(data)) {
    return data.map(normalizeRun);
  }

  const maybe = data as RunListResponse;
  if (maybe && Array.isArray(maybe.runs)) {
    return maybe.runs.map(normalizeRun);
  }

  return [];
}

/**
 * POST /api/v1/run_registry
 *
 * The in-memory backend expects:
 *   - name (string)
 *   - source (string)
 *
 * The DB backend currently expects NO body, but this call is mainly for UI flow,
 * so we keep the in-memory contract. If DB is behind this endpoint, it will
 * likely reject; that’s OK for now.
 */
export async function createRun(): Promise<RunRegistryItem> {
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

  const raw = await handleJson<RawInMemoryRun | RawDbRun>(res);
  return normalizeRun(raw);
}

/**
 * DELETE /api/v1/run_registry/{id}
 * If the backend doesn't implement DELETE yet, a 404 is treated as "already gone".
 */
export async function deleteRun(id: string): Promise<void> {
  const url = `${API_BASE}/${encodeURIComponent(id)}`;
  const res = await fetch(url, {
    method: "DELETE",
    headers: { Accept: "application/json" },
  });

  if (!res.ok && res.status !== 404) {
    const text = await res.text();
    throw new Error(`Delete failed (${res.status}): ${text || res.statusText}`);
  }
}
// Backward-compatible export: DashboardPage.tsx still imports listRuns
export async function listRuns(): Promise<RunRegistryItem[]> {
  return fetchRunRegistry();
}

// Backward-compatible type alias: DashboardPage.tsx imports RunRecord
export type RunRecord = RunRegistryItem;
