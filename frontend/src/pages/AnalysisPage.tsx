// src/pages/AnalysisPage.tsx
import React, { FormEvent, useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

import { fetchRunRegistry, RunRegistryItem } from "../api/runRegistry";
import {
  fetchAnalysisRunV1Overview,
  fetchAnalysisRunV1Segmentation,
  AnalysisRunV1Overview,
  AnalysisRunV1Segmentation,
} from "../api/analysisRunV1";

function Badge({
  children,
  tone = "neutral",
}: {
  children: React.ReactNode;
  tone?: "neutral" | "good" | "warn" | "bad";
}) {
  const cls =
    tone === "good"
      ? "border-emerald-200 bg-emerald-50 text-emerald-800"
      : tone === "warn"
      ? "border-amber-200 bg-amber-50 text-amber-800"
      : tone === "bad"
      ? "border-red-200 bg-red-50 text-red-800"
      : "border-slate-200 bg-slate-50 text-slate-700";

  return (
    <span
      className={`inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide ${cls}`}
    >
      {children}
    </span>
  );
}

function MetricRow({
  label,
  value,
}: {
  label: string;
  value: React.ReactNode;
}) {
  return (
    <div className="flex items-center justify-between rounded bg-slate-50 px-3 py-2 text-xs">
      <span className="text-slate-600">{label}</span>
      <span className="font-mono text-slate-900">{value}</span>
    </div>
  );
}

const AnalysisPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialRunId = searchParams.get("runId") || "";

  const [runIdInput, setRunIdInput] = useState(initialRunId);

  const [overview, setOverview] = useState<AnalysisRunV1Overview | null>(null);
  const [segmentation, setSegmentation] = useState<AnalysisRunV1Segmentation | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Run registry dropdown
  const [runOptions, setRunOptions] = useState<RunRegistryItem[]>([]);
  const [loadingRuns, setLoadingRuns] = useState(false);

  useEffect(() => {
    void (async () => {
      setLoadingRuns(true);
      try {
        const items = await fetchRunRegistry();
        const sorted = [...items].sort((a, b) => {
          const ac = a.created_at || "";
          const bc = b.created_at || "";
          return ac < bc ? 1 : -1;
        });
        setRunOptions(sorted);
      } catch (e) {
        console.error("Failed to load run registry", e);
      } finally {
        setLoadingRuns(false);
      }
    })();
  }, []);

  useEffect(() => {
    if (initialRunId) {
      void loadRun(initialRunId);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialRunId]);

  async function loadRun(runId: string) {
    const id = (runId || "").trim();
    if (!id) return;

    setLoading(true);
    setError(null);

    try {
      const [o, s] = await Promise.all([
        fetchAnalysisRunV1Overview(id),
        fetchAnalysisRunV1Segmentation(id),
      ]);
      setOverview(o);
      setSegmentation(s);
    } catch (e: any) {
      setOverview(null);
      setSegmentation(null);
      setError(e?.message || "Failed to load analysis.");
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const trimmed = runIdInput.trim();
    if (!trimmed) return;
    setSearchParams({ runId: trimmed });
    void loadRun(trimmed);
  }

  function handleRunSelect(e: React.ChangeEvent<HTMLSelectElement>) {
    const value = e.target.value;
    if (!value) return;
    setRunIdInput(value);
    setSearchParams({ runId: value });
    void loadRun(value);
  }

  const readiness = overview?.readiness;
  const readinessTone = useMemo(() => {
    if (!readiness) return "neutral" as const;
    return readiness.ready_for_analysis ? ("good" as const) : ("warn" as const);
  }, [readiness]);

  const counts = overview?.counts;

  return (
    <div className="min-h-screen bg-slate-50">
      <main className="mx-auto max-w-6xl px-6 py-8">
        {/* Header */}
        <div className="mb-6 flex items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold text-slate-900">Analysis</h1>
            <p className="mt-1 max-w-3xl text-sm text-slate-600">
              Phase C Analysis (v1). This is intentionally demo-safe and reads from the
              same in-memory run registry the UI uses today. Next step: compute real segmentation
              from V2 ingested inventory rows.
            </p>
          </div>

          <div className="rounded-xl border border-slate-200 bg-white px-4 py-3 text-xs text-slate-600 shadow-sm">
            <div className="mb-1 text-[11px] font-semibold uppercase tracking-wide text-slate-500">
              Current mode
            </div>
            <ul className="space-y-1">
              <li>
                • Endpoints: <span className="font-mono">/v1/analysis/run/&lt;id&gt;/…</span>
              </li>
              <li>• No DB dependency ✔</li>
              <li>• Stable for demo flow ✔</li>
            </ul>
          </div>
        </div>

        {/* Run selection */}
        <section className="mb-6 rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <div className="mb-3 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                Select assessment run
              </div>
              <p className="mt-1 text-xs text-slate-500">
                Use a run <code>id</code> from the Runs workspace. This page loads:
                <span className="ml-1 font-mono">overview</span> and{" "}
                <span className="font-mono">segmentation</span>.
              </p>
            </div>

            <Link to="/runs" className="text-xs font-medium text-sky-600 hover:text-sky-700">
              Open Runs &amp; Ingestion →
            </Link>
          </div>

          <form onSubmit={handleSubmit} className="flex flex-col gap-3 md:flex-row md:items-center">
            <input
              type="text"
              value={runIdInput}
              onChange={(e) => setRunIdInput(e.target.value)}
              placeholder="e.g. run-09405838"
              className="flex-1 rounded-md border border-slate-300 px-3 py-2 text-sm shadow-sm focus:border-sky-500 focus:outline-none focus:ring-1 focus:ring-sky-500"
            />

            <select
              className="rounded-md border border-slate-300 bg-white px-2 py-2 text-xs shadow-sm focus:border-sky-500 focus:outline-none focus:ring-1 focus:ring-sky-500 md:w-72"
              value=""
              onChange={handleRunSelect}
              disabled={loadingRuns || runOptions.length === 0}
            >
              <option value="">
                {loadingRuns
                  ? "Loading runs…"
                  : runOptions.length === 0
                  ? "No recent runs found"
                  : "Or pick a recent run…"}
              </option>

              {runOptions.map((run) => (
                <option key={run.id} value={run.id}>
                  {run.id}
                  {typeof run.servers_ingested === "number" ? ` • ${run.servers_ingested} servers` : ""}
                </option>
              ))}
            </select>

            <button
              type="submit"
              className="inline-flex items-center justify-center rounded-md bg-sky-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-sky-700 disabled:cursor-not-allowed disabled:bg-slate-300"
              disabled={loading || !runIdInput.trim()}
            >
              {loading ? "Loading…" : "Load analysis"}
            </button>
          </form>

          {overview?.run?.id && (
            <p className="mt-2 text-xs text-slate-500">
              Current run:{" "}
              <span className="rounded bg-slate-100 px-1.5 py-0.5 font-mono text-[11px]">
                {overview.run.id}
              </span>
            </p>
          )}
        </section>

        {/* Error */}
        {error && (
          <div className="mb-4 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-700">
            {error}
          </div>
        )}

        {/* Empty state */}
        {!loading && !overview && !error && (
          <div className="mt-10 rounded-xl border border-dashed border-slate-200 bg-slate-50 px-6 py-8 text-center text-sm text-slate-500">
            Pick a run above to see Analysis v1 readiness and slice counts.
          </div>
        )}

        {/* Main content */}
        {overview && (
          <div className="space-y-6">
            {/* Readiness + Run meta */}
            <div className="grid gap-4 md:grid-cols-3">
              <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm md:col-span-2">
                <div className="flex items-center justify-between">
                  <h2 className="text-sm font-semibold text-slate-800">Readiness gate</h2>
                  <Badge tone={readinessTone}>
                    {readiness?.ready_for_analysis ? "Passed" : "Not ready"}
                  </Badge>
                </div>

                <p className="mt-1 text-xs text-slate-500">
                  For v1: “Ready” means you have servers + at least one other slice.
                </p>

                <div className="mt-3 grid gap-2 sm:grid-cols-3">
                  <MetricRow label="Has servers" value={readiness?.has_servers ? "Yes" : "No"} />
                  <MetricRow label="Has other slice" value={readiness?.has_other_slice ? "Yes" : "No"} />
                  <MetricRow
                    label="Ready for analysis"
                    value={readiness?.ready_for_analysis ? "Yes" : "No"}
                  />
                </div>

                {overview.findings?.length > 0 && (
                  <div className="mt-4">
                    <div className="mb-1 text-[11px] font-semibold uppercase tracking-wide text-slate-500">
                      Findings
                    </div>
                    <ul className="list-disc space-y-1 pl-5 text-xs text-slate-700">
                      {overview.findings.map((f, idx) => (
                        <li key={idx}>{f}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
                <h2 className="text-sm font-semibold text-slate-800">Run details</h2>
                <div className="mt-3 space-y-2 text-xs">
                  <div className="flex justify-between">
                    <span className="text-slate-500">Name</span>
                    <span className="font-medium text-slate-800">{overview.run.name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Source</span>
                    <span className="font-medium text-slate-800">{overview.run.source}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">State</span>
                    <span className="font-medium text-slate-800">{overview.run.state}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Created</span>
                    <span className="font-mono text-[11px] text-slate-800">
                      {overview.run.created_at}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Slice counts */}
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-semibold text-slate-800">Ingestion coverage</h2>
                <Badge tone={counts && counts.servers > 0 ? "good" : "warn"}>
                  {counts?.servers ? "Servers present" : "No servers yet"}
                </Badge>
              </div>

              <p className="mt-1 text-xs text-slate-500">
                These counters come from the in-memory run registry (demo-safe). Next we’ll back them
                with V2 inventory rollups.
              </p>

              <div className="mt-3 grid gap-2 sm:grid-cols-3">
                <MetricRow label="Servers" value={counts?.servers ?? 0} />
                <MetricRow label="Storage" value={counts?.storage ?? 0} />
                <MetricRow label="Databases" value={counts?.databases ?? 0} />
                <MetricRow label="Applications" value={counts?.applications ?? 0} />
                <MetricRow label="Dependencies" value={counts?.dependencies ?? 0} />
                <MetricRow label="Network" value={counts?.network ?? 0} />
              </div>
            </div>

            {/* Segmentation placeholder */}
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-semibold text-slate-800">Server segmentation</h2>
                <Badge tone="neutral">v1 placeholder</Badge>
              </div>

              <p className="mt-1 text-xs text-slate-500">
                Currently returns an empty segmentation shape (stable for UI wiring). Next: compute
                real OS / env / sizing buckets from <code>/v1/ingest/results</code>.
              </p>

              <div className="mt-3 grid gap-2 sm:grid-cols-2">
                <MetricRow label="Total servers (from segmentation)" value={segmentation?.totals?.servers ?? 0} />
                <MetricRow label="Note" value={segmentation?.note ?? "—"} />
              </div>

              <div className="mt-3 rounded border border-slate-200 bg-slate-50 p-3 text-xs text-slate-700">
                <div className="mb-2 text-[11px] font-semibold uppercase tracking-wide text-slate-500">
                  Segments (currently empty)
                </div>
                <ul className="space-y-1 font-mono text-[11px]">
                  <li>os_family: {JSON.stringify(segmentation?.segments?.os_family ?? [])}</li>
                  <li>environment: {JSON.stringify(segmentation?.segments?.environment ?? [])}</li>
                  <li>cpu_cores_bucket: {JSON.stringify(segmentation?.segments?.cpu_cores_bucket ?? [])}</li>
                  <li>ram_gb_bucket: {JSON.stringify(segmentation?.segments?.ram_gb_bucket ?? [])}</li>
                </ul>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default AnalysisPage;
