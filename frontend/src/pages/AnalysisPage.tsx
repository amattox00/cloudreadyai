// src/pages/AnalysisPage.tsx

import React, { FormEvent, useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import {
  AnalysisSummary,
  AnalysisRecommendations,
  fetchAnalysisSummary,
  fetchAnalysisRecommendations,
  RecommendationItem,
} from "../api/analysis";
import {
  fetchRunRegistry,
  RunRegistryItem,
} from "../api/runRegistry";

const AnalysisPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialRunId = searchParams.get("runId") || "";

  const [runIdInput, setRunIdInput] = useState(initialRunId);
  const [summary, setSummary] = useState<AnalysisSummary | null>(null);
  const [recs, setRecs] = useState<AnalysisRecommendations | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // NEW: run registry list for the dropdown
  const [runOptions, setRunOptions] = useState<RunRegistryItem[]>([]);
  const [loadingRuns, setLoadingRuns] = useState(false);

  // Load run registry once on mount
  useEffect(() => {
    void (async () => {
      setLoadingRuns(true);
      try {
        const items = await fetchRunRegistry();
        // Optional: sort newest first if created_at exists
        const sorted = [...items].sort((a, b) => {
          if (a.created_at && b.created_at) {
            return a.created_at < b.created_at ? 1 : -1;
          }
          return 0;
        });
        setRunOptions(sorted);
      } catch (e) {
        // Don’t surface this as a blocking error – console log only
        console.error("Failed to load run registry", e);
      } finally {
        setLoadingRuns(false);
      }
    })();
  }, []);

  // Load when arriving with ?runId=...
  useEffect(() => {
    if (initialRunId) {
      void loadRun(initialRunId);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialRunId]);

  async function loadRun(runId: string) {
    if (!runId.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const [s, r] = await Promise.all([
        fetchAnalysisSummary(runId),
        fetchAnalysisRecommendations(runId),
      ]);
      setSummary(s);
      setRecs(r);
    } catch (e: any) {
      setSummary(null);
      setRecs(null);
      setError(e?.message || "Failed to load analysis.");
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const trimmed = runIdInput.trim();
    if (!trimmed) return;

    // Update URL
    setSearchParams({ runId: trimmed });
    void loadRun(trimmed);
  }

  // NEW: handle selection from run registry dropdown
  function handleRunSelect(e: React.ChangeEvent<HTMLSelectElement>) {
    const value = e.target.value;
    if (!value) return;
    setRunIdInput(value);
    setSearchParams({ runId: value });
    void loadRun(value);
  }

  // Derived aggregates from recommendations
  const strategyBreakdown = useMemo(() => {
    const counts: Record<string, number> = {};
    if (!recs?.items) return counts;
    for (const item of recs.items) {
      const key = item.strategy || "Unclassified";
      counts[key] = (counts[key] || 0) + 1;
    }
    return counts;
  }, [recs]);

  const waveBreakdown = useMemo(() => {
    const counts: Record<number, number> = {};
    if (!recs?.items) return counts;
    for (const item of recs.items) {
      counts[item.wave] = (counts[item.wave] || 0) + 1;
    }
    return counts;
  }, [recs]);

  const totalRecs = recs?.total_recommendations || 0;

  return (
    <div className="min-h-screen bg-slate-50">
      <main className="mx-auto max-w-6xl px-6 py-8">
        {/* Page header */}
        <div className="mb-6 flex items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold text-slate-900">
              Analysis
            </h1>
            <p className="mt-1 max-w-3xl text-sm text-slate-600">
              Phase C analysis prototype. Select a CloudReadyAI assessment run
              and review readiness, landing patterns, and risk signals. This
              view is now backed by live server data from your ingestion runs.
            </p>
          </div>

          <div className="rounded-xl border border-slate-200 bg-white px-4 py-3 text-xs text-slate-600 shadow-sm">
            <div className="mb-1 text-[11px] font-semibold uppercase tracking-wide text-slate-500">
              Phase C status
            </div>
            <ul className="space-y-1">
              <li>• UI and UX shell in place ✔</li>
              <li>• Using live analysis summary &amp; per-server recommendations ✔</li>
              <li>• Next: enrich workload-level views &amp; business readiness</li>
            </ul>
          </div>
        </div>

        {/* Run selection row */}
        <section className="mb-6 rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <div className="mb-3 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                Select assessment run
              </div>
              <p className="mt-1 text-xs text-slate-500">
                Paste any valid CloudReadyAI <code>run_id</code> from the Runs
                &amp; Ingestion workspace. This will call{" "}
                <code className="rounded bg-slate-100 px-1 py-0.5 text-[11px]">
                  /v1/analysis/&lt;run_id&gt;/summary
                </code>{" "}
                and{" "}
                <code className="rounded bg-slate-100 px-1 py-0.5 text-[11px]">
                  /v1/analysis/&lt;run_id&gt;/recommendations
                </code>
                .
              </p>
            </div>
            <Link
              to="/runs"
              className="text-xs font-medium text-sky-600 hover:text-sky-700"
            >
              Open Runs &amp; Ingestion →
            </Link>
          </div>

          {/* Input + Analyze button + NEW: run dropdown */}
          <form
            onSubmit={handleSubmit}
            className="flex flex-col gap-3 md:flex-row md:items-center"
          >
            <input
              type="text"
              value={runIdInput}
              onChange={(e) => setRunIdInput(e.target.value)}
              placeholder="e.g. run-25435416"
              className="flex-1 rounded-md border border-slate-300 px-3 py-2 text-sm shadow-sm focus:border-sky-500 focus:outline-none focus:ring-1 focus:ring-sky-500"
            />

            {/* NEW: run registry dropdown */}
            <select
              className="rounded-md border border-slate-300 bg-white px-2 py-2 text-xs shadow-sm focus:border-sky-500 focus:outline-none focus:ring-1 focus:ring-sky-500 md:w-64"
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
                <option key={run.run_id} value={run.run_id}>
                  {run.run_id}
                  {run.servers_ingested != null
                    ? ` • ${run.servers_ingested} servers`
                    : ""}
                  {run.environment
                    ? ` • env: ${run.environment}`
                    : ""}
                </option>
              ))}
            </select>

            <button
              type="submit"
              className="inline-flex items-center justify-center rounded-md bg-sky-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-sky-700 disabled:cursor-not-allowed disabled:bg-slate-300"
              disabled={loading || !runIdInput.trim()}
            >
              {loading ? "Analyzing…" : "Analyze run"}
            </button>
          </form>

          {summary && (
            <p className="mt-2 text-xs text-slate-500">
              Current run:{" "}
              <span className="rounded bg-slate-100 px-1.5 py-0.5 font-mono text-[11px]">
                {summary.run_id}
              </span>
            </p>
          )}
        </section>

        {/* Error state */}
        {error && (
          <div className="mb-4 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-700">
            {error}
          </div>
        )}

        {/* Empty state */}
        {!loading && !summary && !error && (
          <div className="mt-10 rounded-xl border border-dashed border-slate-200 bg-slate-50 px-6 py-8 text-center text-sm text-slate-500">
            Enter a <code>run_id</code> from the Runs workspace or pick from the
            dropdown above to see live analysis for that assessment.
          </div>
        )}

        {/* Main analysis content */}
        {summary && (
          <div className="space-y-6">
            {/* Top row: portfolio + waves + grade */}
            <div className="grid gap-4 md:grid-cols-3">
              {/* Workload / server portfolio snapshot */}
              <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
                <h2 className="text-sm font-semibold text-slate-800">
                  Workload portfolio snapshot
                </h2>
                <p className="mt-1 text-xs text-slate-500">
                  Server mix for this assessment, based on ingested inventory.
                </p>

                <dl className="mt-3 space-y-1 text-xs text-slate-700">
                  <div className="flex justify-between">
                    <dt>Total servers in scope</dt>
                    <dd className="font-semibold">{summary.total_servers}</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt>Legacy / EOL OS</dt>
                    <dd className="font-semibold">
                      {summary.legacy_server_count}
                    </dd>
                  </div>
                  <div className="flex justify-between">
                    <dt>Modern OS</dt>
                    <dd className="font-semibold">
                      {summary.modern_server_count}
                    </dd>
                  </div>
                </dl>

                <div className="mt-3">
                  <div className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">
                    By environment
                  </div>
                  <ul className="mt-1 space-y-0.5 text-xs text-slate-700">
                    {summary.environments.map((env) => (
                      <li
                        key={env.name}
                        className="flex justify-between rounded bg-slate-50 px-2 py-1"
                      >
                        <span>{env.name || "Unknown"}</span>
                        <span className="font-mono">{env.count}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Migration wave plan (derived from recs) */}
              <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
                <h2 className="text-sm font-semibold text-slate-800">
                  Migration wave plan (derived)
                </h2>
                <p className="mt-1 text-xs text-slate-500">
                  Simple wave grouping based on environment and risk.
                  This will evolve into a full workload wave designer.
                </p>

                <div className="mt-3 space-y-1 text-xs">
                  {Object.keys(waveBreakdown).length === 0 && (
                    <div className="rounded bg-slate-50 px-2 py-2 text-slate-500">
                      No recommendations yet for this run.
                    </div>
                  )}
                  {Object.entries(waveBreakdown)
                    .sort(([a], [b]) => Number(a) - Number(b))
                    .map(([wave, count]) => (
                      <div
                        key={wave}
                        className="flex items-center justify-between rounded bg-slate-50 px-2 py-1"
                      >
                        <span className="font-medium">
                          Wave {wave}
                        </span>
                        <span className="font-mono text-slate-800">
                          {count} servers
                        </span>
                      </div>
                    ))}
                </div>
              </div>

              {/* Readiness grade / summary */}
              <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
                <h2 className="text-sm font-semibold text-slate-800">
                  Readiness snapshot
                </h2>
                <p className="mt-1 text-xs text-slate-500">
                  Basic readiness banding derived from OS currency and
                  environment. This will be expanded to include more
                  business and technical signals.
                </p>

                <dl className="mt-3 space-y-1 text-xs text-slate-700">
                  <div className="flex justify-between">
                    <dt>Ready for rehost</dt>
                    <dd className="font-semibold">
                      {summary.readiness.ready_for_rehost}
                    </dd>
                  </div>
                  <div className="flex justify-between">
                    <dt>Needs modernization</dt>
                    <dd className="font-semibold">
                      {summary.readiness.needs_modernization}
                    </dd>
                  </div>
                  <div className="flex justify-between">
                    <dt>Needs investigation</dt>
                    <dd className="font-semibold">
                      {summary.readiness.needs_investigation}
                    </dd>
                  </div>
                </dl>

                {summary.notes.length > 0 && (
                  <div className="mt-3 text-xs text-slate-500">
                    <div className="mb-1 text-[11px] font-semibold uppercase tracking-wide text-slate-500">
                      Notes
                    </div>
                    <ul className="list-disc space-y-0.5 pl-4">
                      {summary.notes.map((note, idx) => (
                        <li key={idx}>{note}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>

            {/* Pattern recommendations + OS mix */}
            <div className="grid gap-4 md:grid-cols-3">
              {/* Pattern recommendations */}
              <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm md:col-span-2">
                <h2 className="text-sm font-semibold text-slate-800">
                  Pattern recommendations
                </h2>
                <p className="mt-1 text-xs text-slate-500">
                  Distribution of recommended landing patterns (rehost,
                  replatform, refactor, etc.) across this run&apos;s
                  servers.
                </p>

                {totalRecs === 0 && (
                  <div className="mt-3 rounded bg-slate-50 px-3 py-2 text-xs text-slate-500">
                    No recommendations available yet for this run.
                  </div>
                )}

                {totalRecs > 0 && (
                  <div className="mt-3 grid gap-2 sm:grid-cols-2">
                    {Object.entries(strategyBreakdown).map(
                      ([strategy, count]) => {
                        const pct = Math.round(
                          (count / totalRecs) * 100
                        );
                        return (
                          <div
                            key={strategy}
                            className="rounded border border-slate-200 bg-slate-50 px-3 py-2 text-xs"
                          >
                            <div className="flex justify-between">
                              <span className="font-medium">
                                {strategy}
                              </span>
                              <span className="font-mono">
                                {count} ({pct}%)
                              </span>
                            </div>
                            <div className="mt-1 h-1.5 rounded-full bg-slate-200">
                              <div
                                className="h-1.5 rounded-full bg-sky-500"
                                style={{ width: `${pct}%` }}
                              />
                            </div>
                          </div>
                        );
                      }
                    )}
                  </div>
                )}
              </div>

              {/* OS mix */}
              <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
                <h2 className="text-sm font-semibold text-slate-800">
                  OS mix
                </h2>
                <p className="mt-1 text-xs text-slate-500">
                  Families and legacy distribution detected in server
                  inventory.
                </p>

                <ul className="mt-3 space-y-1 text-xs text-slate-700">
                  {summary.os_summary.map((os) => (
                    <li
                      key={os.family}
                      className="flex items-center justify-between rounded bg-slate-50 px-2 py-1"
                    >
                      <span>{os.family}</span>
                      <span className="font-mono">
                        {os.count}{" "}
                        {os.legacy_count > 0 && (
                          <span className="ml-1 text-[11px] text-amber-700">
                            ({os.legacy_count} legacy)
                          </span>
                        )}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Detailed per-server recommendations table */}
            {recs && recs.items.length > 0 && (
              <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
                <div className="mb-2 flex items-center justify-between">
                  <h2 className="text-sm font-semibold text-slate-800">
                    Per-server recommendations
                  </h2>
                  <div className="text-xs text-slate-500">
                    {recs.total_recommendations} servers analyzed
                  </div>
                </div>

                <div className="max-h-80 overflow-auto rounded border border-slate-200">
                  <table className="min-w-full text-left text-xs">
                    <thead className="bg-slate-50 text-slate-600">
                      <tr>
                        <Th>Hostname</Th>
                        <Th>Environment</Th>
                        <Th>OS</Th>
                        <Th>Strategy</Th>
                        <Th>Risk</Th>
                        <Th>Wave</Th>
                        <Th>Summary</Th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {recs.items.map((item) => (
                        <ServerRow key={item.server_id} item={item} />
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>
            )}
          </div>
        )}
      </main>
    </div>
  );
};

const Th: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <th className="px-3 py-2 text-[11px] font-semibold uppercase tracking-wide">
    {children}
  </th>
);

const ServerRow: React.FC<{ item: RecommendationItem }> = ({ item }) => (
  <tr>
    <td className="px-3 py-2 font-mono text-[11px]">
      {item.hostname || "—"}
    </td>
    <td className="px-3 py-2 text-[11px]">
      {item.environment || "—"}
    </td>
    <td className="px-3 py-2 text-[11px]">{item.os || "—"}</td>
    <td className="px-3 py-2 text-[11px]">
      <span className="inline-flex rounded-full border border-slate-300 px-2 py-0.5 text-[10px] font-semibold uppercase">
        {item.strategy}
      </span>
    </td>
    <td className="px-3 py-2 text-[11px]">{item.risk_level}</td>
    <td className="px-3 py-2 text-[11px]">Wave {item.wave}</td>
    <td className="px-3 py-2 text-[11px] text-slate-600">
      {item.summary}
    </td>
  </tr>
);

export default AnalysisPage;
