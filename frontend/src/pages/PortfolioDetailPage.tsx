import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

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

export default function PortfolioDetailPage() {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const runId = id || "";

  const [runMeta, setRunMeta] = useState<RunRecord | null>(null);
  const [summary, setSummary] = useState<RunSummary | null>(null);

  const [loadingMeta, setLoadingMeta] = useState(false);
  const [loadingSummary, setLoadingSummary] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!runId) return;

    async function loadMeta() {
      try {
        setLoadingMeta(true);
        setError(null);

        const res = await fetch(`/v1/run_registry/${encodeURIComponent(runId)}`);
        const text = await res.text();
        let parsed: any = null;

        try {
          parsed = JSON.parse(text);
        } catch {
          throw new Error("Unable to parse run metadata response.");
        }

        if (!res.ok) {
          throw new Error(
            (parsed && parsed.detail) ||
              text ||
              `Failed to load run metadata (status ${res.status})`,
          );
        }

        setRunMeta(parsed as RunRecord);
      } catch (err: any) {
        console.error(err);
        setError(err?.message || "Failed to load portfolio run metadata.");
      } finally {
        setLoadingMeta(false);
      }
    }

    async function loadSummary() {
      try {
        setLoadingSummary(true);

        const res = await fetch(
          `/v1/run_registry/${encodeURIComponent(runId)}/summary`,
        );
        const text = await res.text();
        let parsed: any = null;

        try {
          parsed = JSON.parse(text);
        } catch {
          // If parsing fails, it's probably a simple placeholder.
          parsed = null;
        }

        if (!res.ok) {
          console.warn("Summary fetch failed:", text);
          return;
        }

        if (parsed) {
          setSummary(parsed as RunSummary);
        }
      } catch (err) {
        console.warn("Error loading summary:", err);
      } finally {
        setLoadingSummary(false);
      }
    }

    void loadMeta();
    void loadSummary();
  }, [runId]);

  if (!runId) {
    return (
      <div className="p-8">
        <div className="bg-white border border-gray-300 rounded-xl shadow-md px-6 py-8 text-center text-gray-700">
          <p className="font-semibold">No run selected.</p>
          <p className="text-sm mt-2">
            This page is meant to show the portfolio view of a specific
            assessment run.
          </p>
          <button
            type="button"
            onClick={() => navigate("/portfolio")}
            className="mt-4 inline-block px-4 py-2 bg-[var(--brand-accent)] text-white rounded-md font-semibold hover:opacity-90"
          >
            Back to Portfolio
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 space-y-8">
      {/* Header with navigation */}
      <header className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <button
            type="button"
            onClick={() => navigate("/portfolio")}
            className="text-xs text-gray-600 mb-2 hover:underline"
          >
            ← Back to Portfolio
          </button>
          <h1 className="text-3xl font-bold">
            Portfolio –{" "}
            {runMeta?.name ? runMeta.name : `Assessment ${runId}`}
          </h1>
          <p className="text-gray-700 mt-2 text-sm">
            A run-centric portfolio view: applications, servers, storage, and
            network insights anchored to one CloudReadyAI assessment.
          </p>
        </div>

        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() =>
              navigate(`/runs?runId=${encodeURIComponent(runId)}`)
            }
            className="px-4 py-2 border border-gray-400 bg-white rounded-md text-sm text-gray-800"
          >
            Open Ingestion Workspace
          </button>
          <button
            type="button"
            onClick={() =>
              navigate(`/analysis?runId=${encodeURIComponent(runId)}`)
            }
            className="px-4 py-2 bg-[var(--brand-accent)] text-white rounded-md text-sm font-semibold hover:opacity-90"
          >
            Open Analysis View
          </button>
        </div>
      </header>

      {/* Error state */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-md text-sm">
          {error}
        </div>
      )}

      {/* Metadata + summary row */}
      <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Run metadata */}
        <div className="bg-white border border-gray-300 rounded-xl shadow-md p-6 lg:col-span-2">
          <h2 className="text-xl font-semibold mb-3">Run Details</h2>

          {loadingMeta && !runMeta && (
            <p className="text-sm text-gray-600">Loading run metadata…</p>
          )}

          {runMeta && (
            <dl className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-2 text-sm text-gray-800">
              <div>
                <dt className="font-semibold">Run ID</dt>
                <dd className="mt-1 text-xs">
                  <code>{runMeta.id}</code>
                </dd>
              </div>
              <div>
                <dt className="font-semibold">Created At</dt>
                <dd className="mt-1">{runMeta.created_at || "—"}</dd>
              </div>
              <div>
                <dt className="font-semibold">Source</dt>
                <dd className="mt-1">{runMeta.source || "—"}</dd>
              </div>
              <div>
                <dt className="font-semibold">State</dt>
                <dd className="mt-1">{runMeta.state || "created"}</dd>
              </div>
              <div>
                <dt className="font-semibold">Servers Ingested</dt>
                <dd className="mt-1">
                  {runMeta.servers_ingested ?? 0}
                </dd>
              </div>
              <div>
                <dt className="font-semibold">Storage Objects</dt>
                <dd className="mt-1">
                  {runMeta.storage_ingested ?? 0}
                </dd>
              </div>
              <div>
                <dt className="font-semibold">Network Entries</dt>
                <dd className="mt-1">
                  {runMeta.network_ingested ?? 0}
                </dd>
              </div>
            </dl>
          )}

          {!loadingMeta && !runMeta && !error && (
            <p className="text-sm text-gray-600">
              No metadata available for this run yet.
            </p>
          )}
        </div>

        {/* Summary metrics */}
        <div className="bg-white border border-gray-300 rounded-xl shadow-md p-6">
          <h2 className="text-xl font-semibold mb-3">Run Summary (Phase C)</h2>

          {loadingSummary && !summary && (
            <p className="text-sm text-gray-600">Loading summary…</p>
          )}

          {summary && (
            <div className="space-y-2 text-sm text-gray-800">
              <div className="flex justify-between">
                <span>Underutilized servers</span>
                <span className="font-semibold">
                  {summary.underutilized_servers}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Overprovisioned RAM</span>
                <span className="font-semibold">
                  {summary.overprovisioned_ram_pct.toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between">
                <span>Hot network segments</span>
                <span className="font-semibold">
                  {summary.hot_network_segments}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Rightsizing candidates</span>
                <span className="font-semibold">
                  {summary.rightsizing_candidates}
                </span>
              </div>
              {summary.notes && (
                <p className="mt-2 text-xs text-gray-600">
                  {summary.notes}
                </p>
              )}
            </div>
          )}

          {!loadingSummary && !summary && (
            <p className="text-xs text-gray-500">
              No summary has been generated yet. Today this is driven by the
              placeholder <code>/v1/run_registry/{{run_id}}/summary</code>{" "}
              endpoint and will later connect to the full analysis engine.
            </p>
          )}
        </div>
      </section>

      {/* Portfolio sections – placeholders for Phase B3 expansion */}
      <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white border border-gray-300 rounded-xl shadow-md p-6">
          <h2 className="text-lg font-semibold mb-2">Application Portfolio</h2>
          <p className="text-sm text-gray-700">
            In Phase B3, this panel will show applications, tiers, and business
            groupings inferred from the ingested server and storage data (e.g.,
            &quot;Three-tier web app&quot;, &quot;Batch processing cluster&quot;,
            &quot;database consolidation group&quot;).
          </p>
          <p className="mt-2 text-xs text-gray-500">
            Today this is a structured placeholder to keep the UX ready for
            normalized workload views.
          </p>
        </div>

        <div className="bg-white border border-gray-300 rounded-xl shadow-md p-6">
          <h2 className="text-lg font-semibold mb-2">Server Fleet View</h2>
          <p className="text-sm text-gray-700">
            This panel will aggregate server characteristics — OS, environment,
            vCPU/RAM, tags — and highlight consolidation or rightsizing
            opportunities per workload.
          </p>
          <p className="mt-2 text-xs text-gray-500">
            Future work: connect this to the Phase C metrics engine and display
            counts per application or migration wave.
          </p>
        </div>

        <div className="bg-white border border-gray-300 rounded-xl shadow-md p-6">
          <h2 className="text-lg font-semibold mb-2">Storage Layout</h2>
          <p className="text-sm text-gray-700">
            In later phases this will show storage tiers, RAID groups, and
            volume mappings for the run, aligned with performance and data
            protection requirements.
          </p>
          <p className="mt-2 text-xs text-gray-500">
            For now it serves as a design anchor for where storage insights
            should live in the portfolio.
          </p>
        </div>

        <div className="bg-white border border-gray-300 rounded-xl shadow-md p-6">
          <h2 className="text-lg font-semibold mb-2">Network Topology</h2>
          <p className="text-sm text-gray-700">
            This panel will surface VLANs, subnets, and hot network segments,
            and tie directly into the diagram engine and zero trust overlays.
          </p>
          <p className="mt-2 text-xs text-gray-500">
            Future work: bridge the outputs from network ingestion and the
            Phase 7B/7E diagram pipeline into this summary.
          </p>
        </div>
      </section>
    </div>
  );
}
