import React, { useState } from "react";
import { useParams } from "react-router-dom";

type RunSummary = any;
type RunProblems = any;
type RunAnalysis = any;

const DEFAULT_RUN_BY_PORTFOLIO: Record<string, string> = {
  "usda-assess-fy25": "b2-api-test-001",
  "cbp-cspd": "b3-network-test-001",
};

export default function PortfolioRunOverviewPage() {
  const { portfolioId } = useParams<{ portfolioId: string }>();

  const [runIdInput, setRunIdInput] = useState(
    (portfolioId && DEFAULT_RUN_BY_PORTFOLIO[portfolioId]) || ""
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [summary, setSummary] = useState<RunSummary | null>(null);
  const [problems, setProblems] = useState<RunProblems | null>(null);
  const [analysis, setAnalysis] = useState<RunAnalysis | null>(null);

  const niceName =
    portfolioId === "usda-assess-fy25"
      ? "USDA Assess FY25"
      : portfolioId === "cbp-cspd"
      ? "DHS CBP CSPD"
      : portfolioId || "Unknown";

  async function handleLoadRun() {
    if (!runIdInput.trim()) {
      setError("Please enter a run ID.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const encoded = encodeURIComponent(runIdInput.trim());
      const base = `/v1/runs/${encoded}`;

      const [summaryRes, problemsRes, analysisRes] = await Promise.all([
        fetch(`${base}/summary`),
        fetch(`${base}/problems`),
        fetch(`${base}/analysis`),
      ]);

      if (!summaryRes.ok) {
        throw new Error(
          `Summary error ${summaryRes.status}: ${await summaryRes.text()}`
        );
      }

      // Problems + analysis can fail independently without killing the page
      let problemsJson: any = null;
      let analysisJson: any = null;

      if (problemsRes.ok) {
        problemsJson = await problemsRes.json();
      }

      if (analysisRes.ok) {
        analysisJson = await analysisRes.json();
      }

      const summaryJson = await summaryRes.json();

      setSummary(summaryJson);
      setProblems(problemsJson);
      setAnalysis(analysisJson);
    } catch (e: any) {
      console.error("Error loading run:", e);
      setError(
        e?.message ||
          "Failed to load run data. Check the API logs on the backend."
      );
      setSummary(null);
      setProblems(null);
      setAnalysis(null);
    } finally {
      setLoading(false);
    }
  }

  function metricValue(path: string, fallback = 0): string {
    // Very defensive: safely walk into nested properties using "a.b.c" syntax.
    try {
      const parts = path.split(".");
      let value: any = summary;
      for (const p of parts) {
        if (!value || typeof value !== "object") return String(fallback);
        value = value[p];
      }
      if (value == null || value === "") return String(fallback);
      if (typeof value === "number") return value.toLocaleString();
      return String(value);
    } catch {
      return String(fallback);
    }
  }

  const totalServers = metricValue("totals.servers", 0);
  const totalVcpu = metricValue("totals.vcpu", 0);
  const totalRamGb = metricValue("totals.ram_gb", 0);
  const totalStorageGb = metricValue("totals.storage_gb", 0);
  const totalNetworkDevices = metricValue("totals.network_devices", 0);

  const topRisks: string[] =
    (analysis &&
      (analysis.top_risks ||
        analysis.topRisks ||
        analysis.risks ||
        [])) ||
    [];

  const problemSignals: string[] =
    (problems &&
      (problems.signals ||
        problems.problem_signals ||
        problems.items ||
        [])) ||
    [];

  return (
    <div className="space-y-8">
      {/* Header */}
      <header className="space-y-1">
        <h1 className="text-3xl font-semibold">Portfolio Overview</h1>
        <p className="text-sm text-gray-700">
          Selected portfolio: <span className="font-semibold">{niceName}</span>
        </p>
        <p className="text-sm text-gray-600">
          This page surfaces Phase B (normalized ingestion data) and Phase C
          (initial analysis) for a single assessment run.
        </p>
      </header>

      {/* Run selector */}
      <section className="panel p-6 space-y-4">
        <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
          <div className="flex-1 space-y-2">
            <h2 className="text-lg font-semibold">Select Assessment Run</h2>
            <p className="text-sm text-gray-600">
              Enter the CloudReadyAI run ID backed by <code>/v1/runs</code>{" "}
              (for example: <code>b2-api-test-001</code> or{" "}
              <code>b3-network-test-001</code>).
            </p>
            <div className="flex flex-col sm:flex-row gap-3 mt-2">
              <input
                type="text"
                value={runIdInput}
                onChange={(e) => setRunIdInput(e.target.value)}
                placeholder="e.g. b2-api-test-001"
                className="flex-1"
              />
              <button
                type="button"
                className="btn-primary px-5 py-2"
                onClick={handleLoadRun}
                disabled={loading}
              >
                {loading ? "Loading..." : "Load Run"}
              </button>
            </div>
          </div>
        </div>

        {error && (
          <div className="mt-4 text-sm text-red-700 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
            {error}
          </div>
        )}
      </section>

      {/* Two-column layout: Key Metrics + Risks/Problems */}
      <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Key Metrics */}
        <div className="panel p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">Key Metrics</h2>
            <span className="text-xs px-3 py-1 rounded-full bg-gray-200 text-gray-700 font-medium">
              Phase B • Normalized Data
            </span>
          </div>
          <p className="text-sm text-gray-600">
            High-level footprint for the selected run, combining normalized
            server, storage, and network data.
          </p>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mt-4">
            <MetricCard label="Servers" value={totalServers} />
            <MetricCard label="Total vCPU" value={totalVcpu} />
            <MetricCard label="Total RAM (GB)" value={totalRamGb} />
            <MetricCard label="Total Storage (GB)" value={totalStorageGb} />
            <MetricCard
              label="Network Devices"
              value={totalNetworkDevices}
            />
          </div>

          {!summary && (
            <p className="mt-4 text-xs text-gray-500">
              Metrics will populate once a valid run ID is loaded.
            </p>
          )}
        </div>

        {/* Risks & Problem Signals */}
        <div className="panel p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">Risks & Problem Signals</h2>
            <span className="text-xs px-3 py-1 rounded-full bg-gray-200 text-gray-700 font-medium">
              Phase C • Heuristics
            </span>
          </div>
          <p className="text-sm text-gray-600">
            Quick scan of ingestion quality and technical risks based on
            normalized data. Uses the same engine behind{" "}
            <code>/v1/runs/&lt;id&gt;/analysis</code> and{" "}
            <code>/v1/runs/&lt;id&gt;/problems</code>.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
            <div className="space-y-2">
              <h3 className="text-sm font-semibold text-gray-800">
                Top Risks
              </h3>
              {topRisks && topRisks.length > 0 ? (
                <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                  {topRisks.map((r, idx) => (
                    <li key={idx}>{String(r)}</li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-gray-500">
                  No explicit risks flagged yet.
                </p>
              )}
            </div>

            <div className="space-y-2">
              <h3 className="text-sm font-semibold text-gray-800">
                Problem Signals
              </h3>
              {problemSignals && problemSignals.length > 0 ? (
                <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                  {problemSignals.map((p, idx) => (
                    <li key={idx}>{String(p)}</li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-gray-500">
                  No problem signals returned by the heuristics engine.
                </p>
              )}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

type MetricCardProps = {
  label: string;
  value: string | number;
};

function MetricCard({ label, value }: MetricCardProps) {
  return (
    <div className="border rounded-xl bg-white/70 px-4 py-3 flex flex-col">
      <span className="text-xs uppercase tracking-wide text-gray-500 mb-1">
        {label}
      </span>
      <span className="text-xl font-semibold text-gray-900">{value}</span>
    </div>
  );
}
