import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

type RunSummary = {
  underutilized_servers: number;
  overprovisioned_ram_pct: number;
  hot_network_segments: number;
  rightsizing_candidates: number;
  notes?: string;
};

type RunRecord = {
  id: string;
  name: string;
  created_at?: string;
  source?: string;
  state?: string;
  servers_ingested?: number;
  storage_ingested?: number;
  network_ingested?: number;
  summary?: RunSummary;
};

export default function PortfolioPage() {
  const navigate = useNavigate();

  const [runs, setRuns] = useState<RunRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  useEffect(() => {
    async function loadRuns() {
      try {
        setLoading(true);
        setError(null);
        setDeleteError(null);

        const res = await fetch("/v1/run_registry");
        const text = await res.text();
        let parsed: any = [];

        try {
          parsed = JSON.parse(text);
        } catch {
          throw new Error("Unable to parse /v1/run_registry response");
        }

        if (!res.ok) {
          throw new Error(
            (parsed && parsed.detail) ||
              text ||
              `Failed to load runs (status ${res.status})`,
          );
        }

        const list: RunRecord[] = Array.isArray(parsed) ? parsed : [];
        setRuns(list);
      } catch (err: any) {
        console.error(err);
        setError(err?.message || "Failed to load portfolio runs.");
      } finally {
        setLoading(false);
      }
    }

    void loadRuns();
  }, []);

  const totalRuns = runs.length;
  const mostRecent = runs[0];

  async function handleDelete(runId: string) {
    const target = runs.find((r) => r.id === runId);
    const label = target?.name || runId;

    const confirmed = window.confirm(
      `Delete assessment "${label}"?\n\nThis will remove it from the run registry used by Dashboard, Runs, and Portfolio. It will not delete any source CSV files.`,
    );
    if (!confirmed) return;

    try {
      setDeleteError(null);
      setDeletingId(runId);

      const res = await fetch(`/v1/run_registry/${encodeURIComponent(runId)}`, {
        method: "DELETE",
      });

      const text = await res.text();
      let parsed: any = null;
      try {
        parsed = JSON.parse(text);
      } catch {
        // non-JSON is fine
      }

      if (!res.ok) {
        throw new Error(
          (parsed && parsed.detail) ||
            text ||
            `Failed to delete run (status ${res.status})`,
        );
      }

      // Optimistically remove from list
      setRuns((prev) => prev.filter((r) => r.id !== runId));
    } catch (err: any) {
      console.error(err);
      setDeleteError(err?.message || "Failed to delete run.");
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <header className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Portfolio Overview</h1>
          <p className="text-gray-700 mt-2">
            Each assessment run forms the backbone of your application and
            infrastructure portfolio. Use this view to jump into a specific
            run&apos;s portfolio, analysis, and cost planning.
          </p>
        </div>

        <div className="bg-white border border-gray-300 rounded-xl shadow-md px-4 py-3 text-sm text-gray-800 min-w-[220px]">
          <div className="font-semibold mb-1">Portfolio Snapshot</div>
          <div className="flex items-center justify-between">
            <span>Total assessments</span>
            <span className="font-bold">{totalRuns}</span>
          </div>
          {mostRecent && (
            <div className="mt-2 text-xs text-gray-600">
              <div className="font-semibold">Most recent:</div>
              <div className="truncate">{mostRecent.name}</div>
              {mostRecent.created_at && (
                <div>Started: {mostRecent.created_at}</div>
              )}
            </div>
          )}
        </div>
      </header>

      {/* Error state */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-md text-sm">
          {error}
        </div>
      )}

      {deleteError && (
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-md text-xs">
          {deleteError}
        </div>
      )}

      {/* Empty state */}
      {!error && !loading && runs.length === 0 && (
        <div className="bg-white border border-gray-300 rounded-xl shadow-md px-6 py-8 text-center text-gray-700">
          <p className="font-semibold">No assessments yet.</p>
          <p className="text-sm mt-2">
            Start from the Dashboard by creating a new assessment. Once runs
            exist, they&apos;ll appear here as portfolio entries.
          </p>
          <button
            type="button"
            onClick={() => navigate("/dashboard")}
            className="mt-4 inline-block px-4 py-2 bg-[var(--brand-accent)] text-white rounded-md font-semibold hover:opacity-90"
          >
            Go to Dashboard
          </button>
        </div>
      )}

      {/* Runs table */}
      {runs.length > 0 && (
        <section className="bg-white border border-gray-300 rounded-xl shadow-md p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">Assessment Portfolio</h2>
            <p className="text-xs text-gray-500">
              Backed by <code>/v1/run_registry</code>. Each row represents one
              CloudReadyAI assessment run.
            </p>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="border-b bg-gray-50 text-left">
                  <th className="px-3 py-2 font-semibold">Name</th>
                  <th className="px-3 py-2 font-semibold">Run ID</th>
                  <th className="px-3 py-2 font-semibold">Created</th>
                  <th className="px-3 py-2 font-semibold">Source</th>
                  <th className="px-3 py-2 font-semibold">State</th>
                  <th className="px-3 py-2 font-semibold text-right">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody>
                {runs.map((run) => (
                  <tr
                    key={run.id}
                    className="border-b last:border-b-0 hover:bg-gray-50"
                  >
                    <td className="px-3 py-2 align-top">
                      <div className="font-semibold text-gray-900">
                        {run.name || run.id}
                      </div>
                    </td>
                    <td className="px-3 py-2 align-top text-xs text-gray-700">
                      <code>{run.id}</code>
                    </td>
                    <td className="px-3 py-2 align-top text-xs text-gray-700">
                      {run.created_at || "—"}
                    </td>
                    <td className="px-3 py-2 align-top text-xs text-gray-700">
                      {run.source || "—"}
                    </td>
                    <td className="px-3 py-2 align-top text-xs text-gray-700">
                      {run.state || "created"}
                    </td>
                    <td className="px-3 py-2 align-top text-right">
                      <div className="flex flex-wrap justify-end gap-2">
                        <button
                          type="button"
                          onClick={() => navigate(`/portfolio/${run.id}`)}
                          className="px-3 py-1 border border-gray-300 rounded-md text-xs text-gray-800 bg-white hover:bg-gray-100"
                        >
                          Open Portfolio
                        </button>
                        <button
                          type="button"
                          onClick={() =>
                            navigate(
                              `/analysis?runId=${encodeURIComponent(run.id)}`,
                            )
                          }
                          className="px-3 py-1 border border-gray-300 rounded-md text-xs text-gray-800 bg-white hover:bg-gray-100"
                        >
                          Open Analysis
                        </button>
                        <button
                          type="button"
                          onClick={() =>
                            navigate(`/runs?runId=${encodeURIComponent(run.id)}`)
                          }
                          className="px-3 py-1 bg-[var(--brand-accent)] text-white rounded-md text-xs font-semibold hover:opacity-90"
                        >
                          Ingestion Workspace
                        </button>
                        <button
                          type="button"
                          onClick={() => void handleDelete(run.id)}
                          disabled={deletingId === run.id}
                          className="px-3 py-1 border border-red-400 rounded-md text-xs text-red-700 bg-white hover:bg-red-50 disabled:opacity-60"
                        >
                          {deletingId === run.id ? "Deleting…" : "Delete"}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* Helper note */}
      <p className="text-xs text-gray-500">
        Future Phase B3 work: wire portfolio rows to normalized workload views
        (apps, tiers, dependencies) and feed Phase C/D analytics and TCO.
      </p>
    </div>
  );
}
