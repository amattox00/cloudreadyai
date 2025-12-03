import React, { useState } from "react";

export default function AnalysisOverviewPage() {
  const [runId, setRunId] = useState("b2-api-test-001");

  return (
    <div className="space-y-6">
      {/* Header */}
      <section className="panel p-4">
        <h1 className="text-2xl font-semibold mb-1">Analysis Overview</h1>
        <p className="text-sm text-[var(--text-muted)]">
          Phase C is where CloudReadyAI stops being “just a report” and starts
          behaving like a decision engine. This page will surface normalized
          metrics and findings for a single assessment run.
        </p>
      </section>

      {/* Run selector */}
      <section className="panel p-4 space-y-3">
        <h2 className="text-lg font-semibold">Select Assessment Run</h2>
        <p className="text-xs text-[var(--text-muted)]">
          For now, this is a simple text input. Once the <code>/v1/runs</code>{" "}
          APIs are wired, this will be a dropdown of known runs.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 mt-1 max-w-xl">
          <input
            className="flex-1"
            value={runId}
            onChange={(e) => setRunId(e.target.value)}
            placeholder="e.g. b2-api-test-001"
          />
          <button
            type="button"
            className="btn-primary px-4 py-2"
            disabled={true}
            title="Backend integration coming in Phase C"
          >
            Load Analysis (coming soon)
          </button>
        </div>
        <p className="text-xs text-[var(--text-muted)]">
          In the next pass, this button will call{" "}
          <code>/v1/runs/&lt;id&gt;/summary</code>,{" "}
          <code>/v1/runs/&lt;id&gt;/analysis</code>, and{" "}
          <code>/v1/runs/&lt;id&gt;/problems</code>.
        </p>
      </section>

      {/* Key metrics + findings layout */}
      <section className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Key Metrics */}
        <div className="panel p-4 lg:col-span-2 space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">Key Metrics (Phase C)</h2>
            <span className="text-xs px-3 py-1 rounded-full bg-gray-200 text-gray-700 font-medium">
              Placeholder • UI Ready
            </span>
          </div>
          <p className="text-xs text-[var(--text-muted)]">
            This panel will summarize normalized inventory for the selected run:
            total servers, vCPU, RAM, storage, and network footprint, plus
            right-sizing signals.
          </p>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mt-3">
            <MetricCard label="Servers" value="—" />
            <MetricCard label="Total vCPU" value="—" />
            <MetricCard label="Total RAM (GB)" value="—" />
            <MetricCard label="Storage (TB)" value="—" />
            <MetricCard label="Underutilized Servers" value="—" />
            <MetricCard label="Rightsize Candidates" value="—" />
          </div>
        </div>

        {/* Data Quality */}
        <div className="panel p-4 space-y-2">
          <h2 className="text-lg font-semibold">Data Quality & Gaps</h2>
          <p className="text-xs text-[var(--text-muted)]">
            This is where we&apos;ll surface ingestion/data quality issues:
            missing tags, missing storage mappings, unknown OS versions, and
            anything that weakens confidence in recommendations.
          </p>
          <ul className="mt-2 text-sm list-disc list-inside text-gray-700 space-y-1">
            <li>UI shell is in place.</li>
            <li>
              Next pass will render actual items from{" "}
              <code>/v1/runs/&lt;id&gt;/problems</code>.
            </li>
          </ul>
        </div>
      </section>

      {/* Technical & Business Findings */}
      <section className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="panel p-4 space-y-2">
          <h2 className="text-lg font-semibold">Technical Findings</h2>
          <p className="text-xs text-[var(--text-muted)]">
            This panel is for concrete, technical insights: consolidation
            opportunities, EOL OS, patch lag, CPU/RAM imbalance, storage
            bottlenecks.
          </p>
          <p className="text-xs text-[var(--text-muted)]">
            When Phase C is wired, this will use{" "}
            <code>/v1/runs/&lt;id&gt;/analysis</code> to render structured
            bullet lists instead of placeholder text.
          </p>
        </div>

        <div className="panel p-4 space-y-2">
          <h2 className="text-lg font-semibold">Business Findings</h2>
          <p className="text-xs text-[var(--text-muted)]">
            This is where we translate technical signals into business language:
            migration waves, timelines, risk posture, and investment themes.
          </p>
          <p className="text-xs text-[var(--text-muted)]">
            All of this will be derived from the same Phase C engine, but
            formatted so that it can be pasted directly into slides and
            proposals.
          </p>
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
      <span className="text-[10px] uppercase tracking-wide text-gray-500 mb-1">
        {label}
      </span>
      <span className="text-xl font-semibold text-gray-900">{value}</span>
    </div>
  );
}
